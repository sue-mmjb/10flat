"""Build the home page, the case-type pages, /fees, the share pages, the 404 page, robots.txt and sitemap.xml.

History: rebuilt by hand after the first website review (2 Nov 2026) and revised after the second ("Round 2"): steps
in one row on desktop (stacked cards on phones), "What we don't pay for" instead of a comparison with other firms, a
custom comparison percentage, a message above $100M, share links whose preview image shows the number, case-type pages
and a fees page. The fee is 10% of the total amount recovered at every stage (platform SOW v2.0).
"""
import json
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site import CONFIG, FAQ_ALL_GROUPS, FAQ_GROUPS, SCHEMA, sync_schema_faq  # noqa: E402
from site_common import CASE_PAGES, FIRM, SITE, URL, finalize, footer, head, nav  # noqa: E402

# Case types for the calculator: an example cost share (and minimum) and what the attorney will ask for.
# The cost figures are examples the client can change; the page labels them that way.
CASE_TYPES = [
    ("car", "Car", 0.05, 500, ["Crash report, if there is one", "Photos of the vehicles and your injuries", "Your insurance and the other driver’s", "Medical bills so far"]),
    ("truck", "Truck", 0.07, 1500, ["Crash report", "Photos of the scene and the truck", "The trucking company’s name, if you know it", "Medical bills so far"]),
    ("fall", "Slip and fall", 0.05, 500, ["Photos of where it happened", "Any incident report you were given", "Names of witnesses", "Medical bills so far"]),
    ("medical", "Medical", 0.12, 5000, ["Names of the doctors and hospitals", "Dates of treatment", "Any records or letters you have", "Bills so far"]),
    ("dental", "Dental", 0.10, 3000, ["The dentist’s name and office", "Dates of treatment", "X-rays or records you have", "Bills so far"]),
    ("other", "Other", 0.05, 500, ["Photos", "Any reports or letters", "Medical bills so far"]),
]
TYPE_BY_KEY = {k: (k, label, share, mn, need) for k, label, share, mn, need in CASE_TYPES}

# Settlement amounts that get a share page and preview image; a share snaps to the nearest one.
SHARE_TIERS = [1000, 2000, 3000, 4000, 5000, 7500, 10000, 15000, 20000, 25000, 30000, 40000, 50000, 60000, 75000,
               100000, 125000, 150000, 200000, 250000, 300000, 400000, 500000, 600000, 750000, 1000000, 1250000,
               1500000, 2000000, 2500000, 3000000, 4000000, 5000000, 7500000, 10000000, 15000000, 20000000, 25000000,
               50000000, 75000000, 100000000]

CSS = r"""
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
.hero{padding:32px 32px 72px}
.hero .in{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,460px);gap:64px;align-items:center}
.hero h1{font-size:clamp(52px,7.4vw,104px);line-height:.92;margin:0 0 24px}
.hero.case h1{font-size:clamp(44px,5.6vw,80px)}
.hero .body{font-size:21px}
.calc{background:var(--white);border-radius:28px;padding:22px 26px;box-shadow:0 30px 70px -36px rgba(20,12,10,.45)}
.calc .lbl{font-size:14px;color:var(--muted);margin:0}
.big{font:800 50px/1 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.03em;margin:6px 0 4px;font-variant-numeric:tabular-nums}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 0}
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
.calc input.pct{width:34px;text-align:center;border:0;border-bottom:1.5px dashed #cfc6ad;background:transparent;font:600 15px/1.2 "Instrument Sans",sans-serif;color:var(--ink);padding:0;border-radius:0;min-height:0}
.calc input:focus{outline:none;border-bottom-color:var(--ink)}
input[type=range]{width:100%;margin:10px 0 0;accent-color:var(--ink);height:28px}
.rows{display:grid;gap:6px}
.row{display:flex;justify-content:space-between;align-items:center;gap:12px;font-size:15px}
.row .v{font-weight:600;font-variant-numeric:tabular-nums}
.row.dim .v{color:var(--muted)}
.row.keep{font-size:17px;font-weight:600;border-top:1px solid var(--line);padding-top:10px;margin-top:4px}
.row label{font-weight:400;font-size:15px}
.cmsg{font-size:13px;color:var(--err);margin:8px 0 0}
.cmsg:empty{display:none}
.cact{display:grid;grid-template-columns:1fr auto;gap:10px;margin-top:14px}
.cact .b1{min-height:52px;font-size:16px}
.share{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:52px;padding:0 16px;border-radius:999px;border:2px solid var(--line);font:600 14px/1 "Instrument Sans",sans-serif;text-decoration:none;color:var(--ink)}
.share:hover{border-color:var(--ink)}
.need{margin:12px 0 0;font-size:13px;color:var(--muted)}
.need summary{cursor:pointer;font-weight:600;color:var(--ink);text-decoration:underline;text-underline-offset:3px;width:max-content}
.need ul{margin:8px 0 0;padding-left:18px;display:grid;gap:3px}
.cfine{font-size:11.5px;line-height:1.45;color:var(--muted);margin:10px 0 0}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:40px;list-style:none;padding:0}
.steps li{border-radius:28px;padding:28px;display:flex;flex-direction:column}
.steps li.c1{background:#ffe435}
.steps li.c2{background:#b8d63a}
.steps li.c3{background:#f4b0d8}
.steps img{width:100%;height:auto;aspect-ratio:320/220;object-fit:contain;margin:0 0 18px}
.steps p{margin:0;font-size:16px;line-height:1.55}
.num{display:inline-flex;width:34px;height:34px;border-radius:50%;background:var(--ink);color:#fff;align-items:center;justify-content:center;font-weight:700;margin-bottom:12px;align-self:flex-start}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:36px}
.col{border-radius:24px;padding:28px}
.col.them{background:var(--white)}
.col.us{background:var(--yellow)}
.col ul{margin:0;padding-left:20px;display:grid;gap:8px;font-size:17px}
.money-box{margin-top:24px;background:var(--ink);color:#fff;border-radius:24px;padding:28px 32px;display:grid;grid-template-columns:auto 1fr;gap:24px;align-items:start}
.money-box .h3{color:var(--yellow);margin:0}
.money-box p{margin:0;font-size:17px;line-height:1.6;color:#efe9da}
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
.prom{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:36px;list-style:none;padding:0}
.prom li{background:var(--white);border-radius:20px;padding:22px 24px;font-size:16px;line-height:1.5}
.prom b{display:block;font:800 21px/1.15 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.01em;margin-bottom:6px}
.faq{max-width:820px;margin:32px 0 0}
.faq details{border-bottom:1px solid var(--line)}
.faq summary{list-style:none;cursor:pointer;padding:20px 44px 20px 0;position:relative;font-weight:600;font-size:18px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";position:absolute;right:6px;top:50%;transform:translateY(-50%);font-size:26px;font-weight:400}
.faq details[open] summary::after{content:"–"}
.faq p{margin:0 0 20px;font-size:17px;line-height:1.6;max-width:720px}
.close .in{text-align:center}
.close .h2{max-width:900px;margin:0 auto 14px}
.gavel{display:block;width:min(520px,100%);height:auto;aspect-ratio:854/480;margin:-24px auto 4px;mix-blend-mode:darken}
.close .body{margin:0 auto}
.close .btns{justify-content:center}
.facts{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:32px}
.facts .col{background:var(--white)}
.facts ul{margin:0;padding-left:20px;display:grid;gap:10px;font-size:17px;line-height:1.5}
.note{font-size:13px;color:var(--muted);margin:16px 0 0}
.table-wrap{overflow-x:auto;margin-top:28px;background:var(--white);border-radius:24px;padding:8px 20px}
table.fees{width:100%;border-collapse:collapse;font-size:16px;min-width:640px}
table.fees th,table.fees td{padding:14px 10px;border-bottom:1px solid var(--line);text-align:right;font-variant-numeric:tabular-nums}
table.fees th:first-child,table.fees td:first-child{text-align:left}
table.fees thead th{font-size:13px;color:var(--muted);font-weight:600}
table.fees tr:last-child td{border-bottom:0}
table.fees .us{font-weight:700}
table.fees .diff{background:var(--yellow);font-weight:700}
.share-hero .big2{font:800 clamp(48px,8vw,112px)/.95 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.03em;margin:0 0 20px}
.mbar{display:none}
@media(max-width:1020px){
  .hero .in,.phone-sec .in{grid-template-columns:1fr;gap:40px}
  .calc{max-width:520px}
}
@media(max-width:860px){
  .prom,.compare,.facts{grid-template-columns:1fr}
  .money-box{grid-template-columns:1fr;gap:10px}
  .steps{grid-template-columns:1fr;gap:0}
  .steps::after{content:"";display:block;height:26vh}
  .steps li{position:sticky;top:calc(var(--stack-top,76px) + var(--i) * 14px);min-height:min(560px,calc(100svh - 190px));margin-bottom:32px;
    padding:28px 26px 30px;box-shadow:0 -10px 30px -18px rgba(20,12,10,.35);transform-origin:50% 0;will-change:transform}
  .steps li:last-child{margin-bottom:0}
  .steps img{max-height:220px;margin:0 0 22px}
}
@media(max-width:760px){
  .sec{padding:64px 20px}
  .hero{padding:28px 20px 56px}
  .hero h1{font-size:clamp(46px,13vw,72px)}
  .hero.case h1{font-size:clamp(38px,10vw,56px)}
  .hero .body{font-size:17px;margin-bottom:0}
  .hero .ticks,.hero .btns{display:none}
  .hero .in{gap:24px}
  .calc{padding:22px 18px;border-radius:24px}
  .big{font-size:46px}
  .cact{grid-template-columns:1fr}
  .mbar{display:grid;grid-template-columns:auto 1fr;gap:8px;position:fixed;left:0;right:0;bottom:0;z-index:30;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:rgba(247,245,239,.97);border-top:1px solid var(--line)}
  .mbar a{min-height:50px;font-size:16px}
  body.has-mbar{padding-bottom:76px}
}
"""

GAVEL_JS = r"""
(function () {
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
  var mq = window.matchMedia('(max-width: 860px)'), reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var cards = [].slice.call(document.querySelectorAll('.steps li')), ticking = false, nav = document.querySelector('.nav');
  if (!cards.length) return;
  function setTop() { document.documentElement.style.setProperty('--stack-top', ((nav ? nav.getBoundingClientRect().height : 64) + 12) + 'px'); }
  function update() {
    ticking = false;
    cards.forEach(function (c, i) {
      if (!mq.matches || reduce.matches || i === cards.length - 1) { c.style.transform = ''; return; }
      var r = c.getBoundingClientRect(), n = cards[i + 1].getBoundingClientRect();
      var covered = Math.min(1, Math.max(0, (r.bottom - n.top) / r.height));
      c.style.transform = 'scale(' + (1 - 0.06 * covered).toFixed(4) + ')';
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
  var TYPES = __TYPES__, TIERS = __TIERS__;
  var RATE = 0.10, MIN = 1000, MAX = 100000000, SMIN = 1000, SMAX = 10000000;
  var c = document.getElementById('calculator'); if (!c) return;
  var $ = function (s) { return c.querySelector(s); };
  var amountIn = $('#c-amount'), range = $('#c-range'), costsIn = $('#c-costs'), liensIn = $('#c-liens'), pctIn = $('#c-pct'), msg = $('#c-msg');
  var q = new URLSearchParams(location.search);
  var state = { type: c.dataset.type || 'car', amount: 100000, costs: null, liens: 0, pct: 33, over: false };
  var qa = parseInt(q.get('amount') || '', 10); if (qa >= MIN) state.amount = Math.min(MAX, qa);
  if (q.get('type') && TYPES[q.get('type')]) state.type = q.get('type');
  function money(n) { return '$' + Math.round(n).toLocaleString('en-US'); }
  function parse(v) { var d = String(v).replace(/[^0-9]/g, ''); return d ? Number(d) : NaN; }
  function autoCosts(a) { var t = TYPES[state.type]; return Math.min(a, Math.max(t.min, Math.round(a * t.share / 500) * 500)); }
  function toRange(a) { return Math.round(Math.log10(Math.min(SMAX, Math.max(SMIN, a)) / SMIN) / Math.log10(SMAX / SMIN) * 1000); }
  function fromRange(v) {
    var a = SMIN * Math.pow(SMAX / SMIN, v / 1000), step = a < 10000 ? 100 : a < 100000 ? 1000 : a < 1000000 ? 5000 : 50000;
    return Math.round(a / step) * step;
  }
  function tier(a) { var best = TIERS[0]; TIERS.forEach(function (t) { if (Math.abs(t - a) < Math.abs(best - a)) best = t; }); return best; }
  function set(id, v) { [].forEach.call(c.querySelectorAll('[data-out="' + id + '"]'), function (e) { e.textContent = v; }); }
  function render() {
    var a = state.amount, costs = state.costs == null ? autoCosts(a) : state.costs, liens = state.liens;
    var fee = a * RATE, other = a * state.pct / 100, left = a - fee - costs - liens;
    set('more', money(Math.max(0, other - fee))); set('fee', money(fee)); set('other', money(other)); set('keep', money(Math.max(0, left)));
    set('pct', String(state.pct));
    if (document.activeElement !== costsIn) costsIn.value = money(costs);
    if (document.activeElement !== liensIn) liensIn.value = money(liens);
    if (document.activeElement !== amountIn) amountIn.value = money(a);
    if (document.activeElement !== pctIn) pctIn.value = String(state.pct);
    range.value = toRange(a); range.setAttribute('aria-valuetext', money(a));
    msg.textContent = state.over ? 'Over $100M? Talk to us: start your case and an attorney will go through it with you.'
      : left < 0 ? 'Those costs and bills are more than the settlement after our fee. Every case is different; your attorney goes through the numbers with you before anything is decided.' : '';
    var t = TYPES[state.type];
    $('#c-need').innerHTML = t.need.map(function (n) { return '<li>' + n + '</li>'; }).join('');
    $('#c-start').href = '/start?type=' + state.type;
    var s = tier(a);
    var text = 'At ' + c.dataset.firm + ' the injury fee is 10%, even at trial. On a ' + money(s) + ' settlement, that is ' + money(s * 0.23) + ' more for the client than a one-third fee: ' + location.origin + '/share/' + s;
    $('#c-share').href = 'https://wa.me/?text=' + encodeURIComponent(text);
  }
  [].forEach.call(c.querySelectorAll('.types button'), function (b) {
    b.setAttribute('aria-pressed', String(b.dataset.type === state.type));
    b.addEventListener('click', function () {
      [].forEach.call(c.querySelectorAll('.types button'), function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      state.type = b.dataset.type; state.costs = null; render(); window.track && track('calc_type', { type: state.type });
    });
  });
  range.addEventListener('input', function () { state.amount = fromRange(Number(range.value)); state.over = false; render(); });
  range.addEventListener('change', function () { window.track && track('calc_amount'); });
  amountIn.addEventListener('input', function () {
    var n = parse(amountIn.value);
    if (isNaN(n)) return;
    if (n < MIN) { msg.textContent = 'Enter a settlement of at least $1,000.'; return; }
    state.over = n > MAX; state.amount = Math.min(MAX, n); render();
  });
  amountIn.addEventListener('blur', function () { amountIn.value = money(state.amount); if (msg.textContent.indexOf('at least') > -1) msg.textContent = ''; });
  pctIn.addEventListener('input', function () { var n = parse(pctIn.value); if (n >= 11 && n <= 60) { state.pct = n; render(); } });
  pctIn.addEventListener('blur', function () { var n = parse(pctIn.value); state.pct = isNaN(n) ? 33 : Math.min(60, Math.max(11, n)); render(); });
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


def calculator(default="car"):
    k, label, share, mn, need = TYPE_BY_KEY[default]
    a = 100000
    costs = max(mn, round(a * share / 500) * 500)
    types = "".join(f'<button type="button" data-type="{key}" aria-pressed="{str(key == default).lower()}">{lab}</button>'
                    for key, lab, *_r in CASE_TYPES)
    needs = "".join(f"<li>{escape(n)}</li>" for n in need)
    return f"""
<div class="calc" id="calculator" data-firm="{FIRM}" data-type="{default}" aria-labelledby="calc-h">
  <h2 class="sr" id="calc-h">Fee calculator</h2>
  <p class="lbl">You keep this much more than with a <span data-out="pct">33</span>% fee</p>
  <p class="big" data-out="more" aria-live="polite">{money(a * 0.23)}</p>
  <div class="tags"><span>10% of the settlement</span><span>Stays 10% at trial</span></div>
  <div class="cblk"><p class="lbl" id="types-l">Case type</p><div class="types" role="group" aria-labelledby="types-l">{types}</div></div>
  <div class="cblk">
    <div class="amt"><label for="c-amount">If your case settles for</label><input class="money" id="c-amount" type="text" inputmode="numeric" value="{money(a)}" autocomplete="off"></div>
    <input id="c-range" type="range" min="0" max="1000" step="1" value="500" aria-label="Settlement amount" aria-valuetext="{money(a)}">
  </div>
  <div class="cblk rows">
    <div class="row dim"><label for="c-pct">Fee at a <input class="pct" id="c-pct" type="text" inputmode="numeric" value="33" autocomplete="off" aria-label="Comparison fee, percent">% firm</label><span class="v" data-out="other">{money(a * 0.33)}</span></div>
    <div class="row"><span>Our fee (10%)</span><span class="v" data-out="fee">{money(a * 0.10)}</span></div>
    <div class="row"><label for="c-costs">Case costs (example, change it)</label><input class="money sm" id="c-costs" type="text" inputmode="numeric" value="{money(costs)}" autocomplete="off"></div>
    <div class="row"><label for="c-liens">Medical bills and liens (optional)</label><input class="money sm" id="c-liens" type="text" inputmode="numeric" value="$0" autocomplete="off"></div>
    <div class="row keep"><span>You keep</span><span class="v" data-out="keep">{money(a - a * 0.10 - costs)}</span></div>
  </div>
  <p class="cmsg" id="c-msg" role="status"></p>
  <div class="cact"><a class="b1" id="c-start" href="/start?type={default}">Start your case</a><a class="share" id="c-share" href="https://wa.me/" target="_blank" rel="noopener">Share on WhatsApp</a></div>
  <details class="need"><summary>What we’ll ask you for</summary><ul id="c-need">{needs}</ul></details>
  <p class="cfine">An illustration, not a prediction of what your case is worth. Both fees are figured on the full settlement; case costs, medical bills and liens are paid from your share the same way at any firm.</p>
</div>"""


STEPS = [
    ("step-1.webp", "Drawing of a phone sending photos and documents, next to a speech bubble with an exclamation and question mark.",
     "Tell us what happened.",
     "Send your case with our short online form, with any photos or documents you have. A licensed Texas attorney reviews every case, and we tell you when to expect an answer. You see your attorney’s name and Texas license, and can ask them anything, before you sign."),
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

MONEY_BOX = (f'<div class="money-box"><h3 class="h3">How 10flat makes money</h3><p>{FIRM} PLLC is a Texas law firm owned only by '
             "licensed attorneys. It is paid 10% of what it recovers for you, and nothing if there is no recovery. The software "
             "comes from 10flat Technologies, which the firm pays a fixed fee; it never receives any part of your recovery or of our fee.</p></div>")

CASE_CONTENT = {
    "car-accident": {
        "h1": "Car accident lawyer in Texas. 10% fee, even at trial.",
        "lead": "Hurt in a car crash in Texas? Our fee is 10% of what we recover for you, at every stage. A one-third fee is common for Texas injury cases.",
        "send": ["The crash report number or a copy, if there is one", "Photos of the vehicles, the scene and your injuries",
                 "Your insurance details, and the other driver’s if you have them", "Medical bills and records so far", "Names and numbers of any witnesses"],
        "deadlines": ["Texas injury lawsuits generally must be filed within two years of the crash.",
                      "If a city, county, state or school vehicle was involved, a written notice can be due within six months, and some cities set shorter deadlines."],
    },
    "truck-accident": {
        "h1": "Truck accident lawyer in Texas. 10% fee, even at trial.",
        "lead": "Hurt in a crash with a truck or commercial vehicle in Texas? Our fee is 10% of what we recover for you, at every stage, including trial.",
        "send": ["The crash report number or a copy", "Photos of the scene, the truck and any company name or number on it",
                 "Your insurance details", "Medical bills and records so far", "Names and numbers of any witnesses"],
        "deadlines": ["Texas injury lawsuits generally must be filed within two years of the crash.",
                      "Some records, such as driver logs and truck data, may be kept only for a limited time, so it helps to start early.",
                      "If a government vehicle was involved, a written notice can be due within six months, and some cities set shorter deadlines."],
    },
    "slip-and-fall": {
        "h1": "Slip and fall lawyer in Texas. 10% fee, even at trial.",
        "lead": "Hurt in a fall at a store, a workplace or someone else’s property in Texas? Our fee is 10% of what we recover for you, at every stage.",
        "send": ["Photos of where you fell and what caused it", "Any incident report you were given", "Names of witnesses or staff you spoke to",
                 "Medical bills and records so far"],
        "deadlines": ["Texas injury lawsuits generally must be filed within two years of the fall.",
                      "If it happened on city, county, state or school property, a written notice can be due within six months, and some cities set shorter deadlines.",
                      "Hazards get fixed and video gets recorded over, so photos and names collected early help."],
    },
    "medical-injury": {
        "h1": "Medical injury lawyer in Texas. 10% fee, even at trial.",
        "lead": "Hurt by a doctor, hospital or clinic in Texas? Our fee is 10% of what we recover for you, at every stage, including trial.",
        "send": ["Names of the doctors, hospitals and clinics", "Dates of the treatment", "Any records, letters or discharge papers you have",
                 "Medical bills so far", "What has changed for you since the treatment"],
        "deadlines": ["Texas health care claims generally must be brought within two years of the treatment, with special rules for some cases.",
                      "These cases need a medical expert: once a lawsuit is filed, an expert report is generally due within 120 days of the defendant’s answer.",
                      "Expert costs are higher in these cases. Your attorney sets a cost budget with you when the case is accepted, and you owe no costs if there is no recovery."],
    },
    "dental-injury": {
        "h1": "Dental injury lawyer in Texas. 10% fee, even at trial.",
        "lead": "Hurt by a dentist, oral surgeon or dental clinic in Texas? Our fee is 10% of what we recover for you, at every stage, including trial.",
        "send": ["The dentist’s name and office", "Dates of the treatment", "X-rays, records or treatment plans you have",
                 "Dental and medical bills so far", "What is wrong now, such as pain or numbness"],
        "deadlines": ["Claims against dentists are health care claims in Texas, which generally must be brought within two years of the treatment.",
                      "These cases need a dental expert: once a lawsuit is filed, an expert report is generally due within 120 days of the defendant’s answer.",
                      "Expert costs are higher in these cases. Your attorney sets a cost budget with you when the case is accepted, and you owe no costs if there is no recovery."],
    },
}


def steps_html():
    return "".join(
        f'<li class="c{i}" style="--i:{i - 1}"><img src="/assets/{img}" alt="{escape(alt)}" width="320" height="220" loading="lazy" decoding="async">'
        f'<span class="num" aria-hidden="true">{i}</span><h3 class="h3">{escape(h)}</h3><p>{escape(t)}</p></li>'
        for i, (img, alt, h, t) in enumerate(STEPS, 1))


def faq_html(items):
    return "".join(f'<details><summary>{escape(i["q"])}</summary><p>{escape(i["a"])}</p></details>' for i in items)


def mbar():
    return ('<nav class="mbar" aria-label="Quick actions"><a class="b2" href="#calculator">Your fee</a>'
            '<a class="b1" href="/start" onclick="track(\'start_click\',{from:\'phone-bar\'})">Start your case</a></nav>')


def scripts(calc=True, stack=True, gavel=False):
    types_js = json.dumps({k: {"label": l, "share": s, "min": m, "need": [escape(x) for x in need]} for k, l, s, m, need in CASE_TYPES}, ensure_ascii=False)
    out = ""
    if calc:
        out += "<script>" + CALC_JS.replace("__TYPES__", types_js).replace("__TIERS__", json.dumps(SHARE_TIERS)) + "</script>\n"
    if stack:
        out += f"<script>{STACK_JS}</script>\n"
    if gavel:
        out += f"<script>{GAVEL_JS}</script>\n"
    return out


def closing(where):
    return f"""
<section class="sec yellow close" aria-labelledby="close-h">
  <div class="in">
    <video class="gavel" muted loop playsinline preload="none" poster="/assets/gavel-poster.webp" data-src="/assets/gavel-480.mp4" width="854" height="480" aria-hidden="true"></video>
    <h2 class="h2" id="close-h">We’re putting an end to high legal fees.</h2>
    <p class="body">You’ve been through enough. Let us handle the legal part. We win when you win. Simple as that.</p>
    <div class="btns"><a class="b1" href="/start" onclick="track('start_click',{{from:'{where}'}})">Start your case</a><a class="b2" href="#calculator">See your fee</a></div>
  </div>
</section>"""


def build_home(schema):
    faq_items = [i for g in FAQ_GROUPS for i in g["items"]]
    desc = ("10% injury fee, even at trial. No fee and no costs without a recovery. A licensed Texas attorney on every case. "
            "See what you keep, then start your case online.")
    promises = "".join(f"<li><b>{escape(h)}</b>{escape(t)}</li>" for h, t in PROMISES)
    page = head("", desc, "/", CSS, full_title=CONFIG["title"]).replace("</head>", schema + "\n</head>") + f"""
<body class="has-mbar">
{nav()}
<main id="main">
<section class="hero yellow" aria-labelledby="h1">
  <div class="in">
    <div>
      <h1 id="h1">10% fee.<br>Even at trial.</h1>
      <p class="body">A one-third fee is common for Texas injury cases. Ours is 10% of what we recover for you, and it stays 10% if your case goes to trial.</p>
      <ul class="ticks"><li>No fee and no costs without a recovery</li><li>A licensed Texas attorney on every case</li><li>You decide every offer</li></ul>
      <div class="btns"><a class="b1" href="/start" onclick="track('start_click',{{from:'hero'}})">Start your case</a><a class="b2" href="#how">How it works</a></div>
    </div>
    {calculator()}
  </div>
</section>

<section class="sec cream" id="how" aria-labelledby="how-h">
  <div class="in">
    <h2 class="h2" id="how-h">How it works</h2>
    <p class="body">Three steps, mostly from your phone. No waiting room.</p>
    <ol class="steps">{steps_html()}</ol>
  </div>
</section>

<section class="sec paper" id="fees" aria-labelledby="fees-h">
  <div class="in">
    <h2 class="h2" id="fees-h">Why 10% works</h2>
    <p class="body">Your fee doesn’t change what your case is worth. It changes how much of it you keep. We charge less because we spend less, not because we do less.</p>
    <div class="compare">
      <div class="col them"><h3 class="h3">What we don’t pay for</h3><ul><li>No billboards or TV ads</li><li>No downtown office</li><li>No one retyping letters</li></ul></div>
      <div class="col us"><h3 class="h3">Where our 10% goes</h3><ul><li>Software that does the paperwork</li><li>A trained case team that checks it</li><li>A licensed Texas attorney who reviews, advises and negotiates</li></ul></div>
    </div>
    {MONEY_BOX}
    <div class="btns"><a class="b2" href="/fees">Fee examples</a></div>
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
    <div class="faq">{faq_html(faq_items)}</div>
  </div>
</section>
{closing('closing')}
</main>
{footer()}
{mbar()}
{scripts(gavel=True)}
</body>
</html>
"""
    finalize(page, "index.html")
    print(f"built site/index.html; {len(faq_items)} questions")


def build_case_pages():
    by_q = {i["q"]: i for g in FAQ_ALL_GROUPS for i in g["items"]}
    common_q = ["What is the attorney fee?", "What do I pay if we lose?", "What are case costs, and who pays my medical bills and liens?"]
    for slug, label, key, _incident in CASE_PAGES:
        c = CASE_CONTENT[slug]
        send = "".join(f"<li>{escape(x)}</li>" for x in c["send"])
        deadlines = "".join(f"<li>{escape(x)}</li>" for x in c["deadlines"])
        page = head(c["h1"].split(".")[0], c["lead"], f"/{slug}", CSS, full_title=f"{c['h1'].split('.')[0]}: 10% fee | {FIRM}") + f"""
<body class="has-mbar">
{nav()}
<main id="main">
<section class="hero case yellow" aria-labelledby="h1">
  <div class="in">
    <div>
      <h1 id="h1">{escape(c['h1'])}</h1>
      <p class="body">{escape(c['lead'])}</p>
      <ul class="ticks"><li>No fee and no costs without a recovery</li><li>A licensed Texas attorney reviews every case</li><li>You decide every offer</li></ul>
      <div class="btns"><a class="b1" href="/start?type={key}" onclick="track('start_click',{{from:'{slug}'}})">Start your case</a><a class="b2" href="#facts">What to send us</a></div>
    </div>
    {calculator(key)}
  </div>
</section>

<section class="sec cream" id="facts" aria-labelledby="facts-h">
  <div class="in">
    <h2 class="h2" id="facts-h">What to send us, and deadlines to know</h2>
    <div class="facts">
      <div class="col"><h3 class="h3">What to send us</h3><ul>{send}</ul><p class="note">Send what you have. Your attorney asks for anything else.</p></div>
      <div class="col"><h3 class="h3">Deadlines to know</h3><ul>{deadlines}</ul><p class="note">General information, not legal advice. Your attorney checks the deadlines for your case first.</p></div>
    </div>
  </div>
</section>

<section class="sec paper" id="how" aria-labelledby="how-h">
  <div class="in">
    <h2 class="h2" id="how-h">How it works</h2>
    <ol class="steps">{steps_html()}</ol>
    {MONEY_BOX}
  </div>
</section>

<section class="sec cream" id="faq" aria-labelledby="faq-h">
  <div class="in">
    <h2 class="h2" id="faq-h">Questions people ask</h2>
    <div class="faq">{faq_html([by_q[q] for q in common_q])}</div>
    <div class="btns"><a class="b2" href="/#faq">More questions</a></div>
  </div>
</section>
{closing(slug)}
</main>
{footer()}
{mbar()}
{scripts(gavel=True)}
</body>
</html>
"""
        finalize(page, f"{slug}/index.html")
    print(f"built {len(CASE_PAGES)} case-type pages")


def build_fees():
    rows = ""
    for amount, costs in ((15000, 1000), (35000, 2000), (100000, 5000)):
        fee, third = amount * 0.10, amount * 0.33
        rows += (f"<tr><td>{money(amount)}</td><td>{money(costs)}</td><td class=\"us\">{money(fee)}</td>"
                 f"<td class=\"us\">{money(amount - fee - costs)}</td><td>{money(third)}</td><td>{money(amount - third - costs)}</td>"
                 f"<td class=\"diff\">{money(third - fee)}</td></tr>")
    desc = "Our fee is 10% of the total amount recovered, at every stage, including trial. Worked examples, what is included and how 10flat makes money."
    page = head("Fees", desc, "/fees", CSS, full_title=f"Fees: 10%, at every stage | {FIRM}") + f"""
<body class="has-mbar">
{nav()}
<main id="main">
<section class="hero case yellow" aria-labelledby="h1">
  <div class="in">
    <div>
      <h1 id="h1">Our fee is 10%. At every stage.</h1>
      <p class="body">10% of the total amount recovered, whether your case settles in a month or goes to trial. If there is no recovery, you owe no fee and no case costs.</p>
      <ul class="ticks"><li>No admin, file or technology fees</li><li>Case costs advanced by us and repaid at cost</li><li>The full fee agreement, in plain English, before you sign</li></ul>
    </div>
    {calculator()}
  </div>
</section>

<section class="sec cream" aria-labelledby="ex-h">
  <div class="in">
    <h2 class="h2" id="ex-h">Worked examples</h2>
    <p class="body">Three settlements with example case costs. Both fees are figured on the full settlement. Medical bills and liens come out of your share the same way at any firm, so they are left out here.</p>
    <div class="table-wrap"><table class="fees">
      <thead><tr><th scope="col">Settlement</th><th scope="col">Case costs (example)</th><th scope="col">Our fee (10%)</th><th scope="col">You keep with us</th><th scope="col">A one-third fee</th><th scope="col">You’d keep</th><th scope="col">You keep more</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    <p class="note">Examples only, not a prediction of what any case is worth. A one-third (33%) fee is common for Texas injury cases; fees vary by firm.</p>
  </div>
</section>

<section class="sec paper" aria-labelledby="inc-h">
  <div class="in">
    <h2 class="h2" id="inc-h">What the 10% covers</h2>
    <div class="facts">
      <div class="col"><h3 class="h3">Included</h3><ul><li>Your attorney’s work, from the first review to trial</li><li>The case team and the software that prepare the paperwork</li><li>Every update and every offer, with what you’d keep</li></ul></div>
      <div class="col"><h3 class="h3">Never charged</h3><ul><li>No admin, file or technology fees</li><li>No markup on case costs</li><li>No fee and no costs if there is no recovery</li></ul></div>
    </div>
    {MONEY_BOX}
  </div>
</section>
{closing('fees')}
</main>
{footer()}
{mbar()}
{scripts(stack=False, gavel=True)}
</body>
</html>
"""
    finalize(page, "fees/index.html")
    print("built site/fees/index.html")


def build_share_pages():
    import make_assets
    for amount in SHARE_TIERS:
        more = amount * 0.23
        img = SITE / "share" / f"{amount}.jpg"
        if not img.exists():
            make_assets.share_image(amount, more, img)
        title = f"On a {money(amount)} settlement: keep {money(more)} more"
        desc = f"With a 10% fee instead of a one-third fee. {FIRM}’s fee stays 10%, even at trial."
        page = head("", desc, f"/share/{amount}", CSS, full_title=f"{title} | {FIRM}", og_image=f"{URL}/share/{amount}.jpg",
                    og_title=title, og_alt=f"{title}. 10% fee, even at trial. {FIRM}.") + f"""
<body>
{nav()}
<main id="main" class="sec yellow share-hero" style="min-height:72vh">
  <div class="in">
    <h1 class="big2">On a {money(amount)} settlement, keep {money(more)} more.</h1>
    <p class="body">That is the difference between a 10% fee and a one-third fee on the same settlement. Our fee stays 10% even at trial. An illustration, not a prediction of what any case is worth.</p>
    <div class="btns"><a class="b1" href="/?amount={amount}#calculator">See your own numbers</a><a class="b2" href="/start">Start your case</a></div>
  </div>
</main>
{footer()}
</body>
</html>
"""
        finalize(page, f"share/{amount}/index.html")
    print(f"built {len(SHARE_TIERS)} share pages")


def build_404():
    page = head("Page not found", "This page doesn’t exist. The 10% fee does.", "/404", CSS) + f"""
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
    finalize(page, "404.html")
    print("built site/404.html")


def build_seo():
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {URL}/sitemap.xml\n", encoding="utf-8")
    paths = ["/", "/start", "/es/start", "/fees"] + [f"/{slug}" for slug, *_ in CASE_PAGES] + ["/privacy", "/terms"]
    urls = "".join(f"  <url><loc>{URL}{p}</loc></url>\n" for p in paths)
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n",
        encoding="utf-8")
    print("built robots.txt and sitemap.xml")


def build():
    sync_schema_faq()
    schema = re.search(r'<script type="application/ld\+json">.*?</script>', SCHEMA.read_text(encoding="utf-8"), re.S).group(0)
    schema = schema.replace(f"https://{CONFIG['domain']}", URL)
    build_home(schema)
    build_case_pages()
    build_fees()
    build_share_pages()
    build_404()
    build_seo()


if __name__ == "__main__":
    build()
