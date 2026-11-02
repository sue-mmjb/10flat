"""Build the home page (site/index.html), the branded 404 page, robots.txt and sitemap.xml.

Rebuilt on 3 Nov 2026 from the website review of 2 Nov ("10Flat Website Review", Chandana): nine blocks instead of
twelve, the calculator in the first screen, one H1, one copy of every element, no video, no stock photos, no quote
cards signed by the firm, no scroll-driven card stacks, three font families, alt text on every image, a link-preview
image and a favicon. The old Framer clone is kept at /classic (tools/build_clone.py) for comparison.

Shares its head, navigation, fonts and base styles with the /start, /privacy and /terms pages (tools/build_start.py).
The fee is 10% of the total amount recovered at every stage (platform SOW v2.0, 3 Nov 2026).
"""
import json
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site import CONFIG, FAQ_GROUPS, SCHEMA, sync_schema_faq  # noqa: E402
from build_start import CSS, FIRM, FONTS, head, nav  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# Case types for the calculator: an example cost share (and minimum) and what the attorney will ask for.
# The cost figures are examples the client can change; they are labelled that way on the page.
CASE_TYPES = [
    ("car", "Car", 0.05, 500, ["Crash report, if there is one", "Photos of the vehicles and your injuries", "Your insurance and the other driver’s", "Medical bills so far"]),
    ("truck", "Truck", 0.07, 1500, ["Crash report", "Photos of the scene and the truck", "The trucking company’s name, if you know it", "Medical bills so far"]),
    ("fall", "Slip and fall", 0.05, 500, ["Photos of where it happened", "Any incident report you were given", "Names of witnesses", "Medical bills so far"]),
    ("medical", "Medical", 0.12, 5000, ["Names of the doctors and hospitals", "Dates of treatment", "Any records or letters you have", "Bills so far"]),
    ("dental", "Dental", 0.10, 3000, ["The dentist’s name and office", "Dates of treatment", "X-rays or records you have", "Bills so far"]),
    ("other", "Other", 0.05, 500, ["Photos", "Any reports or letters", "Medical bills so far"]),
]

HOME_CSS = r"""
html{scroll-padding-top:84px}
@media(prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.sec{padding:96px 32px}
.in{max-width:1180px;margin:0 auto}
.h2{font:800 clamp(34px,4.2vw,56px)/1 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.03em;margin:0 0 20px}
.h3{font:800 26px/1.1 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.02em;margin:0 0 10px}
.body{font:500 19px/1.55 "GT Alpina Medium",Georgia,serif;margin:0 0 16px;max-width:640px}
.yellow{background:var(--yellow)}
.cream{background:var(--egg)}
.paper{background:var(--field)}
.btns{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}
.b1,.b2{display:inline-flex;align-items:center;justify-content:center;min-height:56px;padding:0 28px;border-radius:999px;font:600 17px/1 "Instrument Sans",sans-serif;text-decoration:none;border:2px solid var(--ink);cursor:pointer}
.b1{background:var(--ink);color:var(--yellow)}
.b1:hover{background:#2c211d}
.b2{background:transparent;color:var(--ink)}
.b2:hover{background:rgba(20,12,10,.06)}
.ticks{list-style:none;margin:24px 0 0;padding:0;display:grid;gap:10px}
.ticks li{display:flex;gap:12px;align-items:flex-start;font-weight:600;font-size:17px}
.ticks li::before{content:"";flex:none;width:24px;height:24px;margin-top:-1px;border-radius:50%;background:var(--ink) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23ffe435' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 12.5l4 4 8-9'/%3E%3C/svg%3E") center/14px no-repeat}

/* hero */
.hero{padding:32px 32px 72px}
.hero .in{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,460px);gap:64px;align-items:center}
.hero h1{font-size:clamp(52px,7.4vw,104px);line-height:.92;margin:0 0 24px}
.hero .body{font-size:21px}

/* calculator */
.calc{background:var(--white);border-radius:28px;padding:22px 26px;box-shadow:0 30px 70px -36px rgba(20,12,10,.45)}
.calc .lbl{font-size:14px;color:var(--muted);margin:0}
.big{font:800 50px/1 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.03em;margin:6px 0 4px;font-variant-numeric:tabular-nums}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 0}
.tags span{background:var(--field);border-radius:8px;padding:6px 10px;font-size:13px;font-weight:600}
.cblk{border-top:1px solid var(--line);margin-top:14px;padding-top:12px}
.types{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;background:var(--field);border-radius:20px;padding:4px;margin-top:10px}
.types button{border:0;background:transparent;border-radius:16px;min-height:36px;font:600 14px/1 "Instrument Sans",sans-serif;color:var(--ink);cursor:pointer}
.types button[aria-pressed=true]{background:var(--yellow)}
.types button:focus-visible{outline:2px solid var(--ink);outline-offset:-2px}
.amt{display:flex;justify-content:space-between;align-items:center;gap:12px}
.amt label{font-size:14px;color:var(--muted);font-weight:400}
.calc input.money{width:150px;text-align:right;border:0;border-bottom:1.5px dashed #cfc6ad;background:transparent;font:700 24px/1.2 "Instrument Sans",sans-serif;color:var(--ink);padding:2px 0;border-radius:0;min-height:0}
.calc input.money.sm{width:110px;font-size:16px;font-weight:600}
.calc input.money:focus{outline:none;border-bottom-color:var(--ink);background:transparent}
input[type=range]{width:100%;margin:10px 0 0;accent-color:var(--ink);height:28px}
.rows{display:grid;gap:6px}
.row{display:flex;justify-content:space-between;align-items:center;gap:12px;font-size:15px}
.row .v{font-weight:600;font-variant-numeric:tabular-nums}
.row.dim .v{color:var(--muted)}
.row.keep{font-size:17px;font-weight:600;border-top:1px solid var(--line);padding-top:10px;margin-top:4px}
.row label{font-weight:400;font-size:15px}
.cmsg{font-size:13px;color:var(--err);margin:8px 0 0}
.cmsg:empty{display:none}
.need{font-size:12.5px;line-height:1.45;color:var(--muted);margin:10px 0 0}
.need b{color:var(--ink)}
.cact{display:grid;grid-template-columns:1fr auto;gap:10px;margin-top:14px}
.cact .b1{min-height:52px;font-size:16px}
.share{display:inline-flex;align-items:center;gap:8px;min-height:52px;padding:0 16px;border-radius:999px;border:2px solid var(--line);font:600 14px/1 "Instrument Sans",sans-serif;text-decoration:none;color:var(--ink)}
.share:hover{border-color:var(--ink)}
.cfine{font-size:11.5px;line-height:1.45;color:var(--muted);margin:10px 0 0}

/* how it works */
.steps{display:grid;grid-template-columns:1fr;gap:0;margin-top:40px;list-style:none;padding:0}
.steps::after{content:"";display:block;height:26vh}   /* room inside the sticky area, so the finished stack holds for a moment */
.steps li{position:sticky;top:calc(var(--stack-top,88px) + var(--i) * 16px);margin-bottom:40px;border-radius:32px;
  box-shadow:0 -12px 34px -20px rgba(20,12,10,.4);transform-origin:50% 0;will-change:transform;
  display:grid;grid-template-columns:minmax(0,1fr) minmax(0,380px);grid-template-rows:auto auto auto;column-gap:56px;align-content:center;
  min-height:min(480px,calc(100vh - 220px));padding:56px 64px}
.steps li:last-child{margin-bottom:0}
.steps li.c1{background:#ffe435}
.steps li.c2{background:#b8d63a}
.steps li.c3{background:#f4b0d8}
.steps img{grid-column:2;grid-row:1/4;align-self:center;width:100%;height:auto;aspect-ratio:320/220;object-fit:contain;margin:0}
.steps .num{grid-column:1;justify-self:start;background:var(--ink);color:#fff;margin-bottom:16px}
.steps .h3{grid-column:1;font-size:clamp(30px,3.2vw,44px);margin-bottom:14px}
.steps p{grid-column:1;margin:0;font-size:18px;line-height:1.6;max-width:560px}
.num{display:inline-flex;width:34px;height:34px;border-radius:50%;background:var(--yellow);align-items:center;justify-content:center;font-weight:700;margin-bottom:12px}

/* why 10% */
.compare{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:36px}
.col{border-radius:24px;padding:28px}
.col.them{background:var(--white)}
.col.us{background:var(--yellow)}
.col ul{margin:0;padding-left:20px;display:grid;gap:8px;font-size:17px}
.money-box{margin-top:24px;background:var(--ink);color:#fff;border-radius:24px;padding:28px 32px;display:grid;grid-template-columns:auto 1fr;gap:24px;align-items:start}
.money-box .h3{color:var(--yellow);margin:0}
.money-box p{margin:0;font-size:17px;line-height:1.6;color:#efe9da}

/* phone preview */
.phone-sec .in{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,400px);gap:64px;align-items:center}
.phone{background:var(--ink);border-radius:44px;padding:14px;max-width:380px;margin:0 auto;box-shadow:0 30px 70px -36px rgba(20,12,10,.6)}
.screen{background:var(--egg);border-radius:32px;padding:22px 18px;display:grid;gap:10px}
.app-h{display:flex;align-items:center;gap:10px}
.av{width:36px;height:36px;border-radius:50%;background:var(--yellow);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
.app-h b{display:block;font-size:15px}
.app-h span{font-size:12px;color:var(--muted)}
.tile{background:var(--white);border-radius:16px;padding:12px 14px;font-size:13px}
.tile b{display:block;font-size:14px;margin-bottom:2px}
.tile .muted{color:var(--muted)}
.offer{background:var(--white);border:2px solid var(--ink);border-radius:16px;padding:14px;font-size:13px}
.offer .r{display:flex;justify-content:space-between;padding:2px 0}
.offer .r.t{font-weight:700;border-top:1px solid var(--line);margin-top:4px;padding-top:6px}
.offer .acts{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:10px}
.offer .acts span{text-align:center;border-radius:999px;padding:8px 6px;font-weight:600;font-size:12px;border:1.5px solid var(--ink)}
.offer .acts span:first-child{background:var(--yellow);border-color:var(--yellow)}
.preview{font-size:12px;color:var(--muted);text-align:center;margin:12px 0 0}

/* promises */
.prom{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:36px;list-style:none;padding:0}
.prom li{background:var(--white);border-radius:20px;padding:22px 24px;font-size:16px;line-height:1.5}
.prom b{display:block;font:800 21px/1.15 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.01em;margin-bottom:6px}

/* faq */
.faq{max-width:820px;margin:32px 0 0}
.faq details{border-bottom:1px solid var(--line)}
.faq summary{list-style:none;cursor:pointer;padding:20px 44px 20px 0;position:relative;font-weight:600;font-size:18px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";position:absolute;right:6px;top:50%;transform:translateY(-50%);font-size:26px;font-weight:400}
.faq details[open] summary::after{content:"–"}
.faq p{margin:0 0 20px;font-size:17px;line-height:1.6;max-width:720px}

/* closing */
.close .in{text-align:center}
.close .h2{max-width:900px;margin:0 auto 14px}
.gavel{display:block;width:min(520px,100%);height:auto;aspect-ratio:854/480;margin:-24px auto 4px;mix-blend-mode:darken}
.close .body{margin:0 auto}
.close .btns{justify-content:center}

/* phone bar */
.mbar{display:none}
@media(max-width:1020px){
  .hero .in,.phone-sec .in{grid-template-columns:1fr;gap:40px}
  .calc{max-width:520px}
}
@media(max-width:1100px){
  .steps li{grid-template-columns:minmax(0,1fr) minmax(0,260px);column-gap:32px;padding:44px 40px}
}
@media(max-width:860px){
  .prom{grid-template-columns:1fr}
  .steps li{top:calc(var(--stack-top,76px) + var(--i) * 14px);display:flex;flex-direction:column;align-content:normal;
    min-height:min(560px,calc(100svh - 190px));margin-bottom:32px;padding:28px 26px 30px;border-radius:28px}
  .steps img{max-height:220px;margin:0 0 22px}
  .steps .h3{font-size:26px;margin-bottom:10px}
  .steps p{font-size:16px;line-height:1.55}
  .compare{grid-template-columns:1fr}
  .money-box{grid-template-columns:1fr;gap:10px}
}
@media(max-width:760px){
  .sec{padding:64px 20px}
  .hero{padding:28px 20px 56px}
  .hero h1{font-size:clamp(48px,14vw,72px)}
  .hero .body{font-size:17px;margin-bottom:0}
  .hero .ticks,.hero .btns{display:none}  /* on phones the sticky bar carries the buttons; the promises repeat below */
  .hero .in{gap:24px}
  .calc{padding:22px 18px;border-radius:24px}
  .big{font-size:46px}
  .cact{grid-template-columns:1fr}
  .share{justify-content:center}
  .mbar{display:grid;grid-template-columns:auto 1fr;gap:8px;position:fixed;left:0;right:0;bottom:0;z-index:30;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:rgba(247,245,239,.97);border-top:1px solid var(--line)}
  .mbar a{min-height:50px;font-size:16px}
  body{padding-bottom:76px}
}
"""

GAVEL_JS = r"""
(function () {
  // The gavel clip (0.5 MB) loads when it nears the screen, on phones too (Sue, 3 Nov 2026); reduced motion keeps the still.
  var v = document.querySelector('.gavel'); if (!v || !('IntersectionObserver' in window)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (e.isIntersecting) { if (!v.src) v.src = v.dataset.src; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
      else if (v.src) v.pause();
    });
  }, { rootMargin: '300px 0px' }).observe(v);
})();
"""

STACK_JS = r"""
(function () {
  // Stacked step cards: as the next card slides over, the covered one shrinks a little (like the reference).
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var cards = [].slice.call(document.querySelectorAll('.steps li')), ticking = false;
  var nav = document.querySelector('.nav');
  function setTop() { document.documentElement.style.setProperty('--stack-top', ((nav ? nav.getBoundingClientRect().height : 64) + 12) + 'px'); }
  function update() {
    ticking = false;
    cards.forEach(function (c, i) {
      if (reduce.matches || i === cards.length - 1) { c.style.transform = ''; return; }
      var r = c.getBoundingClientRect(), n = cards[i + 1].getBoundingClientRect();
      var covered = Math.min(1, Math.max(0, (r.bottom - n.top) / r.height));
      c.style.transform = 'scale(' + (1 - (window.innerWidth > 860 ? 0.04 : 0.06) * covered).toFixed(4) + ')';
    });
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
  setTop(); update();
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', function () { setTop(); onScroll(); });
})();
"""

CALC_JS = r"""
(function () {
  var TYPES = __TYPES__;
  var RATE = 0.10, TYPICAL = 0.33, MIN = 1000, MAX = 100000000, SMIN = 1000, SMAX = 10000000;
  var c = document.getElementById('calculator'); if (!c) return;
  var $ = function (s) { return c.querySelector(s); };
  var amountIn = $('#c-amount'), range = $('#c-range'), costsIn = $('#c-costs'), liensIn = $('#c-liens'), msg = $('#c-msg');
  var state = { type: 'car', amount: 100000, costs: null, liens: 0 };
  function money(n) { return '$' + Math.round(n).toLocaleString('en-US'); }
  function parse(v) { var d = String(v).replace(/[^0-9]/g, ''); return d ? Number(d) : NaN; }
  function autoCosts(a) { var t = TYPES[state.type]; return Math.min(a, Math.max(t.min, Math.round(a * t.share / 500) * 500)); }
  function toRange(a) { return Math.round(Math.log10(Math.min(SMAX, Math.max(SMIN, a)) / SMIN) / Math.log10(SMAX / SMIN) * 1000); }
  function fromRange(v) {
    var a = SMIN * Math.pow(SMAX / SMIN, v / 1000), step = a < 10000 ? 100 : a < 100000 ? 1000 : a < 1000000 ? 5000 : 50000;
    return Math.round(a / step) * step;
  }
  function set(id, v) { var e = c.querySelector('[data-out="' + id + '"]'); if (e) e.textContent = v; }
  function render() {
    var a = state.amount, costs = state.costs == null ? autoCosts(a) : state.costs, liens = state.liens;
    var fee = a * RATE, fee33 = a * TYPICAL, left = a - fee - costs - liens;
    set('more', money(fee33 - fee)); set('fee', money(fee)); set('fee33', money(fee33)); set('keep', money(Math.max(0, left)));
    set('amount-label', money(a));
    if (document.activeElement !== costsIn) costsIn.value = money(costs);
    if (document.activeElement !== liensIn) liensIn.value = money(liens);
    if (document.activeElement !== amountIn) amountIn.value = money(a);
    range.value = toRange(a); range.setAttribute('aria-valuetext', money(a));
    msg.textContent = left < 0 ? 'Those costs and bills are more than the settlement after our fee. Every case is different; your attorney goes through the numbers with you before anything is decided.' : '';
    var t = TYPES[state.type];
    $('#c-need').innerHTML = '<b>What we’ll ask you for:</b> ' + t.need.join(' · ');
    $('#c-start').href = '/start?type=' + state.type;
    var text = 'At ' + c.dataset.firm + ' the injury fee is 10%, even at trial. On a ' + money(a) + ' settlement that is ' + money(fee33 - fee) + ' more for the client than a one-third fee. ' + location.origin + '/';
    $('#c-share').href = 'https://wa.me/?text=' + encodeURIComponent(text);
  }
  [].forEach.call(c.querySelectorAll('.types button'), function (b) {
    b.addEventListener('click', function () {
      [].forEach.call(c.querySelectorAll('.types button'), function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      state.type = b.dataset.type; state.costs = null; render(); window.track && track('calc_type', { type: state.type });
    });
  });
  range.addEventListener('input', function () { state.amount = fromRange(Number(range.value)); render(); });
  range.addEventListener('change', function () { window.track && track('calc_amount'); });
  amountIn.addEventListener('input', function () {
    var n = parse(amountIn.value);
    if (isNaN(n)) return;
    if (n < MIN) { msg.textContent = 'Enter a settlement of at least $1,000.'; return; }
    state.amount = Math.min(MAX, n); render();
  });
  amountIn.addEventListener('blur', function () { amountIn.value = money(state.amount); if (msg.textContent.indexOf('at least') > -1) msg.textContent = ''; });
  costsIn.addEventListener('input', function () { var n = parse(costsIn.value); state.costs = isNaN(n) ? null : n; render(); });
  liensIn.addEventListener('input', function () { var n = parse(liensIn.value); state.liens = isNaN(n) ? 0 : n; render(); });
  [costsIn, liensIn].forEach(function (i) { i.addEventListener('blur', render); });
  $('#c-share').addEventListener('click', function () { window.track && track('calc_share_whatsapp'); });
  $('#c-start').addEventListener('click', function () { window.track && track('start_click', { from: 'calculator', type: state.type }); });
  render();
})();
"""


def money(n):
    return "$" + f"{round(n):,}"


def calculator():
    t0 = CASE_TYPES[0]
    a, costs = 100000, max(t0[3], round(100000 * t0[2] / 500) * 500)
    types = "".join(f'<button type="button" data-type="{k}" aria-pressed="{str(i == 0).lower()}">{label}</button>'
                    for i, (k, label, *_r) in enumerate(CASE_TYPES))
    return f"""
<div class="calc" id="calculator" data-firm="{FIRM}" aria-labelledby="calc-h">
  <h2 class="sr" id="calc-h">Fee calculator</h2>
  <p class="lbl">You keep this much more than with a one-third fee</p>
  <p class="big" data-out="more" aria-live="polite">{money(a * 0.23)}</p>
  <div class="tags"><span>10% of the settlement</span><span>Stays 10% at trial</span></div>
  <div class="cblk"><p class="lbl" id="types-l">Case type</p><div class="types" role="group" aria-labelledby="types-l">{types}</div></div>
  <div class="cblk">
    <div class="amt"><label for="c-amount">If your case settles for</label><input class="money" id="c-amount" type="text" inputmode="numeric" value="{money(a)}" autocomplete="off"></div>
    <input id="c-range" type="range" min="0" max="1000" step="1" value="500" aria-label="Settlement amount" aria-valuetext="{money(a)}">
  </div>
  <div class="cblk rows">
    <div class="row dim"><span>Fee at a one-third (33%) firm</span><span class="v" data-out="fee33">{money(a * 0.33)}</span></div>
    <div class="row"><span>Our fee (10%)</span><span class="v" data-out="fee">{money(a * 0.10)}</span></div>
    <div class="row"><label for="c-costs">Case costs (example, change it)</label><input class="money sm" id="c-costs" type="text" inputmode="numeric" value="{money(costs)}" autocomplete="off"></div>
    <div class="row"><label for="c-liens">Medical bills and liens (optional)</label><input class="money sm" id="c-liens" type="text" inputmode="numeric" value="$0" autocomplete="off"></div>
    <div class="row keep"><span>You keep</span><span class="v" data-out="keep">{money(a - a * 0.10 - costs)}</span></div>
  </div>
  <p class="cmsg" id="c-msg" role="status"></p>
  <p class="need" id="c-need"><b>What we’ll ask you for:</b> {' · '.join(t0[4])}</p>
  <div class="cact"><a class="b1" id="c-start" href="/start?type=car">Start your case</a><a class="share" id="c-share" href="https://wa.me/?text=" target="_blank" rel="noopener">Share on WhatsApp</a></div>
  <p class="cfine">An illustration, not a prediction of what your case is worth. Both fees are figured on the full settlement; case costs, medical bills and liens are paid from your share the same way at any firm.</p>
</div>"""


STEPS = [
    ("step-1.webp", "Drawing of a phone sending photos and documents, next to a speech bubble with an exclamation and question mark.",
     "Tell us what happened.",
     "Send your case with our short online form, with any photos or documents you have. A licensed Texas attorney reviews every case, and we tell you when to expect an answer. You meet your attorney before you sign anything."),
    ("step-2.webp", "Drawing of document folders being stacked into a folder labelled Case by a small crane.",
     "We build your case.",
     "Our software organizes your records, requests what’s missing, builds a timeline of your treatment, totals your bills and tracks every deadline. A trained case team checks the work."),
    ("step-3.webp", "Drawing of the scales of justice, a briefcase and a bag of money tied with a ribbon, moving forward.",
     "We pursue your recovery.",
     "Your attorney reviews your case, advises you and negotiates with the insurance company. Nothing goes to the insurer or a court without your attorney’s approval, and you decide every offer. If the insurer won’t make a fair offer, we file a lawsuit, and your fee stays 10%."),
]

PROMISES = [
    ("No fee without a recovery.", "If we don’t recover money for you, you owe no fee and no case costs."),
    ("10% at every stage.", "Settled early or decided at trial, the fee stays 10%."),
    ("We advance the costs.", "Records, reports and filing fees are on us until the case resolves, repaid at cost with no markup."),
    ("No admin fees.", "No file fees, no technology fees. The 10% and the actual costs are the only deductions."),
    ("You decide every offer.", "Your attorney advises you; settling, countering or going on is your call."),
    ("A lawyer signs off.", "Nothing reaches an insurer or a court without your attorney’s approval."),
]


def faq_html():
    items = [i for g in FAQ_GROUPS for i in g["items"]]
    return "".join(f'<details><summary>{escape(i["q"])}</summary><p>{escape(i["a"])}</p></details>' for i in items), len(items)


FOOT_TEXT = (
    f"{FIRM} PLLC, Texas, a law firm owned only by licensed attorneys. Our fee is 10% of the total amount recovered at every "
    "stage, including trial; case costs and liens are paid from your share after the fee. If there is no recovery, you owe no "
    "fee and no case costs. Every case is different, and past results do not guarantee future results. "
    f"{FIRM} uses software, including AI, and a supervised case team to prepare work; a licensed attorney reviews and approves "
    "legal work. The software company, 10flat Technologies, is paid a fixed fee and never shares in a recovery or a fee. "
    "Contacting us does not create an attorney-client relationship until a fee agreement is signed. Attorney advertising. "
    "Fee comparisons use a one-third (33%) fee, common for Texas injury cases. The calculator is an illustration, not a promise of any outcome."
)


def footer():
    return (f'<footer><p>{escape(FOOT_TEXT)}</p><p class="flinks"><a href="/privacy">Privacy</a><a href="/terms">Terms</a>'
            f'<span>© 2026 {FIRM}. All rights reserved.</span></p></footer>')


def build_home():
    sync_schema_faq()
    schema = re.search(r'<script type="application/ld\+json">.*?</script>', SCHEMA.read_text(encoding="utf-8"), re.S).group(0)
    faq, n_faq = faq_html()
    types_js = json.dumps({k: {"label": l, "share": s, "min": m, "need": need} for k, l, s, m, need in CASE_TYPES}, ensure_ascii=False)
    steps = "".join(
        f'<li class="c{i}" style="--i:{i - 1}"><img src="/assets/{img}" alt="{escape(alt)}" width="320" height="220" loading="lazy" decoding="async">'
        f'<span class="num" aria-hidden="true">{i}</span><h3 class="h3">{escape(h)}</h3><p>{escape(t)}</p></li>'
        for i, (img, alt, h, t) in enumerate(STEPS, 1))
    promises = "".join(f"<li><b>{escape(h)}</b>{escape(t)}</li>" for h, t in PROMISES)
    desc = ("10% injury fee, even at trial. No fee and no costs without a recovery. A licensed Texas attorney on every case. "
            "See what you keep, then start your case online.")
    page = head("", desc, "/", HOME_CSS, full_title=CONFIG["title"]).replace("</head>", schema + "\n</head>") + f"""
<body>
{nav()}
<main id="main">
<section class="hero yellow" aria-labelledby="h1">
  <div class="in">
    <div>
      <h1 id="h1">10% fee.<br>Even at trial.</h1>
      <p class="body">A one-third fee is common for Texas injury cases. Ours is 10% of what we recover for you, and it stays 10% if your case goes to trial.</p>
      <ul class="ticks">
        <li>No fee and no costs without a recovery</li>
        <li>A licensed Texas attorney on every case</li>
        <li>You decide every offer</li>
      </ul>
      <div class="btns"><a class="b1" href="/start" onclick="track('start_click',{{from:'hero'}})">Start your case</a><a class="b2" href="#how">How it works</a></div>
    </div>
    {calculator()}
  </div>
</section>

<section class="sec cream" id="how" aria-labelledby="how-h">
  <div class="in">
    <h2 class="h2" id="how-h">How it works</h2>
    <p class="body">Three steps, mostly from your phone. No waiting room.</p>
    <ol class="steps">{steps}</ol>
  </div>
</section>

<section class="sec paper" id="fees" aria-labelledby="fees-h">
  <div class="in">
    <h2 class="h2" id="fees-h">Why 10% works</h2>
    <p class="body">Your fee doesn’t change what your case is worth. It changes how much of it you keep. We charge less because we spend less, not because we do less.</p>
    <div class="compare">
      <div class="col them"><h3 class="h3">Where a one-third fee goes</h3><ul><li>Staff who type letters and track deadlines by hand</li><li>Billboards and TV ads</li><li>Expensive offices</li></ul></div>
      <div class="col us"><h3 class="h3">Where our 10% goes</h3><ul><li>Software that does the paperwork</li><li>A trained case team that checks it</li><li>A licensed Texas attorney who reviews, advises and negotiates</li></ul></div>
    </div>
    <div class="money-box"><h3 class="h3">How 10flat makes money</h3><p>{FIRM} PLLC is a Texas law firm owned only by licensed attorneys. It is paid 10% of what it recovers for you, and nothing if there is no recovery. The software comes from 10flat Technologies, which the firm pays a fixed fee; it never receives any part of your recovery or of our fee.</p></div>
  </div>
</section>

<section class="sec cream phone-sec" aria-labelledby="app-h">
  <div class="in">
    <div>
      <h2 class="h2" id="app-h">Your case, on your phone.</h2>
      <p class="body">Every document, every update and every offer in one place, with what you’d actually keep. No calling the office to ask where your case is.</p>
      <ul class="ticks"><li>Upload photos, bills and letters any time</li><li>See the next step and when to expect it</li><li>For every offer: the fee, the costs, the bills and what’s left for you</li></ul>
    </div>
    <figure style="margin:0">
      <div class="phone" role="img" aria-label="Preview of the client app: a car accident case with documents received, the 10% fee, the next step, and an offer of $100,000 showing $85,000 to the client after the fee and example costs.">
        <div class="screen" aria-hidden="true">
          <div class="app-h"><span class="av">YC</span><div><b>Your case</b><span>Car accident · 10% fee, even at trial</span></div></div>
          <div class="tile"><b>Documents received</b><span class="muted">Police report · Medical bills · Photos</span></div>
          <div class="tile"><b>Next step</b><span class="muted">Waiting for medical records · expected in about 2 weeks</span></div>
          <div class="offer"><b>Offer from the insurer</b>
            <div class="r"><span>Offer</span><span>$100,000</span></div>
            <div class="r"><span>Our fee (10%)</span><span>−$10,000</span></div>
            <div class="r"><span>Case costs (example)</span><span>−$5,000</span></div>
            <div class="r t"><span>To you</span><span>$85,000</span></div>
            <div class="acts"><span>Talk to my attorney</span><span>Decide</span></div>
          </div>
        </div>
      </div>
      <figcaption class="preview">Preview of the client app. Figures are an example.</figcaption>
    </figure>
  </div>
</section>

<section class="sec paper" aria-labelledby="prom-h">
  <div class="in">
    <h2 class="h2" id="prom-h">Our promises</h2>
    <ul class="prom">{promises}</ul>
  </div>
</section>

<section class="sec cream" id="faq" aria-labelledby="faq-h">
  <div class="in">
    <h2 class="h2" id="faq-h">Questions people ask</h2>
    <div class="faq">{faq}</div>
  </div>
</section>

<section class="sec yellow close" aria-labelledby="close-h">
  <div class="in">
    <video class="gavel" muted loop playsinline preload="none" poster="/assets/gavel-poster.webp" data-src="/assets/gavel-480.mp4" width="854" height="480" aria-hidden="true"></video>
    <h2 class="h2" id="close-h">We’re putting an end to high legal fees.</h2>
    <p class="body">You’ve been through enough. Let us handle the legal part. We win when you win. Simple as that.</p>
    <div class="btns"><a class="b1" href="/start" onclick="track('start_click',{{from:'closing'}})">Start your case</a><a class="b2" href="#calculator">See your fee</a></div>
  </div>
</section>
</main>
{footer()}
<nav class="mbar" aria-label="Quick actions"><a class="b2" href="#calculator">Your fee</a><a class="b1" href="/start" onclick="track('start_click',{{from:'phone-bar'}})">Start your case</a></nav>
<script>{CALC_JS.replace("__TYPES__", types_js)}</script>
<script>{STACK_JS}</script>
<script>{GAVEL_JS}</script>
</body>
</html>
"""
    (SITE / "index.html").write_text(page, encoding="utf-8")
    check(page, "/", n_h1=1)
    print(f"built site/index.html: {len(page):,} bytes; {n_faq} questions")


def build_404():
    page = head("Page not found", "This page doesn’t exist. The 10% fee does.", "/404", HOME_CSS) + f"""
<body>
{nav()}
<main id="main" class="sec yellow" style="min-height:70vh">
  <div class="in">
    <h1 class="h2" style="font-size:clamp(48px,8vw,96px)">This page doesn’t exist.</h1>
    <p class="body">The 10% fee does. See what you’d keep, or tell us what happened.</p>
    <div class="btns"><a class="b1" href="/start">Start your case</a><a class="b2" href="/#calculator">See your fee</a></div>
  </div>
</main>
{footer()}
</body>
</html>
"""
    (SITE / "404.html").write_text(page, encoding="utf-8")
    check(page, "/404", n_h1=1)
    print("built site/404.html")


def build_seo():
    base = f"https://{CONFIG['domain']}"
    (SITE / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /classic/\nDisallow: /v2/\nDisallow: /api/\n\n"
        f"Sitemap: {base}/sitemap.xml\n", encoding="utf-8")
    urls = "".join(f"  <url><loc>{base}{p}</loc></url>\n" for p in ("/", "/start", "/privacy", "/terms"))
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n",
        encoding="utf-8")
    print("built robots.txt and sitemap.xml")


def check(page, path, n_h1):
    body = page[page.find("<body"):]
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S)))
    m = re.search(r"\[[^\]]{2,80}\]", text)
    if m:
        raise SystemExit(f"build_home {path}: placeholder: {m.group(0)!r}")
    for bad in ("Se habla", "smaller settlement", "worth the same", "not on what your lawyer charges", "Most injury firms take",
                "WhatsApp us", "guaranteed", "after case costs", "never goes up"):
        if bad.lower() in text.lower():
            raise SystemExit(f"build_home {path}: review flagged wording {bad!r}")
    if body.count("<h1") != n_h1:
        raise SystemExit(f"build_home {path}: {body.count('<h1')} h1")
    for img in re.findall(r"<img\b[^>]*>", body):
        if not re.search(r'alt="[^"]+"', img):
            raise SystemExit(f"build_home {path}: image without alt text: {img[:80]}")


def build():
    build_home()
    build_404()
    build_seo()


if __name__ == "__main__":
    build()
