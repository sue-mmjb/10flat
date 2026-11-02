"""Build site/start/index.html: the "Start your case" page where clients send their case for attorney review.

Run on its own or through tools/build_clone.py (which calls it at the end). The form posts JSON to /api/intake
(api/intake.js, a Vercel function) which forwards it to the webhook in the INTAKE_WEBHOOK_URL environment variable.
Fields follow Sue's mock-up of 3 Nov 2026 plus the SOW's required intake facts (incident, date, county, injuries,
treatment, existing lawyer).
"""
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site import CONFIG  # noqa: E402

OUT = ROOT / "site" / "start" / "index.html"
FIRM = CONFIG["firm"]

CASE_TYPES = ["Car accident", "Truck accident", "Slip and fall", "Medical injury", "Dental injury", "Something else"]

DISCLAIMER = (
    f"{FIRM} PLLC, Texas, a law firm owned only by licensed attorneys. Our fee is 10% of the total amount recovered at every stage, "
    "including trial; case costs and liens are paid from your share after the fee. If there is no recovery, you owe no fee and no case costs. "
    "Sending this form does not create an attorney-client relationship until a fee agreement is signed. Attorney advertising."
)

FONTS = """
@font-face{font-family:"Perfektta ExtraBold";src:url("https://framerusercontent.com/assets/ehgAhB5skp3UmdaHTx9XRxEGak.woff2");font-display:swap;font-weight:800}
@font-face{font-family:"GT Alpina Medium";src:url("https://framerusercontent.com/assets/akcrPmCPzVvRITrHAHEcGkGliuE.woff2");font-display:swap;font-weight:500}
@font-face{font-family:"Archivo SemiExpanded SemiBold";src:url("https://framerusercontent.com/assets/Yy0SUpLGt8QS5Po9OqrTNSyrc.woff2");font-display:swap;font-weight:600}
@font-face{font-family:"Instrument Sans";src:url("https://fonts.gstatic.com/s/instrumentsans/v4/pximypc9vsFDm051Uf6KVwgkfoSxQ0GsQv8ToedPibnr-yp2JGEJOH9npSTF-QfwmS0v3_7Y.woff2");font-display:swap;font-weight:400}
@font-face{font-family:"Instrument Sans";src:url("https://fonts.gstatic.com/s/instrumentsans/v4/pximypc9vsFDm051Uf6KVwgkfoSxQ0GsQv8ToedPibnr-yp2JGEJOH9npSQb_gfwmS0v3_7Y.woff2");font-display:swap;font-weight:600}
"""

CSS = """
:root{--ink:#140c0a;--muted:#5f564a;--yellow:#ffe435;--egg:#f7f5ef;--sand:#e9dfc2;--field:#f4efe1;--line:#e3ded2;--white:#fff;--err:#b3261e;--ok:#2f6b3a}
*{box-sizing:border-box}
[hidden]{display:none!important}
html,body{margin:0;background:var(--egg);color:var(--ink);font:400 16px/1.5 "Instrument Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit}
.nav{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;padding:18px 32px;background:rgba(247,245,239,.92);backdrop-filter:blur(8px)}
.mark{font:800 26px/1 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.03em;text-decoration:none}
.back{font:600 15px/1 "Instrument Sans",sans-serif;text-decoration:none;display:inline-flex;gap:8px;align-items:center}
.back:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:40px 32px 72px;display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:56px;align-items:start}
.intro{position:sticky;top:96px}
.eyebrow{font:600 12px/1 "Archivo SemiExpanded SemiBold","Instrument Sans",sans-serif;letter-spacing:.14em;text-transform:uppercase;margin:0 0 16px}
h1{font:800 clamp(40px,5vw,64px)/.95 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.03em;margin:0 0 24px}
.lead{font:500 20px/1.45 "GT Alpina Medium",Georgia,serif;margin:0 0 28px}
.points{list-style:none;margin:0 0 28px;padding:0;display:grid;gap:10px}
.points li{display:flex;gap:12px;align-items:center;font-weight:600}
.points li::before{content:"";flex:none;width:22px;height:22px;border-radius:50%;background:var(--yellow) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23140c0a' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 12.5l4 4 8-9'/%3E%3C/svg%3E") center/14px no-repeat}
.fine{font-size:13px;line-height:1.55;color:var(--muted);margin:0}
.card{background:var(--white);border-radius:28px;padding:36px;box-shadow:0 24px 60px -30px rgba(20,12,10,.25)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px 18px}
.full{grid-column:1/-1}
.field{display:flex;flex-direction:column;gap:8px;min-width:0}
label,.legend{font:600 14px/1.3 "Instrument Sans",sans-serif}
.opt{font-weight:400;color:var(--muted)}
input[type=text],input[type=tel],input[type=date],select,textarea{width:100%;font:400 16px/1.4 "Instrument Sans",sans-serif;color:var(--ink);background:var(--field);border:1.5px solid var(--field);border-radius:14px;padding:14px 16px;min-height:52px;appearance:none;-webkit-appearance:none}
select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23140c0a' stroke-width='2' stroke-linecap='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center;background-size:18px;padding-right:44px}
textarea{min-height:132px;resize:vertical}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--ink);background-color:var(--white)}
.field.bad input,.field.bad select,.field.bad textarea{border-color:var(--err);background-color:#fff6f5}
.err{font-size:13px;color:var(--err);min-height:0;margin:0}
.err:empty{display:none}
fieldset{border:0;margin:0;padding:0;min-width:0}
.choices{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px}
.choice{position:relative}
.choice input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}
.choice span{display:inline-flex;align-items:center;min-height:44px;padding:0 18px;border-radius:999px;background:var(--field);border:1.5px solid var(--field);font-weight:600;font-size:15px}
.choice input:checked+span{background:var(--yellow);border-color:var(--yellow)}
.choice input:focus-visible+span{border-color:var(--ink)}
.note{background:var(--field);border-radius:14px;padding:14px 16px;font-size:14px;margin:12px 0 0}
.consent{display:flex;gap:12px;align-items:flex-start;font-size:14px;line-height:1.5;color:var(--muted);font-weight:400}
.consent input{flex:none;width:22px;height:22px;margin:1px 0 0;accent-color:var(--ink)}
.btn{width:100%;border:0;border-radius:999px;background:var(--yellow);color:var(--ink);min-height:58px;font:600 14px/1 "Archivo SemiExpanded SemiBold","Instrument Sans",sans-serif;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:transform .15s ease,background .15s}
.btn:hover{background:#f5d800}
.btn:active{transform:scale(.99)}
.btn[disabled]{opacity:.6;cursor:progress}
.formerr{background:#fff6f5;color:var(--err);border-radius:14px;padding:14px 16px;font-size:14px;margin:0}
.formerr:empty{display:none}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.done{text-align:left}
.done h2{font:800 40px/1 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.03em;margin:0 0 16px}
.done p{font:500 19px/1.5 "GT Alpina Medium",Georgia,serif;margin:0 0 14px}
.done ol{margin:20px 0 28px;padding-left:22px;display:grid;gap:8px}
.done a.btn{display:inline-flex;align-items:center;justify-content:center;text-decoration:none;width:auto;padding:0 28px}
footer{border-top:1px solid var(--line);padding:28px 32px 40px;max-width:1180px;margin:0 auto;font-size:12.5px;line-height:1.55;color:var(--muted)}
@media(max-width:900px){
  .wrap{grid-template-columns:1fr;gap:28px;padding:20px 20px 56px}
  .intro{position:static}
  .nav{padding:14px 20px}
  .lead{font-size:18px}
  footer{padding:24px 20px 36px}
}
@media(max-width:560px){
  .card{padding:24px 20px;border-radius:24px}
  .grid{grid-template-columns:1fr}
}
"""

JS = """
(function () {
  var form = document.getElementById('case-form'), el = function (n) { return form.elements.namedItem(n); }, btn = document.getElementById('send'), formErr = document.getElementById('form-err');
  var date = document.getElementById('f-date');
  var t = new Date(); date.max = t.getFullYear() + '-' + String(t.getMonth() + 1).padStart(2, '0') + '-' + String(t.getDate()).padStart(2, '0');
  var lawyerNote = document.getElementById('lawyer-note');
  [].forEach.call(form.querySelectorAll('input[name=lawyer]'), function (r) {
    r.addEventListener('change', function () { lawyerNote.hidden = el('lawyer').value !== 'yes'; });
  });
  var MSG = {
    name: 'Please tell us your name.',
    phone: 'Please enter a mobile number we can reach you on.',
    incident: 'Please choose what happened.',
    date: 'Please enter the date it happened (not in the future).',
    county: 'Please enter the Texas county where it happened.',
    treatment: 'Please tell us whether you have seen a doctor or dentist.',
    story: 'Please tell us briefly what happened and how you were hurt.',
    consent: 'Please tick the box so we can contact you about your request.'
  };
  function setErr(name, msg) {
    var f = form.querySelector('[data-field="' + name + '"]'); if (!f) return;
    f.classList.toggle('bad', !!msg);
    var e = f.querySelector('.err'); if (e) e.textContent = msg || '';
  }
  function check() {
    var bad = [];
    var v = {
      name: el('name').value.trim(), phone: el('phone').value.trim(), incident: el('incident').value, date: el('date').value,
      county: el('county').value.trim(), treatment: el('treatment').value, story: el('story').value.trim(), consent: el('consent').checked
    };
    var digits = v.phone.replace(/[^0-9]/g, '');
    var ok = {
      name: v.name.length >= 2, phone: digits.length >= 10 && digits.length <= 15, incident: !!v.incident,
      date: !!v.date && v.date <= date.max, county: v.county.length >= 2, treatment: !!v.treatment, story: v.story.length >= 10, consent: v.consent
    };
    Object.keys(ok).forEach(function (k) { setErr(k, ok[k] ? '' : MSG[k]); if (!ok[k]) bad.push(k); });
    return bad;
  }
  form.addEventListener('input', function (e) { var f = e.target.closest('[data-field]'); if (f && f.classList.contains('bad')) check(); });
  form.addEventListener('change', function (e) { var f = e.target.closest('[data-field]'); if (f && f.classList.contains('bad')) check(); });
  form.addEventListener('submit', function (e) {
    e.preventDefault(); formErr.textContent = '';
    var bad = check();
    if (bad.length) { var first = form.querySelector('[data-field="' + bad[0] + '"] input, [data-field="' + bad[0] + '"] select, [data-field="' + bad[0] + '"] textarea'); if (first) first.focus(); return; }
    var data = {
      name: el('name').value.trim(), phone: el('phone').value.trim(), incident: el('incident').value, date: el('date').value,
      county: el('county').value.trim(), language: el('language').value, treatment: el('treatment').value,
      insurer: el('insurer').value.trim(), story: el('story').value.trim(), hasLawyer: el('lawyer').value === 'yes',
      consent: true, company: el('company').value, page: location.href
    };
    btn.disabled = true; btn.textContent = 'Sending…';
    fetch('/api/intake', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, body: j }; }); })
      .then(function (res) {
        if (res.status === 200 && res.body.ok) {
          document.getElementById('done-name').textContent = data.name.split(/\\s+/)[0];
          form.hidden = true; var d = document.getElementById('done'); d.hidden = false; d.focus();
          window.scrollTo({ top: 0, behavior: 'smooth' });
          return;
        }
        throw new Error(res.status);
      })
      .catch(function () {
        formErr.textContent = 'Sorry, we couldn’t send your request just now, and nothing was saved. Please try again in a few minutes.';
        btn.disabled = false; btn.textContent = 'Send for attorney review';
      });
  });
})();
"""


def field(name, label, control, full=False, optional=False):
    opt = ' <span class="opt">(optional)</span>' if optional else ""
    return (f'<div class="field{" full" if full else ""}" data-field="{name}">'
            f'<label for="f-{name}">{label}{opt}</label>{control}'
            f'<p class="err" id="e-{name}" aria-live="polite"></p></div>')


def radios(name, legend, options, full=True, checked=None):
    items = "".join(
        f'<label class="choice"><input type="radio" name="{name}" value="{v}"{" checked" if v == checked else ""}><span>{t}</span></label>'
        for v, t in options)
    return (f'<fieldset class="field{" full" if full else ""}" data-field="{name}"><legend class="legend">{legend}</legend>'
            f'<div class="choices">{items}</div><p class="err" id="e-{name}" aria-live="polite"></p></fieldset>')


def build():
    case_opts = '<option value="">Choose one</option>' + "".join(f'<option>{escape(c)}</option>' for c in CASE_TYPES)
    form = "".join([
        field("name", "Your name", '<input type="text" id="f-name" name="name" autocomplete="name" maxlength="100" aria-describedby="e-name">'),
        field("phone", "Mobile number", '<input type="tel" id="f-phone" name="phone" autocomplete="tel" inputmode="tel" maxlength="30" aria-describedby="e-phone">'),
        field("incident", "What happened?", f'<select id="f-incident" name="incident" aria-describedby="e-incident">{case_opts}</select>'),
        field("date", "When did it happen?", '<input type="date" id="f-date" name="date" aria-describedby="e-date">'),
        field("county", "Texas county", '<input type="text" id="f-county" name="county" autocomplete="address-level2" maxlength="60" aria-describedby="e-county">'),
        field("language", "Preferred language", '<select id="f-language" name="language"><option>English</option><option>Español</option></select>'),
        radios("treatment", "Have you seen a doctor or dentist for this?", [("yes", "Yes"), ("no", "No"), ("scheduled", "Appointment scheduled")]),
        field("story", "Briefly, what happened and how were you hurt?", '<textarea id="f-story" name="story" maxlength="4000" aria-describedby="e-story"></textarea>', full=True),
        field("insurer", "Insurance company involved", '<input type="text" id="f-insurer" name="insurer" maxlength="100">', full=True, optional=True),
        radios("lawyer", "Do you already have a lawyer for this?", [("no", "No"), ("yes", "Yes")], checked="no"),
        '<p class="note full" id="lawyer-note" hidden>Thanks for telling us. An attorney will read your request first. We don’t ask people who already have a lawyer to switch; if you want to talk about changing lawyers, say so above.</p>',
        f'<div class="field full" data-field="consent"><label class="consent"><input type="checkbox" id="f-consent" name="consent" aria-describedby="e-consent">'
        f'<span>I agree that {FIRM} may contact me about my request by phone, text or WhatsApp, and that technology helps organize my information for attorney review.</span></label>'
        f'<p class="err" id="e-consent" aria-live="polite"></p></div>',
        '<div class="hp" aria-hidden="true"><label for="f-company">Company</label><input type="text" id="f-company" name="company" tabindex="-1" autocomplete="off"></div>',
        '<p class="formerr full" id="form-err" role="alert"></p>',
        '<div class="full"><button type="submit" class="btn" id="send">Send for attorney review</button></div>',
    ])
    robots = '<meta name="robots" content="noindex, nofollow">' if CONFIG.get("noindex") else ""
    page = f"""<!doctype html>
<!-- Built by tools/build_start.py. Do not edit by hand; edit the script and rebuild. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Start your case | {FIRM}</title>
<meta name="description" content="Tell {FIRM} what happened. A licensed Texas attorney reviews every request. 10% fee, even at trial; no fee and no costs without a recovery.">
{robots}
<link rel="canonical" href="https://{CONFIG['domain']}/start">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23ffe435'/%3E%3Ctext x='16' y='22' font-family='Arial' font-weight='900' font-size='15' text-anchor='middle' fill='%23140c0a'%3E10%3C/text%3E%3C/svg%3E">
<style>{FONTS}{CSS}</style>
</head>
<body>
<header class="nav"><a class="mark" href="/">{FIRM}</a><a class="back" href="/">&larr; Back to home</a></header>
<main class="wrap">
  <section class="intro" aria-labelledby="h">
    <p class="eyebrow">Start my case review</p>
    <h1 id="h">Tell us what happened.</h1>
    <p class="lead">It takes about three minutes. A licensed Texas attorney reviews every request, and we tell you when to expect an answer, whether or not we can take your case.</p>
    <ul class="points">
      <li>10% fee, even at trial</li>
      <li>No fee and no costs without a recovery</li>
      <li>Se habla español</li>
    </ul>
    <p class="fine">Sending this form does not create an attorney-client relationship. Please don’t include anything you consider highly sensitive; your attorney will ask for records securely later.</p>
  </section>
  <section class="card" aria-label="Case review form">
    <form id="case-form" class="grid" novalidate>{form}</form>
    <div class="done" id="done" hidden tabindex="-1">
      <h2>Thank you, <span id="done-name"></span>.</h2>
      <p>We have your request. A licensed Texas attorney will review it.</p>
      <ol>
        <li>We message you on the mobile number you gave us, with the date to expect an answer.</li>
        <li>The attorney reviews what you sent and may ask for a few more details.</li>
        <li>If we can take your case, you meet your attorney and see the fee agreement before you sign anything.</li>
      </ol>
      <a class="btn" href="/">Back to home</a>
    </div>
  </section>
</main>
<footer>{escape(DISCLAIMER)}</footer>
<script>{JS}</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", "", page, flags=re.S)))
    m = re.search(r"\[[^\]]{2,80}\]", text)
    if m:
        raise SystemExit(f"build_start: placeholder on the page: {m.group(0)!r}")
    print(f"built {OUT.relative_to(ROOT)}: {len(page):,} bytes")


if __name__ == "__main__":
    build()
