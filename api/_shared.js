// Helpers shared by api/intake.js and api/intake-file.js. Files starting with "_" are not deployed as functions.

const crypto = require("crypto");

function str(v, max) {
  return typeof v === "string" ? v.trim().slice(0, max) : "";
}

function body(req) {
  let b = req.body;
  if (typeof b === "string") {
    try { b = JSON.parse(b); } catch (e) { b = null; }
  }
  return b && typeof b === "object" ? b : null;
}

// A short reference the client sees on the thank-you screen and the firm sees in the Sheet and email.
function reference() {
  const d = new Date();
  const ymd = String(d.getUTCFullYear()).slice(2) + String(d.getUTCMonth() + 1).padStart(2, "0") + String(d.getUTCDate()).padStart(2, "0");
  const abc = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let tail = "";
  for (const byte of crypto.randomBytes(4)) tail += abc[byte % abc.length];
  return "10F-" + ymd + "-" + tail;
}

// A one-time key that lets this visitor add files to this request, and nobody else.
function uploadKey() {
  return crypto.randomBytes(18).toString("base64url");
}

async function forward(payload, timeout) {
  const url = process.env.INTAKE_WEBHOOK_URL;
  if (!url) return { ok: false, why: "INTAKE_WEBHOOK_URL is not set", status: 503 };
  try {
    const out = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(timeout || 25000),
    });
    // the Google Apps Script receiver answers {"ok":true}; anything else means it did not save the request
    const reply = out.ok ? await out.json().catch(() => null) : null;
    if (!out.ok || (reply && reply.ok === false)) {
      return { ok: false, why: "receiver answered " + out.status + (reply && reply.error ? " " + reply.error : ""), status: 502 };
    }
    return { ok: true };
  } catch (e) {
    return { ok: false, why: "receiver unreachable: " + String(e && e.name), status: 502 };
  }
}

async function alertLostLead(record, why) {
  const summary = { ref: record.ref, receivedAt: record.receivedAt, why, name: record.name, phone: record.phone,
    incident: record.incident, county: record.county, files: record.filesExpected || 0 };
  console.error("INTAKE NOT DELIVERED", JSON.stringify(summary));
  const url = process.env.INTAKE_ALERT_URL;
  if (!url) return;
  const text = "Case request " + summary.ref + " was NOT delivered (" + why + "). " + summary.name + ", " + summary.phone +
    ", " + summary.incident + ", " + summary.county + " County. Call them back and check the intake setup.";
  try {
    await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, ...summary }),
      signal: AbortSignal.timeout(5000) });
  } catch (e) {
    console.error("INTAKE ALERT FAILED", String(e));
  }
}

module.exports = { str, body, reference, uploadKey, forward, alertLostLead };
