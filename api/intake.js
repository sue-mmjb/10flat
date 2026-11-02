// Vercel function behind the case form (/start and /es/start). It checks the request and forwards it as JSON to the
// webhook in the INTAKE_WEBHOOK_URL environment variable (the Google Apps Script in integrations/google-sheet-intake,
// or any service that accepts a JSON POST). Nothing is stored here. It answers with the request's reference and a
// one-time upload key; the form then sends any files in pieces to /api/intake-file.
// If a request can't be delivered, an alert goes to INTAKE_ALERT_URL (optional: any JSON webhook) and the details are
// written to the Vercel function log, so a lost lead is noticed.

const { str, body, reference, uploadKey, forward, alertLostLead } = require("./_shared");

const CASE_TYPES = ["Car accident", "Truck accident", "Slip and fall", "Medical injury", "Dental injury", "Something else"];
const LANGS = ["English", "Español"];
const TREATMENT = ["yes", "no", "scheduled"];
const GOVERNMENT = ["yes", "no", "unsure"];
const MAX_FILES = 10;

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "method_not_allowed" });
  }
  const b = body(req);
  if (!b) return res.status(400).json({ ok: false, error: "bad_request" });

  // honeypot: real people never see or fill this field
  if (str(b.company, 200)) return res.status(200).json({ ok: true });

  const today = new Date().toISOString().slice(0, 10);
  const r = {
    name: str(b.name, 100),
    phone: str(b.phone, 30),
    incident: str(b.incident, 40),
    date: str(b.date, 10),
    dateUnsure: b.dateUnsure === true,
    county: str(b.county, 60),
    language: str(b.language, 20) || "English",
    government: str(b.government, 10),
    treatment: str(b.treatment, 20),
    insurer: str(b.insurer, 100),
    story: str(b.story, 4000),
    hasLawyer: b.hasLawyer === true,
    consent: b.consent === true,
    page: str(b.page, 40),
    filesExpected: Number.isInteger(b.filesExpected) ? b.filesExpected : 0,
    fileNames: Array.isArray(b.fileNames) ? b.fileNames.slice(0, MAX_FILES).map((n) => str(n, 120)) : [],
  };
  const digits = r.phone.replace(/[^0-9]/g, "");
  const problems = [];
  if (r.name.length < 2) problems.push("name");
  if (digits.length < 10 || digits.length > 15) problems.push("phone");
  if (!CASE_TYPES.includes(r.incident)) problems.push("incident");
  if (r.dateUnsure ? (r.date && (!/^\d{4}-\d{2}-\d{2}$/.test(r.date) || r.date > today))
                    : (!/^\d{4}-\d{2}-\d{2}$/.test(r.date) || r.date > today)) problems.push("date");
  if (r.county.length < 2) problems.push("county");
  if (!LANGS.includes(r.language)) problems.push("language");
  if (!GOVERNMENT.includes(r.government)) problems.push("government");
  if (!TREATMENT.includes(r.treatment)) problems.push("treatment");
  if (r.story.length < 10) problems.push("story");
  if (!r.consent) problems.push("consent");
  if (r.filesExpected < 0 || r.filesExpected > MAX_FILES) problems.push("files");
  if (problems.length) return res.status(422).json({ ok: false, error: "invalid", fields: problems });

  const record = {
    type: "case_review_request",
    ref: reference(),
    receivedAt: new Date().toISOString(),
    source: "website " + (r.page || "/start"),
    ...r,
    uploadKey: r.filesExpected ? uploadKey() : "",
  };
  const sent = await forward(record, 25000);
  if (!sent.ok) {
    await alertLostLead(record, sent.why);
    return res.status(sent.status).json({ ok: false, error: sent.status === 503 ? "not_configured" : "forward_failed" });
  }
  return res.status(200).json({ ok: true, ref: record.ref, upload: record.uploadKey || undefined });
};
