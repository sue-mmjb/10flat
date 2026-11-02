/**
 * 10flat Law: case requests from the website's "Start your case" page.
 *
 * Paste this into Extensions > Apps Script of the Google Sheet that should hold the requests, then deploy it as a
 * web app (steps in SETUP.md next to this file). For every request it:
 *   1. saves any attached photos or documents in a private Google Drive folder,
 *   2. adds one row to the "Case requests" tab,
 *   3. emails NOTIFY_TO with the details and the files attached.
 * The website never talks to this script directly: the site's /api/intake function forwards to it, and only that
 * function knows the web app URL (Vercel environment variable INTAKE_WEBHOOK_URL).
 */

const NOTIFY_TO = 'contact@10flatlaw.com';          // who gets the email for each new request
const SHEET_NAME = 'Case requests';                  // tab created on first use
const FOLDER_NAME = '10flat Law case uploads';       // Drive folder created on first use (private to this account)

const HEADERS = ['Received (Texas time)', 'Name', 'Mobile', 'What happened', 'Date of incident', 'Texas county',
  'Language', 'Seen a doctor or dentist', 'Already has a lawyer', 'Insurance company', 'What happened and injuries',
  'Files', 'Status'];

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(25000);
  try {
    const d = JSON.parse(e.postData.contents);
    if (d.type !== 'case_review_request') return reply({ ok: false, error: 'wrong_type' });

    const received = Utilities.formatDate(new Date(d.receivedAt || Date.now()), 'America/Chicago', 'yyyy-MM-dd HH:mm');

    // 1. files to Drive
    const blobs = [];
    const links = [];
    if (Array.isArray(d.files) && d.files.length) {
      const folder = subFolder(rootFolder(), received + ' ' + (d.name || 'request'));
      d.files.forEach(function (f) {
        const blob = Utilities.newBlob(Utilities.base64Decode(f.data), f.type || 'application/octet-stream', f.name || 'file');
        const file = folder.createFile(blob);
        links.push(file.getName() + ': ' + file.getUrl());
        blobs.push(blob);
      });
    }

    // 2. the row
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) sheet = ss.insertSheet(SHEET_NAME, 0);
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.setFrozenRows(1);
      sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    }
    const treatment = { yes: 'Yes', no: 'No', scheduled: 'Appointment scheduled' }[d.treatment] || d.treatment;
    sheet.appendRow([received, d.name, d.phone, d.incident, d.date, d.county, d.language, treatment,
      d.hasLawyer ? 'Yes' : 'No', d.insurer || '', d.story, links.join('\n'), 'New'].map(safe));

    // 3. the email
    const rows = [['Name', d.name], ['Mobile', d.phone], ['What happened', d.incident], ['Date of incident', d.date],
      ['Texas county', d.county], ['Language', d.language], ['Seen a doctor or dentist', treatment],
      ['Already has a lawyer', d.hasLawyer ? 'Yes' : 'No'], ['Insurance company', d.insurer || '(not given)'],
      ['Files', links.length ? links.length + ' attached' : 'None']];
    const html = '<p><b>New case review request</b> from the website, received ' + esc(received) + ' (Texas time).</p>' +
      '<table cellpadding="6" style="border-collapse:collapse;font:14px Arial,sans-serif">' +
      rows.map(function (r) { return '<tr><td style="color:#666">' + esc(r[0]) + '</td><td><b>' + esc(r[1]) + '</b></td></tr>'; }).join('') +
      '</table><p style="font:14px Arial,sans-serif"><b>What happened and injuries</b><br>' + esc(d.story).replace(/\n/g, '<br>') + '</p>' +
      '<p style="font:13px Arial,sans-serif;color:#666">Saved in the "' + SHEET_NAME + '" sheet: ' + ss.getUrl() + '</p>';
    MailApp.sendEmail({
      to: NOTIFY_TO,
      subject: 'New case request: ' + d.incident + ', ' + d.county + ' County (' + d.name + ')',
      htmlBody: html,
      attachments: blobs,
      name: '10flat Law website',
    });

    return reply({ ok: true });
  } catch (err) {
    console.error(err);
    return reply({ ok: false, error: 'server_error' });
  } finally {
    lock.releaseLock();
  }
}

// Run this once from the editor (select "testSetup", press Run) to grant permissions and see a sample row and email.
function testSetup() {
  doPost({ postData: { contents: JSON.stringify({
    type: 'case_review_request', receivedAt: new Date().toISOString(), name: 'Test request', phone: '000 000 0000',
    incident: 'Car accident', date: '2026-11-01', county: 'Harris', language: 'English', treatment: 'yes',
    hasLawyer: false, insurer: '', story: 'Setup test. Delete this row.', files: [],
  }) } });
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
