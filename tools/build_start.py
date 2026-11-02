"""Build the case form in English (/start) and Spanish (/es/start), plus /privacy and /terms.

The form posts the case to /api/intake (api/intake.js), which forwards it to the Google Sheet script and returns a
reference and an upload key; files then go up in pieces to /api/intake-file, so the limit is 25 MB in total instead
of the 4.5 MB a single request allows. Unsent answers are kept on the visitor's own device until the form is sent.
Fields: the 3 Nov mock-up, the SOW's intake facts, and the round 2 review (government involvement, drafts, uploads,
Spanish).
"""
import json
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_common import FIRM, finalize, footer, footer_es, head, nav, nav_es  # noqa: E402
from texas_counties import COUNTIES  # noqa: E402

CASE_TYPES = ["Car accident", "Truck accident", "Slip and fall", "Medical injury", "Dental injury", "Something else"]

T = {
    "en": {
        "path": "/start", "out": "start/index.html", "title": "Start your case",
        "desc": f"Tell {FIRM} what happened. A licensed Texas attorney reviews every request. 10% fee, even at trial; no fee and no costs without a recovery.",
        "h1": "Tell us what happened.",
        "lead": "It takes about three minutes. A licensed Texas attorney reviews every request, and we tell you when to expect an answer, whether or not we can take your case.",
        "points": ["10% fee, even at trial", "No fee and no costs without a recovery", "A licensed Texas attorney reviews every request"],
        "fine": "Sending this form does not create an attorney-client relationship. Please don’t send anything you consider highly sensitive, such as full medical records; your attorney will ask for those securely later.",
        "cases": CASE_TYPES, "choose": "Choose one",
        "name": "Your name", "phone": "Mobile number", "incident": "What happened?", "date": "When did it happen?",
        "unsure": "I’m not sure of the exact date",
        "deadline": "Texas injury deadlines are generally two years from the date of the injury. Please send this today, and an attorney will look at the deadline first.",
        "county": "Texas county",
        "county_note": "We couldn’t match that to a Texas county. If it happened outside Texas we may not be able to help, but send it anyway and we’ll tell you.",
        "language": "Preferred language", "lang_default": "English",
        "gov": "Was a city, county, state or school vehicle or property involved?", "gov_opts": ["Yes", "No", "Not sure"],
        "gov_warn": "Claims against a government can have a notice deadline as short as 6 months, and some cities set shorter ones. Please send this today.",
        "treatment": "Have you seen a doctor or dentist for this?", "treat_opts": ["Yes", "No", "Appointment scheduled"],
        "story": "Briefly, what happened and how were you hurt?",
        "files": "Photos or documents", "optional": "(optional)", "drop": "Add photos or documents",
        "drop_hint": "Scene or injury photos, police report, bills or insurer letters. Up to 10 files, 25 MB in total.",
        "insurer": "Insurance company involved", "lawyer": "Do you already have a lawyer for this?", "yn": ["No", "Yes"],
        "lawyer_note": "Thanks for telling us. An attorney will read your request first. We don’t ask people who already have a lawyer to switch; if you want to talk about changing lawyers, say so above.",
        "consent": f"I agree that {FIRM} may contact me about my request by phone, text or WhatsApp, and that technology helps organize my information for attorney review, as the <a href=\"/privacy\" target=\"_blank\">Privacy Policy</a> explains. Message and data rates may apply. Reply STOP to opt out of texts.",
        "send": "Send for attorney review", "sending": "Sending…", "uploading": "Uploading file {i} of {n}…",
        "draft": "We restored the answers you hadn’t sent yet.", "start_over": "Start over",
        "done_h": "Thank you, {name}.", "done_p": "We have your request. A licensed Texas attorney will review it.", "ref": "Your reference:",
        "done_steps": ["We message you on the mobile number you gave us, with the date to expect an answer.",
                       "The attorney reviews what you sent and may ask for a few more details.",
                       "If we can take your case, you see your attorney’s name and Texas license, and the fee agreement, before you sign anything."],
        "back": "Back to home", "back_href": "/",
        "msg": {
            "name": "Please tell us your name.", "phone": "Please enter a mobile number we can reach you on.",
            "incident": "Please choose what happened.",
            "date": "Please enter the date it happened (not in the future), or tick “not sure” and give your best guess.",
            "county": "Please enter the Texas county where it happened.",
            "government": "Please tell us whether a government vehicle or property was involved, or choose “Not sure”.",
            "treatment": "Please tell us whether you have seen a doctor or dentist.",
            "story": "Please tell us briefly what happened and how you were hurt.",
            "consent": "Please tick the box so we can contact you about your request.",
            "not_file": "“{f}” isn’t a photo or PDF.", "too_many": "You can add up to 10 files here; your attorney can collect more later.",
            "too_big": "“{f}” is too large to send here (25 MB in total). Your attorney can collect larger files later.",
            "remove": "Remove", "fail": "Sorry, we couldn’t send your request just now, and nothing was saved. Please try again in a few minutes.",
            "partial": "We have your request, but {n} file(s) didn’t upload. Your attorney will ask you for them.",
        },
    },
    "es": {
        "path": "/es/start", "out": "es/start/index.html", "title": "Empiece su caso",
        "desc": f"Cuéntele a {FIRM} qué pasó. Un abogado con licencia en Texas revisa cada solicitud. Honorarios del 10%, incluso en juicio; sin honorarios ni gastos si no hay recuperación.",
        "h1": "Cuéntenos qué pasó.",
        "lead": "Toma unos tres minutos. Un abogado con licencia en Texas revisa cada solicitud, y le decimos cuándo esperar una respuesta, podamos o no tomar su caso.",
        "points": ["Honorarios del 10%, incluso en juicio", "Sin honorarios ni gastos si no hay recuperación", "Un abogado con licencia en Texas revisa cada solicitud"],
        "fine": "Enviar este formulario no crea una relación abogado-cliente. Por favor no envíe nada que considere muy delicado, como expedientes médicos completos; su abogado se los pedirá de forma segura más adelante.",
        "cases": ["Accidente de auto", "Accidente de camión", "Resbalón y caída", "Lesión médica", "Lesión dental", "Otra cosa"],
        "choose": "Elija una opción",
        "name": "Su nombre", "phone": "Número de celular", "incident": "¿Qué pasó?", "date": "¿Cuándo pasó?",
        "unsure": "No sé la fecha exacta",
        "deadline": "En Texas, el plazo para casos de lesiones suele ser de dos años desde la fecha de la lesión. Envíe esto hoy y un abogado revisará primero el plazo.",
        "county": "Condado de Texas",
        "county_note": "No encontramos ese condado de Texas. Si pasó fuera de Texas, es posible que no podamos ayudar, pero envíelo de todos modos y le diremos.",
        "language": "Idioma preferido", "lang_default": "Español",
        "gov": "¿Hubo un vehículo o una propiedad de una ciudad, condado, estado o escuela involucrados?", "gov_opts": ["Sí", "No", "No sé"],
        "gov_warn": "Los reclamos contra un gobierno pueden tener un plazo de aviso de solo 6 meses, y algunas ciudades fijan plazos más cortos. Envíe esto hoy.",
        "treatment": "¿Ha visto a un médico o dentista por esto?", "treat_opts": ["Sí", "No", "Tengo una cita"],
        "story": "En pocas palabras, ¿qué pasó y cómo se lastimó?",
        "files": "Fotos o documentos", "optional": "(opcional)", "drop": "Agregar fotos o documentos",
        "drop_hint": "Fotos del lugar o de las lesiones, reporte policial, facturas o cartas del seguro. Hasta 10 archivos, 25 MB en total.",
        "insurer": "Compañía de seguros involucrada", "lawyer": "¿Ya tiene un abogado para esto?", "yn": ["No", "Sí"],
        "lawyer_note": "Gracias por decirnos. Un abogado leerá primero su solicitud. No pedimos a quienes ya tienen abogado que cambien; si quiere hablar de cambiar de abogado, díganoslo arriba.",
        "consent": f"Acepto que {FIRM} me contacte sobre mi solicitud por teléfono, mensaje de texto o WhatsApp, y que la tecnología ayude a organizar mi información para que la revise un abogado, como explica la <a href=\"/privacy\" target=\"_blank\" hreflang=\"en\">Política de privacidad</a> (en inglés). Pueden aplicarse tarifas de mensajes y datos. Responda STOP para dejar de recibir mensajes de texto.",
        "send": "Enviar para revisión de un abogado", "sending": "Enviando…", "uploading": "Subiendo archivo {i} de {n}…",
        "draft": "Recuperamos las respuestas que aún no había enviado.", "start_over": "Empezar de nuevo",
        "done_h": "Gracias, {name}.", "done_p": "Recibimos su solicitud. Un abogado con licencia en Texas la revisará.", "ref": "Su número de referencia:",
        "done_steps": ["Le escribiremos al celular que nos dio, con la fecha en que puede esperar una respuesta.",
                       "El abogado revisa lo que envió y puede pedirle algunos datos más.",
                       "Si podemos tomar su caso, verá el nombre y la licencia de Texas de su abogado, y el acuerdo de honorarios, antes de firmar nada."],
        "back": "Volver al inicio", "back_href": "/",
        "msg": {
            "name": "Por favor díganos su nombre.", "phone": "Por favor escriba un número de celular donde podamos contactarle.",
            "incident": "Por favor elija qué pasó.",
            "date": "Por favor escriba la fecha en que pasó (no en el futuro), o marque “No sé la fecha exacta” y dé su mejor cálculo.",
            "county": "Por favor escriba el condado de Texas donde pasó.",
            "government": "Por favor díganos si hubo un vehículo o una propiedad del gobierno involucrados, o elija “No sé”.",
            "treatment": "Por favor díganos si ha visto a un médico o dentista.",
            "story": "Por favor cuéntenos brevemente qué pasó y cómo se lastimó.",
            "consent": "Por favor marque la casilla para que podamos contactarle sobre su solicitud.",
            "not_file": "“{f}” no es una foto ni un PDF.", "too_many": "Puede agregar hasta 10 archivos aquí; su abogado puede pedir más después.",
            "too_big": "“{f}” es demasiado grande para enviarlo aquí (25 MB en total). Su abogado puede pedir archivos más grandes después.",
            "remove": "Quitar", "fail": "Lo sentimos, no pudimos enviar su solicitud en este momento y no se guardó nada. Inténtelo de nuevo en unos minutos.",
            "partial": "Recibimos su solicitud, pero {n} archivo(s) no se subieron. Su abogado se los pedirá.",
        },
    },
}

FORM_CSS = """
.wrap{max-width:1180px;margin:0 auto;padding:40px 32px 72px;display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:56px;align-items:start}
.intro{position:sticky;top:96px}
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
.err{font-size:13px;color:var(--err);margin:0}
.err:empty{display:none}
fieldset{border:0;margin:0;padding:0;min-width:0}
.choices{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px}
.choice{position:relative}
.choice input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}
.choice span{display:inline-flex;align-items:center;min-height:44px;padding:0 18px;border-radius:999px;background:var(--field);border:1.5px solid var(--field);font-weight:600;font-size:15px}
.choice input:checked+span{background:var(--yellow);border-color:var(--yellow)}
.choice input:focus-visible+span{border-color:var(--ink)}
.field.bad .choice span{border-color:var(--err)}
.note{background:var(--field);border-radius:14px;padding:14px 16px;font-size:14px;margin:0}
.consent{display:flex;gap:12px;align-items:flex-start;font-size:14px;line-height:1.5;color:var(--muted);font-weight:400}
.consent input{flex:none;width:22px;height:22px;margin:1px 0 0;accent-color:var(--ink)}
.consent a{color:var(--ink)}
.btn{width:100%;border:0;border-radius:999px;background:var(--yellow);color:var(--ink);min-height:58px;font:600 17px/1 "Instrument Sans",sans-serif;cursor:pointer;transition:transform .15s ease,background .15s}
.btn:hover{background:#f5d800}
.btn:active{transform:scale(.99)}
.btn[disabled]{opacity:.6;cursor:progress}
.formerr{background:#fff6f5;color:var(--err);border-radius:14px;padding:14px 16px;font-size:14px;margin:0}
.formerr:empty{display:none}
.drop{position:relative;display:flex;flex-direction:column;gap:4px;align-items:flex-start;border:1.5px dashed #cfc6ad;border-radius:16px;padding:18px 18px 18px 64px;background:var(--field);cursor:pointer;font-weight:400}
.drop::before{content:"";position:absolute;left:18px;top:50%;width:32px;height:32px;margin-top:-16px;border-radius:50%;background:var(--yellow) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23140c0a' stroke-width='2.4' stroke-linecap='round'%3E%3Cpath d='M12 5v14M5 12h14'/%3E%3C/svg%3E") center/16px no-repeat}
.drop:hover,.drop:focus-within{border-color:var(--ink)}
.drop b{font-weight:600;font-size:15px}
.drop span{font-size:13px;color:var(--muted)}
.drop input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%}
.files{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.files:empty{display:none}
.files li{display:flex;align-items:center;gap:12px;background:var(--egg);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font-size:14px;min-width:0}
.files .fn{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.files .fs{color:var(--muted);font-size:13px;flex:none}
.files button,.draft button{flex:none;border:0;background:none;font:600 13px/1 "Instrument Sans",sans-serif;text-decoration:underline;cursor:pointer;padding:6px;color:var(--ink)}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.hint{font-size:13px;line-height:1.45;color:var(--muted);margin:0}
.warn{background:#fff4d6;border-radius:12px;padding:10px 12px;font-size:13.5px;line-height:1.45;margin:0}
.unsure{display:flex;gap:8px;align-items:center;font-weight:400;font-size:14px;color:var(--muted)}
.unsure input{width:18px;height:18px;margin:0;accent-color:var(--ink)}
.draft{display:flex;align-items:center;justify-content:space-between;gap:12px;background:var(--field);border-radius:12px;padding:10px 14px;font-size:14px;margin:0 0 18px}
.done h2{font:800 40px/1 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.03em;margin:0 0 16px}
.done p{font:500 19px/1.5 "GT Alpina Medium",Georgia,serif;margin:0 0 14px}
.done ol{margin:20px 0 28px;padding-left:22px;display:grid;gap:8px}
.done a.btn{display:inline-flex;align-items:center;justify-content:center;text-decoration:none;width:auto;padding:0 28px}
.ref{display:inline-block;background:var(--field);border-radius:10px;padding:8px 12px;font:600 15px/1 "Instrument Sans",sans-serif;letter-spacing:.04em}
@media(max-width:900px){
  .wrap{grid-template-columns:1fr;gap:28px;padding:20px 20px 56px}
  .intro{position:static}
  .lead{font-size:18px}
}
@media(max-width:560px){
  .card{padding:24px 20px;border-radius:24px}
  .grid{grid-template-columns:1fr}
}
"""

JS = r"""
(function () {
  var S = __STRINGS__, LANG = '__LANG__';
  var form = document.getElementById('case-form'), el = function (n) { return form.elements.namedItem(n); };
  var btn = document.getElementById('send'), formErr = document.getElementById('form-err'), date = document.getElementById('f-date');
  var unsure = document.getElementById('f-unsure'), KEY = '10flat-case-draft-' + LANG;
  var TYPES = { car: 'Car accident', truck: 'Truck accident', fall: 'Slip and fall', medical: 'Medical injury', dental: 'Dental injury', other: 'Something else' };
  var t = new Date(); date.max = t.getFullYear() + '-' + String(t.getMonth() + 1).padStart(2, '0') + '-' + String(t.getDate()).padStart(2, '0');

  var DRAFT = ['name', 'phone', 'incident', 'date', 'county', 'language', 'government', 'treatment', 'story', 'insurer', 'lawyer'];
  var sent = false;
  function saveDraft() {
    if (sent) return;
    try {
      var d = { at: Date.now(), unsure: unsure.checked };
      DRAFT.forEach(function (n) { d[n] = el(n).value; });
      localStorage.setItem(KEY, JSON.stringify(d));
    } catch (e) {}
  }
  function clearDraft() { clearTimeout(draftTimer); try { localStorage.removeItem(KEY); } catch (e) {} }
  var draftTimer;
  form.addEventListener('input', function () { clearTimeout(draftTimer); draftTimer = setTimeout(saveDraft, 400); });
  form.addEventListener('change', function () { clearTimeout(draftTimer); draftTimer = setTimeout(saveDraft, 400); });
  try {
    var d = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (d && Date.now() - d.at < 7 * 864e5 && (d.name || d.story)) {
      DRAFT.forEach(function (n) {
        var f = el(n); if (!f || d[n] == null || d[n] === '') return;
        if (f instanceof RadioNodeList) { [].forEach.call(f, function (r) { r.checked = r.value === d[n]; }); } else f.value = d[n];
      });
      unsure.checked = !!d.unsure;
      var box = document.getElementById('draft'); box.hidden = false;
      document.getElementById('draft-reset').addEventListener('click', function () { clearDraft(); form.reset(); box.hidden = true; refresh(); });
    }
  } catch (e) {}
  var q = new URLSearchParams(location.search).get('type'); if (q && TYPES[q]) el('incident').value = TYPES[q];

  var COUNTIES = [].map.call(document.querySelectorAll('#tx-counties option'), function (o) { return o.value.toLowerCase(); });
  var countyNote = document.getElementById('county-note'), deadline = document.getElementById('deadline-note');
  var govNote = document.getElementById('gov-note'), lawyerNote = document.getElementById('lawyer-note');
  function countyCheck() { var v = el('county').value.trim().toLowerCase().replace(/\s+(county|condado)$/, '').replace(/^condado( de)?\s+/, ''); countyNote.hidden = !v || COUNTIES.indexOf(v) > -1; }
  function deadlineCheck() {
    var v = el('date').value; if (!v || unsure.checked) { deadline.hidden = true; return; }
    var months = (Date.now() - new Date(v + 'T12:00:00').getTime()) / (1000 * 60 * 60 * 24 * 30.44);
    deadline.hidden = months < 20;
  }
  function govCheck() { var g = el('government').value; govNote.hidden = !(g === 'yes' || g === 'unsure'); }
  function lawyerCheck() { lawyerNote.hidden = el('lawyer').value !== 'yes'; }
  function refresh() { countyCheck(); deadlineCheck(); govCheck(); lawyerCheck(); }
  el('county').addEventListener('change', countyCheck); el('county').addEventListener('blur', countyCheck);
  el('date').addEventListener('change', deadlineCheck); el('date').addEventListener('input', deadlineCheck);
  unsure.addEventListener('change', function () { deadlineCheck(); if (form.querySelector('[data-field="date"]').classList.contains('bad')) check(); });
  [].forEach.call(form.querySelectorAll('input[name=government]'), function (r) { r.addEventListener('change', govCheck); });
  [].forEach.call(form.querySelectorAll('input[name=lawyer]'), function (r) { r.addEventListener('change', lawyerCheck); });
  refresh();

  var MAX_FILES = 10, MAX_TOTAL = 25 * 1024 * 1024, CHUNK = 3000000, picked = [], busy = 0;
  var fileIn = document.getElementById('f-files'), fileList = document.getElementById('file-list');
  function kb(n) { return n < 1048576 ? Math.max(1, Math.round(n / 1024)) + ' KB' : (n / 1048576).toFixed(1) + ' MB'; }
  function total() { return picked.reduce(function (a, f) { return a + f.size; }, 0); }
  function okType(f) { return /^image\//.test(f.type) || f.type === 'application/pdf' || /\.(pdf|jpe?g|png|heic|heif|webp)$/i.test(f.name); }
  function shrink(f) {
    if (!/^image\/(jpeg|png|webp|heic|heif)$/.test(f.type) || !window.createImageBitmap) return Promise.resolve(f);
    return createImageBitmap(f).then(function (bmp) {
      var s = Math.min(1, 2000 / Math.max(bmp.width, bmp.height)), c = document.createElement('canvas');
      c.width = Math.round(bmp.width * s); c.height = Math.round(bmp.height * s);
      c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
      return new Promise(function (res) { c.toBlob(function (b) {
        if (!b || b.size >= f.size) return res(f);
        res(new File([b], f.name.replace(/\.[^.]+$/, '') + '.jpg', { type: 'image/jpeg' }));
      }, 'image/jpeg', 0.85); });
    }).catch(function () { return f; });
  }
  function b64(blob) { return new Promise(function (res, rej) { var r = new FileReader(); r.onload = function () { res(String(r.result).split(',')[1]); }; r.onerror = rej; r.readAsDataURL(blob); }); }
  function drawFiles() {
    fileList.innerHTML = '';
    picked.forEach(function (f, i) {
      var li = document.createElement('li'), n = document.createElement('span'), s = document.createElement('span'), x = document.createElement('button');
      n.className = 'fn'; n.textContent = f.name; s.className = 'fs'; s.textContent = kb(f.size);
      x.type = 'button'; x.textContent = S.msg.remove; x.setAttribute('aria-label', S.msg.remove + ' ' + f.name);
      x.addEventListener('click', function () { picked.splice(i, 1); setErr('files', ''); drawFiles(); });
      li.appendChild(n); li.appendChild(s); li.appendChild(x); fileList.appendChild(li);
    });
  }
  fileIn.addEventListener('change', function () {
    var list = [].slice.call(fileIn.files); fileIn.value = ''; var msgs = [];
    list.forEach(function (f) {
      if (!okType(f)) { msgs.push(S.msg.not_file.replace('{f}', f.name)); return; }
      if (picked.length + busy >= MAX_FILES) { msgs.push(S.msg.too_many); return; }
      busy++;
      shrink(f).then(function (g) {
        busy--;
        if (total() + g.size > MAX_TOTAL) { setErr('files', S.msg.too_big.replace('{f}', f.name)); return; }
        picked.push(g); drawFiles();
      });
    });
    setErr('files', msgs.filter(function (m, i) { return msgs.indexOf(m) === i; }).join(' '));
  });

  function setErr(name, msg) {
    var f = form.querySelector('[data-field="' + name + '"]'); if (!f) return;
    f.classList.toggle('bad', !!msg);
    var e = f.querySelector('.err'); if (e) e.textContent = msg || '';
  }
  function check() {
    var bad = [];
    var v = {
      name: el('name').value.trim(), phone: el('phone').value.trim(), incident: el('incident').value, date: el('date').value,
      county: el('county').value.trim(), government: el('government').value, treatment: el('treatment').value,
      story: el('story').value.trim(), consent: el('consent').checked
    };
    var digits = v.phone.replace(/[^0-9]/g, '');
    var ok = {
      name: v.name.length >= 2, phone: digits.length >= 10 && digits.length <= 15, incident: !!v.incident,
      date: (!!v.date && v.date <= date.max) || (unsure.checked && (!v.date || v.date <= date.max)), county: v.county.length >= 2,
      government: !!v.government, treatment: !!v.treatment, story: v.story.length >= 10, consent: v.consent
    };
    Object.keys(ok).forEach(function (k) { setErr(k, ok[k] ? '' : S.msg[k]); if (!ok[k]) bad.push(k); });
    return bad;
  }
  form.addEventListener('input', function (e) { var f = e.target.closest('[data-field]'); if (f && f.classList.contains('bad')) check(); });
  form.addEventListener('change', function (e) { var f = e.target.closest('[data-field]'); if (f && f.classList.contains('bad')) check(); });

  function post(url, body) {
    return fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, body: j }; }); });
  }
  function uploadAll(ref, token) {
    var failed = 0;
    return picked.reduce(function (p, f, fi) {
      return p.then(function () {
        btn.textContent = S.uploading.replace('{i}', fi + 1).replace('{n}', picked.length);
        var chunks = Math.max(1, Math.ceil(f.size / CHUNK));
        var seq = Promise.resolve(true);
        for (var ci = 0; ci < chunks; ci++) (function (ci) {
          seq = seq.then(function (good) {
            if (!good) return false;
            return b64(f.slice(ci * CHUNK, Math.min(f.size, (ci + 1) * CHUNK))).then(function (data) {
              var body = { ref: ref, token: token, file: fi, name: f.name, type: f.type || 'application/octet-stream', chunk: ci, chunks: chunks, data: data };
              return post('/api/intake-file', body).then(function (r) { return r.status === 200 && r.body.ok ? true : post('/api/intake-file', body).then(function (r2) { return r2.status === 200 && r2.body.ok; }); });
            });
          });
        })(ci);
        return seq.then(function (good) { if (!good) failed++; }, function () { failed++; });
      });
    }, Promise.resolve()).then(function () { return failed; });
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault(); formErr.textContent = '';
    var bad = check();
    if (bad.length) { var first = form.querySelector('[data-field="' + bad[0] + '"] input, [data-field="' + bad[0] + '"] select, [data-field="' + bad[0] + '"] textarea'); if (first) first.focus(); return; }
    var data = {
      name: el('name').value.trim(), phone: el('phone').value.trim(), incident: el('incident').value, date: el('date').value,
      dateUnsure: unsure.checked, county: el('county').value.trim(), language: el('language').value, government: el('government').value,
      treatment: el('treatment').value, insurer: el('insurer').value.trim(), story: el('story').value.trim(), hasLawyer: el('lawyer').value === 'yes',
      consent: true, company: el('company').value, page: location.pathname, filesExpected: picked.length,
      fileNames: picked.map(function (f) { return f.name; })
    };
    btn.disabled = true; btn.textContent = S.sending;
    (function wait() { return busy ? new Promise(function (r) { setTimeout(r, 150); }).then(wait) : Promise.resolve(); })()
      .then(function () { data.filesExpected = picked.length; data.fileNames = picked.map(function (f) { return f.name; }); return post('/api/intake', data); })
      .then(function (res) {
        if (!(res.status === 200 && res.body.ok)) throw new Error(res.status);
        sent = true; clearDraft();
        return (picked.length && res.body.upload ? uploadAll(res.body.ref, res.body.upload) : Promise.resolve(0)).then(function (failed) {
          document.getElementById('done-name').textContent = data.name.split(/\s+/)[0];
          document.getElementById('done-ref').textContent = res.body.ref || '';
          var pf = document.getElementById('done-files'); pf.hidden = !failed; pf.textContent = failed ? S.msg.partial.replace('{n}', failed) : '';
          window.track && track('form_sent', { type: data.incident, lang: LANG });
          form.hidden = true; document.getElementById('draft').hidden = true;
          var d = document.getElementById('done'); d.hidden = false; d.focus();
          window.scrollTo({ top: 0, behavior: 'smooth' });
        });
      })
      .catch(function () { formErr.textContent = S.msg.fail; btn.disabled = false; btn.textContent = S.send; });
  });
})();
"""


def field(name, label, control, full=False, optional=None):
    opt = f' <span class="opt">{optional}</span>' if optional else ""
    return (f'<div class="field{" full" if full else ""}" data-field="{name}">'
            f'<label for="f-{name}">{label}{opt}</label>{control}'
            f'<p class="err" id="e-{name}" aria-live="polite"></p></div>')


def radios(name, legend, options, full=True, checked=None, extra=""):
    items = "".join(
        f'<label class="choice"><input type="radio" name="{name}" value="{v}"{" checked" if v == checked else ""}><span>{t}</span></label>'
        for v, t in options)
    return (f'<fieldset class="field{" full" if full else ""}" data-field="{name}"><legend class="legend">{legend}</legend>'
            f'<div class="choices">{items}</div>{extra}<p class="err" id="e-{name}" aria-live="polite"></p></fieldset>')


def build_form(lang):
    s = T[lang]
    case_opts = f'<option value="">{s["choose"]}</option>' + "".join(
        f'<option value="{escape(v)}">{escape(lab)}</option>' for v, lab in zip(CASE_TYPES, s["cases"]))
    langs = "".join(f'<option{" selected" if o == s["lang_default"] else ""}>{o}</option>' for o in ("English", "Español"))
    form = "".join([
        field("name", s["name"], '<input type="text" id="f-name" name="name" autocomplete="name" maxlength="100" aria-describedby="e-name">'),
        field("phone", s["phone"], '<input type="tel" id="f-phone" name="phone" autocomplete="tel" inputmode="tel" maxlength="30" aria-describedby="e-phone">'),
        field("incident", s["incident"], f'<select id="f-incident" name="incident" aria-describedby="e-incident">{case_opts}</select>'),
        field("date", s["date"], '<input type="date" id="f-date" name="date" aria-describedby="e-date">'
              f'<label class="unsure"><input type="checkbox" id="f-unsure" name="unsure"> {s["unsure"]}</label>'
              f'<p class="warn" id="deadline-note" hidden>{s["deadline"]}</p>'),
        field("county", s["county"], '<input type="text" id="f-county" name="county" list="tx-counties" autocomplete="off" maxlength="60" aria-describedby="e-county">'
              '<datalist id="tx-counties">' + "".join(f'<option value="{c}">' for c in COUNTIES) + '</datalist>'
              f'<p class="hint" id="county-note" hidden>{s["county_note"]}</p>'),
        field("language", s["language"], f'<select id="f-language" name="language">{langs}</select>'),
        radios("government", s["gov"], list(zip(("yes", "no", "unsure"), s["gov_opts"])),
               extra=f'<p class="warn" id="gov-note" hidden style="margin-top:10px">{s["gov_warn"]}</p>'),
        radios("treatment", s["treatment"], list(zip(("yes", "no", "scheduled"), s["treat_opts"]))),
        field("story", s["story"], '<textarea id="f-story" name="story" maxlength="4000" aria-describedby="e-story"></textarea>', full=True),
        (f'<div class="field full" data-field="files"><span class="legend">{s["files"]} <span class="opt">{s["optional"]}</span></span>'
         f'<label class="drop" for="f-files"><input type="file" id="f-files" multiple accept="image/*,application/pdf,.heic,.heif" aria-describedby="e-files">'
         f'<b>{s["drop"]}</b><span>{s["drop_hint"]}</span></label>'
         '<ul class="files" id="file-list"></ul><p class="err" id="e-files" aria-live="polite"></p></div>'),
        field("insurer", s["insurer"], '<input type="text" id="f-insurer" name="insurer" maxlength="100">', full=True, optional=s["optional"]),
        radios("lawyer", s["lawyer"], list(zip(("no", "yes"), s["yn"])), checked="no"),
        f'<p class="note full" id="lawyer-note" hidden>{s["lawyer_note"]}</p>',
        f'<div class="field full" data-field="consent"><label class="consent"><input type="checkbox" id="f-consent" name="consent" aria-describedby="e-consent">'
        f'<span>{s["consent"]}</span></label><p class="err" id="e-consent" aria-live="polite"></p></div>',
        '<div class="hp" aria-hidden="true"><label for="f-company">Company</label><input type="text" id="f-company" name="company" tabindex="-1" autocomplete="off"></div>',
        '<p class="formerr full" id="form-err" role="alert"></p>',
        f'<div class="full"><button type="submit" class="btn" id="send">{s["send"]}</button></div>',
    ])
    strings = {k: s[k] for k in ("send", "sending", "uploading", "msg")}
    js = JS.replace("__STRINGS__", json.dumps(strings, ensure_ascii=False)).replace("__LANG__", lang)
    top = nav(start_button=False, lang_link=("/es/start", "Español", "es")) if lang == "en" else nav_es()
    page = head(s["title"], s["desc"], s["path"], FORM_CSS, lang=lang) + f"""
<body>
{top}
<main class="wrap" id="main">
  <section class="intro" aria-labelledby="h">
    <h1 id="h">{s['h1']}</h1>
    <p class="lead">{s['lead']}</p>
    <ul class="points">{''.join(f'<li>{p}</li>' for p in s['points'])}</ul>
    <p class="fine">{s['fine']}</p>
  </section>
  <section class="card" aria-label="{s['title']}">
    <p class="draft" id="draft" hidden><span>{s['draft']}</span><button type="button" id="draft-reset">{s['start_over']}</button></p>
    <form id="case-form" class="grid" novalidate>{form}</form>
    <div class="done" id="done" hidden tabindex="-1">
      <h2>{s['done_h'].replace('{name}', '<span id="done-name"></span>')}</h2>
      <p>{s['done_p']}</p>
      <p>{s['ref']} <span class="ref" id="done-ref"></span></p>
      <p class="warn" id="done-files" hidden></p>
      <ol>{''.join(f'<li>{x}</li>' for x in s['done_steps'])}</ol>
      <a class="btn" href="{s['back_href']}">{s['back']}</a>
    </div>
  </section>
</main>
{footer() if lang == 'en' else footer_es()}
<script>{js}</script>
</body>
</html>
"""
    finalize(page, s["out"])
    print(f"built site/{s['out']}")


DOC_CSS = """
.doc{max-width:760px;margin:0 auto;padding:40px 32px 72px}
.doc h1{margin-bottom:12px}
.doc .updated{font-size:14px;color:var(--muted);margin:0 0 36px}
.doc h2{font:800 26px/1.1 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.02em;margin:40px 0 12px}
.doc p,.doc li{font-size:17px;line-height:1.65}
.doc p{margin:0 0 14px}
.doc ul{margin:0 0 14px;padding-left:22px;display:grid;gap:8px}
.doc a{text-underline-offset:3px}
@media(max-width:900px){.doc{padding:24px 20px 56px}.doc h2{font-size:22px}}
"""


def build_legal():
    from legal_content import PRIVACY, TERMS, UPDATED
    for slug, title, desc, body in (
        ("privacy", "Privacy Policy", f"How {FIRM} collects, uses and protects the information you send through this website.", PRIVACY),
        ("terms", "Terms of Use", f"The terms for using the {FIRM} website.", TERMS),
    ):
        page = (head(title, desc, f"/{slug}", DOC_CSS) + "\n<body>\n" + nav() + "\n"
                f'<main class="doc" id="main"><h1>{title}</h1><p class="updated">Last updated {UPDATED}</p>{body}</main>\n'
                f"{footer()}\n</body>\n</html>\n")
        finalize(page, f"{slug}/index.html")
        print(f"built site/{slug}/index.html")


def build():
    build_form("en")
    build_form("es")
    build_legal()


if __name__ == "__main__":
    build()
