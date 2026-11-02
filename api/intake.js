// Vercel function behind the "Start your case" page (site/start). It checks the request and forwards it as JSON
// to the webhook in the INTAKE_WEBHOOK_URL environment variable (set in Vercel: Project > Settings > Environment
// Variables). Any service that accepts a JSON POST works: Zapier, Make, a Google Apps Script web app writing to a
// Sheet, a CRM's inbound webhook, or the firm's intake system. Nothing is stored here.

const CASE_TYPES = ["Car accident", "Truck accident", "Slip and fall", "Medical injury", "Dental injury", "Something else"];
const LANGS = ["English", "Español"];
const TREATMENT = ["yes", "no", "scheduled"];
const MAX_FILES = 5;
const MAX_TOTAL = 3 * 1024 * 1024; // bytes after decoding; keeps the request under Vercel's 4.5 MB body limit
const FILE_TYPE = /^(image\/(jpeg|png|webp|heic|heif|gif)|application\/pdf|application\/octet-stream)$/;

function str(v, max) {
  return typeof v === "string" ? v.trim().slice(0, max) : "";
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "method_not_allowed" });
  }
  let b = req.body;
  if (typeof b === "string") {
    try { b = JSON.parse(b); } catch (e) { b = null; }
  }
  if (!b || typeof b !== "object") return res.status(400).json({ ok: false, error: "bad_request" });

  // honeypot: real people never see or fill this field
  if (str(b.company, 200)) return res.status(200).json({ ok: true });

  const today = new Date().toISOString().slice(0, 10);
  const r = {
    name: str(b.name, 100),
    phone: str(b.phone, 30),
    incident: str(b.incident, 40),
    date: str(b.date, 10),
    county: str(b.county, 60),
    language: str(b.language, 20) || "English",
    treatment: str(b.treatment, 20),
    insurer: str(b.insurer, 100),
    story: str(b.story, 4000),
    hasLawyer: b.hasLawyer === true,
    consent: b.consent === true,
  };
  // optional attachments: [{name, type, data (base64)}]
  const files = [];
  let bytes = 0, badFiles = false;
  if (b.files !== undefined) {
    if (!Array.isArray(b.files) || b.files.length > MAX_FILES) badFiles = true;
    else for (const f of b.files) {
      const name = f && str(f.name, 120).replace(/[\\/:*?"<>|\u0000-\u001f]/g, "_");
      const type = f && str(f.type, 60);
      const data = f && typeof f.data === "string" ? f.data : "";
      if (!name || !FILE_TYPE.test(type) || !/^[A-Za-z0-9+/=]+$/.test(data)) { badFiles = true; break; }
      const size = Math.floor((data.length * 3) / 4) - (data.endsWith("==") ? 2 : data.endsWith("=") ? 1 : 0);
      bytes += size;
      files.push({ name, type, size, data });
    }
    if (bytes > MAX_TOTAL) badFiles = true;
  }
  const digits = r.phone.replace(/[^0-9]/g, "");
  const problems = [];
  if (r.name.length < 2) problems.push("name");
  if (digits.length < 10 || digits.length > 15) problems.push("phone");
  if (!CASE_TYPES.includes(r.incident)) problems.push("incident");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(r.date) || r.date > today) problems.push("date");
  if (r.county.length < 2) problems.push("county");
  if (!LANGS.includes(r.language)) problems.push("language");
  if (!TREATMENT.includes(r.treatment)) problems.push("treatment");
  if (r.story.length < 10) problems.push("story");
  if (!r.consent) problems.push("consent");
  if (badFiles) problems.push("files");
  if (problems.length) return res.status(422).json({ ok: false, error: "invalid", fields: problems });

  const url = process.env.INTAKE_WEBHOOK_URL;
  if (!url) return res.status(503).json({ ok: false, error: "not_configured" });

  const record = {
    type: "case_review_request",
    receivedAt: new Date().toISOString(),
    source: "website /start",
    ...r,
    files,
  };
  try {
    const out = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
      signal: AbortSignal.timeout(25000),
    });
    if (!out.ok) return res.status(502).json({ ok: false, error: "forward_failed" });
    // the Google Apps Script receiver answers {"ok":true}; anything else means it did not save the request
    const reply = await out.json().catch(() => null);
    if (reply && reply.ok === false) return res.status(502).json({ ok: false, error: "forward_failed" });
  } catch (e) {
    return res.status(502).json({ ok: false, error: "forward_failed" });
  }
  return res.status(200).json({ ok: true });
};
