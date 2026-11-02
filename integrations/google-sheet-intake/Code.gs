/**
 * 10flat Law: case requests from the website's case form (/start and /es/start).
 *
 * Paste this into Extensions > Apps Script of the Google Sheet that should hold the requests, then deploy it as a
 * web app (steps in SETUP.md next to this file). It receives two kinds of message from the website's server:
 *   case_review_request  adds one row to the "Case requests" tab, makes a private Drive folder for the request and
 *                        emails NOTIFY_TO with the details;
 *   file_chunk           one piece (up to 3 MB) of an attached photo or document; when a file's pieces are all in,
 *                        it is joined in the request's folder and its link is added to the row. When every file is in,
 *                        a short "files received" email follows.
 * The website never talks to this script directly: its /api functions forward to it, and only they know the web app
 * URL (Vercel environment variable INTAKE_WEBHOOK_URL).
 */

// Who gets the email for each new request. Gmail for now: 10flatlaw.com is not registered yet (3 Nov 2026), so
// contact@10flatlaw.com cannot receive mail. Change this line once the firm's mailbox works.
const NOTIFY_TO = '10flatlaw@gmail.com';
const SHEET_NAME = 'Case requests';                  // tab created on first use
const FOLDER_NAME = '10flat Law case uploads';       // Drive folder created on first use (private to this account)

const HEADERS = ['Received (Texas time)', 'Reference', 'Name', 'Mobile', 'What happened', 'Date of incident', 'Texas county',
  'Government involved', 'Language', 'Seen a doctor or dentist', 'Already has a lawyer', 'Insurance company',
  'What happened and injuries', 'Files', 'Status'];
const FILES_COL = HEADERS.indexOf('Files') + 1;

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(28000);
  try {
    const d = JSON.parse(e.postData.contents);
    if (d.type === 'case_review_request') return reply(newRequest(d));
    if (d.type === 'file_chunk') return reply(filePiece(d));
    return reply({ ok: false, error: 'wrong_type' });
  } catch (err) {
    console.error(err);
    return reply({ ok: false, error: 'server_error' });
  } finally {
    lock.releaseLock();
  }
}

function newRequest(d) {
  const received = Utilities.formatDate(new Date(d.receivedAt || Date.now()), 'America/Chicago', 'yyyy-MM-dd HH:mm');
  const folder = subFolder(rootFolder(), received + ' ' + (d.ref ? d.ref + ' ' : '') + (d.name || 'request'));

  // files sent inside the request itself (older form versions)
  const blobs = [];
  const links = [];
  (Array.isArray(d.files) ? d.files : []).forEach(function (f) {
    const blob = Utilities.newBlob(Utilities.base64Decode(f.data), f.type || 'application/octet-stream', f.name || 'file');
    const file = folder.createFile(blob);
    links.push(file.getName() + ': ' + file.getUrl());
    blobs.push(blob);
  });
  const expected = Number(d.filesExpected) || 0;
  const filesCell = links.length ? links.join('\n') : expected ? 'Uploading ' + expected + ' file(s)…' : 'None';

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = requestSheet(ss);
  const treatment = { yes: 'Yes', no: 'No', scheduled: 'Appointment scheduled' }[d.treatment] || d.treatment;
  const government = { yes: 'Yes', no: 'No', unsure: 'Not sure' }[d.government] || d.government || '';
  const when = d.dateUnsure ? (d.date ? 'About ' + d.date + ' (not sure)' : 'Not sure') : d.date;
  sheet.appendRow([received, d.ref || '', d.name, d.phone, d.incident, when, d.county, government, d.language, treatment,
    d.hasLawyer ? 'Yes' : 'No', d.insurer || '', d.story, filesCell, 'New'].map(safe));
  const row = sheet.getLastRow();

  if (expected && d.uploadKey) {
    PropertiesService.getScriptProperties().setProperty('up:' + d.ref, JSON.stringify({
      key: d.uploadKey, folder: folder.getId(), row: row, expected: expected, done: [], links: [], at: Date.now(),
    }));
  }

  const rows = [['Reference', d.ref || ''], ['Name', d.name], ['Mobile', d.phone], ['What happened', d.incident], ['Date of incident', when],
    ['Texas county', d.county], ['Government vehicle or property', government], ['Language', d.language],
    ['Seen a doctor or dentist', treatment], ['Already has a lawyer', d.hasLawyer ? 'Yes' : 'No'],
    ['Insurance company', d.insurer || '(not given)'],
    ['Files', links.length ? links.length + ' attached' : expected ? expected + ' uploading; you will get a second email when they are in' : 'None']];
  const urgent = d.government === 'yes' || d.government === 'unsure';
  const html = (urgent ? '<p style="font:14px Arial,sans-serif;color:#b3261e"><b>Possible government claim: notice deadlines can be as short as 6 months.</b></p>' : '') +
    '<p><b>New case review request</b> from the website, received ' + esc(received) + ' (Texas time).</p>' +
    '<table cellpadding="6" style="border-collapse:collapse;font:14px Arial,sans-serif">' +
    rows.map(function (r) { return '<tr><td style="color:#666">' + esc(r[0]) + '</td><td><b>' + esc(r[1]) + '</b></td></tr>'; }).join('') +
    '</table><p style="font:14px Arial,sans-serif"><b>What happened and injuries</b><br>' + esc(d.story).replace(/\n/g, '<br>') + '</p>' +
    '<p style="font:13px Arial,sans-serif;color:#666">Sheet: ' + ss.getUrl() + '<br>Files folder: ' + folder.getUrl() + '</p>';
  MailApp.sendEmail({
    to: NOTIFY_TO,
    subject: (urgent ? 'URGENT ' : '') + 'New case request ' + (d.ref ? d.ref + ': ' : ': ') + d.incident + ', ' + d.county + ' County (' + d.name + ')',
    htmlBody: html,
    attachments: blobs,
    name: '10flat Law website',
  });
  return { ok: true };
}

function filePiece(d) {
  const props = PropertiesService.getScriptProperties();
  const raw = props.getProperty('up:' + d.ref);
  if (!raw) return { ok: false, error: 'unknown_request' };
  const up = JSON.parse(raw);
  if (up.key !== d.token) return { ok: false, error: 'bad_key' };
  if (Date.now() - up.at > 6 * 3600 * 1000) return { ok: false, error: 'expired' };
  if (up.done.indexOf(d.file) > -1) return { ok: true };

  const folder = DriveApp.getFolderById(up.folder);
  const partName = '.part ' + d.file + ' ' + d.chunk;
  const existing = folder.getFilesByName(partName);
  while (existing.hasNext()) existing.next().setTrashed(true);
  folder.createFile(Utilities.newBlob(Utilities.base64Decode(d.data), 'application/octet-stream', partName));

  // all pieces of this file in? join them
  const parts = [];
  for (let i = 0; i < d.chunks; i++) {
    const it = folder.getFilesByName('.part ' + d.file + ' ' + i);
    if (!it.hasNext()) return { ok: true };
    parts.push(it.next());
  }
  let bytes = [];
  parts.forEach(function (p) { bytes = bytes.concat(p.getBlob().getBytes()); });
  const file = folder.createFile(Utilities.newBlob(bytes, d.mime || 'application/octet-stream', d.name || 'file'));
  parts.forEach(function (p) { p.setTrashed(true); });

  up.done.push(d.file);
  up.links.push(file.getName() + ': ' + file.getUrl());
  const sheet = requestSheet(SpreadsheetApp.getActiveSpreadsheet());
  const left = up.expected - up.done.length;
  sheet.getRange(up.row, FILES_COL).setValue(safe(up.links.join('\n') + (left > 0 ? '\n(' + left + ' more uploading…)' : '')));
  if (left <= 0) {
    props.deleteProperty('up:' + d.ref);
    MailApp.sendEmail({
      to: NOTIFY_TO,
      subject: 'Files received for ' + d.ref,
      htmlBody: '<p style="font:14px Arial,sans-serif">All ' + up.expected + ' file(s) for case request <b>' + esc(d.ref) + '</b> are in:</p><p style="font:14px Arial,sans-serif">' +
        up.links.map(function (l) { return esc(l); }).join('<br>') + '</p><p style="font:13px Arial,sans-serif;color:#666">Folder: ' + folder.getUrl() + '</p>',
      name: '10flat Law website',
    });
  } else {
    props.setProperty('up:' + d.ref, JSON.stringify(up));
  }
  return { ok: true };
}

// Run this once from the editor (select "testSetup", press Run) to grant permissions and see a sample row and email.
function testSetup() {
  newRequest({
    type: 'case_review_request', ref: '10F-TEST-0000', receivedAt: new Date().toISOString(), name: 'Test request', phone: '000 000 0000',
    incident: 'Car accident', date: '2026-11-01', county: 'Harris', government: 'no', language: 'English', treatment: 'yes',
    hasLawyer: false, insurer: '', story: 'Setup test. Delete this row and its folder.', filesExpected: 0,
  });
}

// Tidies up uploads that never finished (optional: add a daily time-driven trigger for this function).
function cleanUploads() {
  const props = PropertiesService.getScriptProperties();
  const all = props.getProperties();
  Object.keys(all).forEach(function (k) {
    if (k.indexOf('up:') !== 0) return;
    const up = JSON.parse(all[k]);
    if (Date.now() - up.at > 24 * 3600 * 1000) props.deleteProperty(k);
  });
}

function requestSheet(ss) {
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(SHEET_NAME, 0);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
  }
  return sheet;
}

function rootFolder() {
  const it = DriveApp.getFoldersByName(FOLDER_NAME);
  return it.hasNext() ? it.next() : DriveApp.createFolder(FOLDER_NAME);
}

function subFolder(parent, name) {
  return parent.createFolder(name.replace(/[\\/]/g, '-').slice(0, 120));
}

// Stops a value that starts with = + - @ from being read as a spreadsheet formula.
function safe(v) {
  const s = v == null ? '' : String(v);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

function esc(v) {
  return String(v == null ? '' : v).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
