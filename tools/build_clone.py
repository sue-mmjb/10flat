#!/usr/bin/env python3
"""Build site/index.html: the mystack.com clone with every tile and section
kept, the text swapped for the personal injury content, and the scroll
motion put back with a small script of our own.

Why there is a script of our own: Framer's bundle re-renders the page from
Stack's data a few seconds after load and puts "Brutal Renewal" back (tested
30 Oct 2026), so it cannot stay. Without it the scroll-pinned sections sat
frozen, which left the three-step section as a blank runway. The motion layer
below reproduces what the bundle did: scroll-in reveals, the pinned card
stack, the pinned closing image, the logo ticker, the quote arrows, and a
calculator card with Tim's real numbers.

Run from the project root:
    python tools/build_clone.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site import Tree, by_name, by_class, derevelo, unhide, strip_comments, CONFIG, SCHEMA  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "mystack-index.html"
OUT = ROOT / "site" / "index.html"
FIRM = CONFIG["firm"]

# ----------------------------------------------------------------------------
# Text swaps. Left = exact text in the clone (curly quotes as in the source).
# ----------------------------------------------------------------------------
GLOBAL = [
    ('href="./brokers">For Brokers', 'href="#we-win-when">Pricing'),
    (">Instant Quote<", ">Start your case<"),            # nav and closing CTA
    (">Instant quote<", ">See what you’d keep<"),         # hero button
    ("We’re putting an end to the Brutal Renewal.", "We’re putting an end to high legal fees."),
    ("You know what’s absurd? A surprise 20% hike on your team’s group plan. But that’s commonplace today. That’s why we built Stack.",
     "We win when you win. Simple as that. $0 down. Personal injury representation with the fee published up front. Move the slider, see what you’d keep."),
    (">Set a budget.<", ">Know your fee<"),
    (">Skip the headache.<", ">before you start.<"),
    ("Give your team an allowance for health benefits and they’ll choose a plan that’s right for them. You pick a budget. Stack handles the rest.",
     "Most people never find out what a lawyer will cost until the case is over. We think that’s backwards. The fee is a fixed percentage, published on this page, agreed in writing before we lift a finger."),
    ("Set your benchmark plan and contribution to see your budget. You’re in total control.",
     "Slide to the amount you expect to recover. We’ll show you our fee and what you keep, next to what a typical firm would charge."),
    (">Your team shops for benefits.<", ">Tell us what happened.<"),
    ("Each employee builds a stack of health benefits that’s right for them.",
     "Answer a short set of questions online or on WhatsApp, at your own pace. Upload what you have: photos, police report, medical bills."),
    # the mock app card inside step 2
    (">Maria R.<", ">Your case<"), (">Designer<", ">Car accident<"), (">Full-Time<", ">25% fee<"),
    (">$575/mo<", ">$75,000<"), (">Total Allowance<", ">What you keep<"), (">Maria’s Stack<", ">Your documents<"),
    (">Stackables<", ">Uploaded<"), (">Whoop<", ">Police report<"), (">Carbon Health<", ">Medical bills<"),
    (">Stack Save HSA<", ">Photos<"), (">$50 Employer + $50 Maria<", ">Fee: 25% when we win<"),
    (">Pre-Tax Savings<", ">Agreed in writing<"), (">Stack Pay<", ">Pay nothing today<"),
    (">0% Interest<", ">$0 down<"), (">Pay over time<", ">$50 per hour option<"), (">Coming Soon<", ">To confirm<"),
    (">Dental Plan<", ">Dental malpractice<"), (">Family Plan<", ">33% when we win<"),
    (">Silver HMO Family Plan<", ">25% when we win<"), (">health Plan<", ">Car accident<"), (">Health Premium<", ">Our fee<"),
    (">Bronze<", ">Car 25%<"), (">Silver<", ">Medical 33%<"), (">Gold<", ">Dental 33%<"),   # pill variants outside the card
    # logo rows kept as tiles; headings say what they are
    (">Our trusted partners<", ">Partner logos (placeholder tiles)<"),
    (">Insurance carriers available through stack<", ">One published rate for every kind of case. Car accidents 25% · Medical and dental malpractice 33% · $0 down<"),
    # we win when
    ("We win when you and your team are <span", "We win when <span"),
    (">happy.</span>", ">you win.</span>"),
    ("We’re not selling your team a plan. We’re helping them find the right one.",
     "Our fee is a percentage of your recovery. That means we only do well when you do."),
    (">No conflicts.<", ">No hourly billing.<"), (">No asterisks.<", ">No surprises.<"),
    (">Doug Buckley<", ">Client testimonial<"), (">Black Kahawa Coffee<", ">Placeholder until we have real ones<"),
    # quote carousel
    (">We make an instant impact<", ">Lower fees aren’t a gimmick. They’re a design.<"),
    ('We make an <br class="framer-text">instant impact', 'Lower fees aren’t a gimmick.<br class="framer-text">They’re a design.'),
    ("“I renewed the same plan four years in a row because changing felt impossible. Stack makes it feel possible.”",
     "Traditional firms charge high percentages because they run on paperwork and hours. We built the firm around technology that handles the intake, the document assembly and the case tracking."),
    ("“Our renewal rates have been 15 to 20% year over year, which is just asinine, but you know, that's life.”",
     "Our attorney spends time on your case, not on admin. That’s the saving we pass on."),
    ("“It’s all just so much busy work.”", "$0 down. $50 per hour or 25% of what we recover. 33% for medical and dental malpractice."),
    ("“We’ve been hit the last two years with 20% increases in terms of our premiums, year over year, and those costs compound.”",
     "Client testimonial placeholder. Real quotes only, once we have them."),
    ("“There are real challenges to fitting a one-size-fits-all type of deal for our overall demographic.”",
     "Client testimonial placeholder. Real quotes only, once we have them."),
    (">General Contractor (9 employees)<", ">Why our fee is lower<"), (">Architecture Firm (28 employees)<", ">Why our fee is lower<"),
    (">Law Firm (4 employees)<", ">Published rates<"), (">Creative Agency (70 employees)<", ">Placeholder<"), (">Pizza Chain (110 employees)<", ">Placeholder<"),
    (">Head of HR<", ">Case type<"), (">Owner<", ">Case type<"),
    # closing
    ('You’ve got a business<br class="framer-text">to run. Let Stack handle the benefits part.', 'You’ve been through enough.<br class="framer-text">Let us handle the legal part.'),
    # footer
    (">Privacy Policy<", ">Privacy<"), (">Terms of Use<", ">Terms<"),
    ("© 2026 Stack Healthcare, Inc. All rights reserved.", f"© 2026 {FIRM}. All rights reserved."),
]

SCOPED = {
    "SET A BUDGET": [
        (">You set the budget.<", ">What would you actually take home?<"),
    ],
    "WE BUILT STACK": [
        ("We built Stack to give you and your team ", "Three steps. "),
        (">control</span>.", ">No waiting room</span>."),
        (">You set the budget.<", ">1. Tell us what happened.<"),
        ("Pick a monthly amount you can contribute. That’s your number. It doesn’t move unless you want it to. No surprise renewals.",
         "Answer a short set of questions online or on WhatsApp, at your own pace. Upload what you have: photos, police report, medical bills. If something is missing, we’ll ask."),
        (">Your team builds their plan.<", ">2. We build your case.<"),
        ("Stack guides each employee to coverage that fits them like their favorite pair of pants. If they're HSA-eligible, we help them maximize HSA funding to build a healthier financial future.",
         "Our system organises your facts and documents and prepares the paperwork. Our attorney reviews every case and makes every legal decision."),
        (">The plan goes with them.<", ">3. We pursue your recovery.<"),
        ("If someone leaves your team, the plan leaves with them, because it’s their plan. That’s how insurance should work.",
         "You see the fee before we start. You see what you keep when we win."),
    ],
}

FOOTER_DISCLAIMER = (
    f'{FIRM} · [STREET ADDRESS, CITY, STATE ZIP] · Text or call [PHONE]. '
    f'Attorney responsible for this website: [ATTORNEY NAME, BAR NUMBER], licensed in [STATE]. '
    f'Attorney advertising. Prior results do not guarantee a similar outcome. Fee percentages are subject to a written fee agreement. The calculator is illustrative only.'
)

# The step-1 card's insides were drawn by Framer's bundle on the live site (the
# $3,744 budget, the 80% slider). This is our version with Tim's numbers.
CALC_HTML = """
<div class="pi-c" data-pi-calc>
  <div class="pi-c-row pi-c-top">
    <div><div class="pi-c-label">What you get when we win</div><div class="pi-c-big" data-out="keep">$75,000</div></div>
    <div class="pi-c-tags"><span>$0 down</span><span data-out="ratetag">25% fee</span></div>
  </div>
  <div class="pi-c-row pi-c-line"><div class="pi-c-label">Case type</div><div class="pi-c-val">$50 / hour option</div></div>
  <div class="pi-c-pills" role="group" aria-label="Case type">
    <button type="button" class="pi-c-pill is-on" data-rate="0.25">Car 25%</button>
    <button type="button" class="pi-c-pill" data-rate="0.33">Medical 33%</button>
    <button type="button" class="pi-c-pill" data-rate="0.33">Dental 33%</button>
  </div>
  <div class="pi-c-row pi-c-line"><label class="pi-c-label" for="__ID__">Expected award</label><div class="pi-c-val" data-out="amount">$100,000</div></div>
  <input class="pi-c-range" id="__ID__" type="range" min="10000" max="1000000" step="1000" value="100000" aria-valuetext="$100,000">
  <div class="pi-c-foot"><div class="pi-c-next">Next, tell us what happened.</div><a class="pi-c-btn" href="#product-step-2">Step 2</a></div>
</div>
"""

CASE_HTML = """
<div class="pi-case" data-pi-case hidden>
  <div class="pi-case-head"><div><div class="pi-case-name">Your case</div><div class="pi-c-label">Car accident · 25% fee</div></div><div><div class="pi-c-big" style="font-size:26px">$75,000</div><div class="pi-c-label" style="text-align:right">What you keep</div></div></div>
  <div class="pi-c-label">Your documents</div>
  <div class="pi-case-item"><span class="pi-case-ic" style="background:#ffe435">&#9776;</span><div><b>Uploaded</b><span>Police report · Medical bills · Photos</span></div></div>
  <div class="pi-case-item"><span class="pi-case-ic" style="background:#ffa9d8">&#10003;</span><div><b>Fee: 25% when we win</b><span>Agreed in writing</span></div></div>
  <div class="pi-case-item"><span class="pi-case-ic" style="background:#a9d300">$</span><div><b>Pay nothing today</b><span>$0 down · $50 per hour option</span></div></div>
  <div class="pi-case-item"><span class="pi-case-ic" style="background:#f97815">33</span><div><b>Medical and dental malpractice</b><span>33% when we win</span></div></div>
</div>
"""

MOTION_CSS = """
<style id="pi-clone-motion">
.framer-xvfz0d,.framer-xvfz0d *{pointer-events:auto}
html{scroll-behavior:smooth}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
/* scroll-in reveals: hidden only once our script has marked the page as scripted */
.js [style*="--pi-appear"]{opacity:0!important;transform:translateY(var(--pi-appear))!important;transition:opacity .8s cubic-bezier(.2,.7,.2,1),transform .8s cubic-bezier(.2,.7,.2,1)}
.js [style*="--pi-appear"].pi-in{opacity:1!important;transform:none!important}
@media(prefers-reduced-motion:reduce){.js [style*="--pi-appear"]{opacity:1!important;transform:none!important;transition:none}}
/* Nav */
.pi-wordmark{font:800 22px/1 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.02em;color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);white-space:nowrap;text-decoration:none}
.framer-e8x4r3 .hidden-yycdle{display:flex!important}
.framer-e8x4r3 button{display:none!important}
.framer-e8x4r3{transition:background-color .2s}
.framer-e8x4r3.pi-nav-solid{background:rgba(247,245,239,.94);backdrop-filter:blur(8px)}
/* Footer: the bundle revealed it from behind the page; show it in flow */
.framer-1ebd1db,.framer-TzIF9 .framer-1ebd1db{position:relative!important;height:auto!important;width:100%!important;flex:none!important;padding:120px 0 56px!important;bottom:auto!important}
.framer-1w3xnl7,.framer-TzIF9 .framer-1w3xnl7{height:auto!important;flex:none!important;width:100%!important}
.framer-8pye7d,.framer-TzIF9 .framer-8pye7d{width:auto!important;max-width:60%!important;height:auto!important;flex:none!important}
.framer-whz10a,.framer-TzIF9 .framer-whz10a{width:auto!important;max-width:420px!important;height:auto!important;flex:none!important}
.framer-xj49yz,.framer-TzIF9 .framer-xj49yz{height:auto!important;overflow:visible!important}
.framer-nh45d3,.framer-TzIF9 .framer-nh45d3{position:relative!important;top:auto!important;height:auto!important;width:100%!important}
.pi-footer-mark{font:800 clamp(56px,12vw,180px)/.9 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.04em;color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);margin:0}
/* Elements the bundle faded in that are not scroll reveals */
[data-framer-name="TRUSTED PARTNERS"] div,[data-framer-name="TRUSTED PARTNERS"] ul,[data-framer-name="TRUSTED PARTNERS"] li,[data-framer-name="Tabs"],[data-framer-name="SET A BUDGET"] [style*="opacity:0"]{opacity:1!important}
/* Logo ticker */
[data-framer-name="TRUSTED PARTNERS"] .framer-100iuxi{overflow:hidden!important}
.pi-marquee{animation:pi-marquee 28s linear infinite;width:max-content!important;transform:none!important}
@keyframes pi-marquee{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media(prefers-reduced-motion:reduce){.pi-marquee{animation:none}}
/* Quote carousel */
.pi-track{overflow-x:auto!important;scroll-snap-type:x mandatory;scrollbar-width:none;-webkit-overflow-scrolling:touch;scroll-behavior:smooth}
.pi-track::-webkit-scrollbar{display:none}
.pi-track > *{scroll-snap-align:start}
[data-framer-name="Arrow Left"],[data-framer-name="Arrow Right"]{cursor:pointer}
/* Calculator card */
.pi-c{width:100%;display:flex;flex-direction:column;gap:14px;font-family:"Instrument Sans",system-ui,sans-serif;color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);text-align:left}
.pi-c-row{display:flex;justify-content:space-between;align-items:flex-end;gap:12px}
.pi-c-line{border-top:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb);padding-top:14px;align-items:center}
.pi-c-label{font-size:12px;color:#5f564a;line-height:1.3}
.pi-c-big{font:800 36px/1 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.02em;margin-top:6px;font-variant-numeric:tabular-nums}
.pi-c-val{font:700 15px/1 "Instrument Sans",system-ui,sans-serif;font-variant-numeric:tabular-nums;white-space:nowrap}
.pi-c-tags{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.pi-c-tags span{font:600 11px/1 "Instrument Sans",system-ui,sans-serif;background:var(--token-4c494f9f-03b3-4eac-88e8-f5161b116659,#f4efe1);border-radius:6px;padding:6px 8px;white-space:nowrap}
.pi-c-pills{display:flex;background:var(--token-4c494f9f-03b3-4eac-88e8-f5161b116659,#f4efe1);border-radius:999px;padding:5px;gap:4px}
.pi-c-pill{flex:1;border:0;background:transparent;border-radius:999px;padding:11px 6px;font:700 13px/1 "Instrument Sans",system-ui,sans-serif;color:inherit;cursor:pointer;min-height:38px}
.pi-c-pill.is-on{background:var(--token-dfd7ceb1-6225-41fe-9a08-4ed6d573c4d7,#ffe435)}
.pi-c-pill:focus-visible,.pi-c-range:focus-visible,.pi-c-btn:focus-visible{outline:3px solid #140c0a;outline-offset:2px}
.pi-c-range{width:100%;accent-color:#140c0a;height:32px;cursor:pointer;margin:0}
.pi-c-foot{border-top:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb);padding-top:16px;display:flex;flex-direction:column;align-items:center;gap:10px}
.pi-c-next{font-size:12px;color:#5f564a}
.pi-c-btn{display:block;width:100%;text-align:center;background:var(--token-dfd7ceb1-6225-41fe-9a08-4ed6d573c4d7,#ffe435);border-radius:999px;padding:13px 0;font:700 12px/1 "Instrument Sans",system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:inherit;text-decoration:none}
.pi-case{width:100%;display:flex;flex-direction:column;gap:12px;font-family:"Instrument Sans",system-ui,sans-serif;color:#140c0a;text-align:left}
.pi-case[hidden]{display:none}
.pi-case-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;border-bottom:1px solid #c9c4bb;padding-bottom:12px}
.pi-case-name{font:800 18px/1.1 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif}
.pi-case-item{display:flex;gap:12px;align-items:center;background:#f4efe1;border-radius:12px;padding:12px}
.pi-case-item b{display:block;font-size:14px}
.pi-case-item span:last-child{font-size:12px;color:#5f564a}
.pi-case-ic{flex:none;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font:700 13px/1 "Instrument Sans",system-ui,sans-serif}
.pi-c,.pi-case{transition:opacity .35s ease}
/* Pinned scroll sections: original geometry at desktop, driven by our script */
@media(min-width:1200px){
  .framer-1ccwr6f,.framer-hd6jU .framer-1ccwr6f{height:300vh!important;position:relative!important;display:block!important;align-content:start!important;padding:0!important}
  /* heading pinned in a left column, the card stack pinned beside it on the right; both release together */
  .framer-1tvol1x,.framer-hd6jU .framer-1tvol1x{position:absolute!important;top:0!important;left:0!important;bottom:auto!important;height:100%!important;width:38%!important;display:block!important;padding:0 32px 0 0!important;box-sizing:border-box;pointer-events:none;overflow:visible!important}
  .framer-1tvol1x .framer-18msark,.framer-hd6jU .framer-1tvol1x .framer-18msark{position:sticky!important;top:0!important;height:100vh!important;min-height:0!important;width:100%!important;display:flex!important;flex-direction:column!important;align-items:flex-start!important;justify-content:center!important;padding-top:110px!important;box-sizing:border-box}
  .framer-1tvol1x .framer-1cw2mkh{display:none!important}
  .framer-1tvol1x .framer-t9ypgs{justify-content:flex-start!important}
  .framer-1tvol1x .framer-1r7kqfy-container{width:100%!important;max-width:520px}
  .framer-1tvol1x .framer-1r7kqfy-container *{text-align:left!important}
  .framer-9g4wr0,.framer-hd6jU .framer-9g4wr0{position:absolute!important;top:0!important;left:38%!important;width:62%!important;height:100%!important;display:block!important;padding:0!important}
  .framer-9g4wr0 > *,.framer-hd6jU .framer-9g4wr0 > *{position:sticky!important;top:var(--pi-slot)!important;bottom:auto!important;height:calc(100vh - var(--pi-slot))!important;min-height:0!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;align-items:center!important;width:100%!important;padding:0!important}
  .framer-9g4wr0 .framer-126fhqh,.framer-9g4wr0 .framer-1t0z88y{width:100%!important}
  .framer-9g4wr0 [data-framer-name^="Card"]{width:100%!important;max-width:none!important;padding:64px 48px!important;transition:transform .15s linear;will-change:transform;box-shadow:0 20px 60px rgba(20,12,10,.12)}
  .framer-1ccwr6f{--pi-slot:calc(50vh - 200px)}
  .framer-71z80s,.framer-hd6jU .framer-71z80s{height:200vh!important;padding:0!important}
  .framer-882vmr,.framer-hd6jU .framer-882vmr{position:sticky!important;top:0!important;height:100vh!important}
  .framer-18uk1a7,.framer-hd6jU .framer-18uk1a7{height:1px!important}
  .framer-1j23hd2-container{transition:transform .1s linear}
}
@media(max-width:1199.98px){
  [data-framer-name="MAIN"] [data-framer-name="Absolute"]{position:relative!important;inset:auto!important;transform:none!important}
  [data-framer-name="MAIN"] [data-framer-name="Viewport"]{height:auto!important;min-height:0!important;overflow:visible!important}
  [data-framer-name="Card 1"],[data-framer-name="Card 2"],[data-framer-name="Card 3"]{transform:none!important}
  /* below desktop the layers flow one after another; the title layer and each card wrapper lose their viewport-tall runway */
  .framer-1tvol1x,.framer-hd6jU .framer-1tvol1x{height:auto!important;min-height:0!important;padding-bottom:40px}
  .framer-9g4wr0,.framer-hd6jU .framer-9g4wr0{height:auto!important;gap:24px!important;align-items:center!important}
  .framer-9g4wr0 > *{position:relative!important;height:auto!important;top:auto!important;display:flex!important;justify-content:center;width:100%!important}
  [data-framer-name="WE BUILT STACK"] [data-framer-name="Sticky"]{position:relative!important;top:auto!important;height:auto!important;min-height:0!important}
  [data-framer-name="WE BUILT STACK"] [data-framer-name="spacer"]{display:none!important}
  .framer-71z80s{height:auto!important;padding:120px 0!important}
  .framer-882vmr{position:relative!important;height:auto!important;top:auto!important}
  .framer-18uk1a7{height:auto!important}
  .framer-1j23hd2-container{transform:none!important}
  .framer-e8x4r3{padding:14px 16px}
}
@media(max-width:809.98px){
  .framer-e8x4r3 .framer-1ezgx8l{display:none}
  /* phone configurator: Framer's script swapped step 1 and step 2 in one box; show them one after the other */
  [data-framer-name="Container Configurator Mobile 2"]{height:auto!important;min-height:0!important;display:flex!important;flex-direction:column!important;gap:28px!important;align-items:stretch!important}
  [data-framer-name="Container Configurator Mobile 2"] > *{position:relative!important;top:auto!important;left:auto!important;height:auto!important;width:100%!important;transform:none!important}
  .framer-8OGkr .framer-85s22j{position:relative!important;top:auto!important;left:auto!important;right:auto!important}
  .framer-8OGkr{height:auto!important;min-height:0!important}
  .framer-1w3xnl7,.framer-TzIF9 .framer-1w3xnl7{padding:0 20px!important;flex-direction:column!important;align-items:flex-start!important;gap:32px!important}
  .framer-8pye7d,.framer-TzIF9 .framer-8pye7d,.framer-whz10a,.framer-TzIF9 .framer-whz10a{max-width:100%!important}
}
</style>
"""

MOTION_JS = """
<script>
(function () {
  var doc = document.documentElement;
  doc.classList.add('js');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var desktop = function () { return window.innerWidth >= 1200; };
  function clamp(x) { return Math.max(0, Math.min(1, x)); }

  /* 1. Scroll-in reveals (elements the bundle used to fade and lift in) */
  var items = [].slice.call(document.querySelectorAll('[style*="--pi-appear"]'));
  if (reduce || !('IntersectionObserver' in window)) {
    items.forEach(function (el) { el.classList.add('pi-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('pi-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* 2. Pinned card stack and pinned closing image, driven by scroll progress */
  var cards = ['Card 1', 'Card 2', 'Card 3'].map(function (n) { return document.querySelector('[data-framer-name="' + n + '"]'); });
  var cta = document.querySelector('[data-framer-name="CTA"]');
  var ctaImg = cta && cta.querySelector('.framer-1j23hd2-container');
  var ctaContent = cta && cta.querySelector('.framer-18uk1a7');
  var nav = document.querySelector('.framer-e8x4r3');
  function onScroll() {
    if (nav) nav.classList.toggle('pi-nav-solid', window.scrollY > 24);
    if (!desktop() || reduce) {
      cards.forEach(function (c) { if (c) c.style.transform = 'none'; });
      if (ctaImg) ctaImg.style.transform = 'none';
      if (ctaContent) { ctaContent.style.opacity = 1; ctaContent.style.transform = 'none'; }
      return;
    }
    var vh = window.innerHeight;
    cards.forEach(function (c, i) {
      if (!c) return;
      if (i === 0) { c.style.transform = 'none'; return; }
      var r = c.getBoundingClientRect();
      var slot = Math.max(0, vh * 0.5 - 200);                 /* same as --pi-slot in the CSS */
      var p = clamp(1 - (r.top - slot) / (vh - slot));         /* 0 when entering from below, 1 when pinned */
      var sign = i === 1 ? -1 : 1;
      c.style.transform = 'rotate(' + (sign * 10 * (1 - p)).toFixed(2) + 'deg) translateY(' + (40 * (1 - p)).toFixed(1) + 'px)';
      var prev = cards[i - 1];
      if (prev) prev.style.transform = 'scale(' + (1 - 0.06 * p).toFixed(3) + ') translateY(' + (-24 * p).toFixed(1) + 'px)';
    });
    if (cta) {
      var r2 = cta.getBoundingClientRect();
      var p2 = clamp(-r2.top / Math.max(1, r2.height - vh));
      if (ctaImg) ctaImg.style.transform = 'scale(' + (0.3 + 0.7 * p2).toFixed(3) + ')';
      if (ctaContent) { ctaContent.style.opacity = p2.toFixed(3); ctaContent.style.transform = 'scale(' + (0.9 + 0.1 * p2).toFixed(3) + ')'; }
    }
  }
  var step2Text = document.querySelector('[data-framer-name="Container Configurator"]') ? [].slice.call(document.querySelectorAll('[data-framer-name="Text Step 2"]')).filter(function (e) { return e.getBoundingClientRect().height > 0; })[0] : null;
  var swapCalc = document.querySelector('[data-framer-name="Container Configurator"] [data-pi-calc]');
  var swapCase = document.querySelector('[data-framer-name="Container Configurator"] [data-pi-case]');
  function onSwap() {
    if (!step2Text || !swapCalc || !swapCase) return;
    var show2 = desktop() && step2Text.getBoundingClientRect().top < window.innerHeight * 0.55;
    swapCase.hidden = !show2; swapCalc.style.display = show2 ? 'none' : '';
  }
  window.addEventListener('scroll', onSwap, { passive: true }); window.addEventListener('resize', onSwap); onSwap();
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();

  /* 3. Logo ticker */
  var track = document.querySelector('[data-framer-name="TRUSTED PARTNERS"] .framer-100iuxi > div');
  if (track && track.children.length) {
    track.innerHTML += track.innerHTML;   /* seamless loop */
    track.classList.add('pi-marquee');
  }

  /* 4. Quote carousel arrows */
  var impact = document.querySelector('[data-framer-name="INSTANT IMPACT"]');
  if (impact) {
    var statements = [].slice.call(impact.querySelectorAll('[data-framer-name="Statement Container"]')).filter(function (s) { return s.getBoundingClientRect().width > 0; });
    if (statements.length > 1) {
      var t = statements[0];
      while (t.parentElement && t.parentElement !== impact && !statements.every(function (s) { return t.parentElement.contains(s) && s !== t.parentElement; })) t = t.parentElement;
      var trackEl = t.parentElement;
      while (trackEl && trackEl !== impact && trackEl.children.length < 2) trackEl = trackEl.parentElement;
      if (trackEl && trackEl !== impact) {
        trackEl.classList.add('pi-track');
        var step = function () { return statements[0].getBoundingClientRect().width + 24; };
        var left = impact.querySelector('[data-framer-name="Arrow Left"]'), right = impact.querySelector('[data-framer-name="Arrow Right"]');
        if (left) left.addEventListener('click', function () { trackEl.scrollBy({ left: -step(), behavior: 'smooth' }); });
        if (right) right.addEventListener('click', function () { trackEl.scrollBy({ left: step(), behavior: 'smooth' }); });
      }
    }
  }

  /* 5. Calculator cards (one per breakpoint variant) */
  function money(n) { return '$' + Math.round(n).toLocaleString('en-US'); }
  [].forEach.call(document.querySelectorAll('[data-pi-calc]'), function (c) {
    var range = c.querySelector('.pi-c-range'), pills = c.querySelectorAll('.pi-c-pill');
    var rate = 0.25;
    function update() {
      var amount = Number(range.value);
      c.querySelector('[data-out="amount"]').textContent = money(amount);
      c.querySelector('[data-out="keep"]').textContent = money(amount - amount * rate);
      c.querySelector('[data-out="ratetag"]').textContent = Math.round(rate * 100) + '% fee';
      range.setAttribute('aria-valuetext', money(amount));
    }
    [].forEach.call(pills, function (p) {
      p.addEventListener('click', function () {
        [].forEach.call(pills, function (q) { q.classList.remove('is-on'); });
        p.classList.add('is-on'); rate = Number(p.getAttribute('data-rate')); update();
      });
    });
    range.addEventListener('input', update);
    update();
  });
})();
</script>
"""


def replace_all(html, pairs, where, required=True):
    """Apply swaps. Section swaps must all hit; page-wide ones may miss when the
    text they target lived inside a card we replaced. The leftover scan at the
    end is what guarantees no Stack wording survives."""
    skipped = []
    for old, new in pairs:
        if old not in html:
            if required:
                raise SystemExit(f"build_clone: text not found in {where}: {old[:80]!r}")
            skipped.append(old[:40])
            continue
        html = html.replace(old, new)
    if skipped:
        print(f"  (no longer present, skipped: {len(skipped)} swaps)")
    return html


def mark_appear(html):
    """Turn the bundle's initial 'hidden, 40px lower' inline styles into a marker
    our CSS and script use for scroll-in reveals. Without script the element is
    simply visible."""
    return re.sub(r"will-change:transform;opacity:0(?:\.001)?;transform:translateY\((\d+)px\)",
                  r"opacity:1;transform:none;--pi-appear:\1px", html)


def main():
    src = SRC.read_text(encoding="utf-8")
    t = Tree(src)

    # --- pass 1: section-scoped text swaps (whole sections, never nested)
    edits = []
    for name, pairs in SCOPED.items():
        n = t.find(by_name(name))
        edits.append((n["start"], n["end"], replace_all(src[n["start"]:n["end"]], pairs, name)))
    for start, end, new in sorted(edits, key=lambda e: -e[0]):
        src = src[:start] + new + src[end:]

    # --- pass 2: structural edits on a fresh parse, applied from the end
    t = Tree(src)
    edits = []
    disc = t.find(by_name("Disclaimer"))
    disc_p = [c for c in disc["children"] if c["tag"] == "p"][0]
    open_tag = src[disc_p["start"]:src.find(">", disc_p["start"]) + 1]
    edits.append((disc_p["start"], disc_p["end"], f"{open_tag}{FOOTER_DISCLAIMER}</p>"))
    mark = t.find(by_class("framer-8pye7d"))
    edits.append((mark["start"], mark["end"], f'<div class="framer-8pye7d"><p class="pi-footer-mark">{FIRM}</p></div>'))
    # Step-2 cards carry a copy of the step-1 calculator that the bundle used to
    # slide away; drop those copies so step 2 shows only the case summary.
    page2 = [n for n in t.find_all(by_name("Product - Page 2"))
             if any(k in (n["attrs"].get("class") or "") for k in ("framer-lOaxc", "framer-8OGkr"))]
    doomed = set()
    for pg in page2:
        for c in pg["children"]:
            cls = c["attrs"].get("class") or ""
            if "framer-85s22j" in cls or "framer-lyo4iw" in cls:
                doomed.add(c["start"])
                edits.append((c["start"], c["end"], ""))
    # calculator card insides, every breakpoint variant (desktop/tablet use
    # .framer-85s22j, the phone variant uses .framer-lyo4iw)
    cards = [n for n in t.find_all(lambda n: any(k in (n["attrs"].get("class") or "").split() for k in ("framer-85s22j", "framer-lyo4iw")))
             if n["start"] not in doomed]
    desktop_cards = {c["start"] for cfg in t.find_all(by_name("Container Configurator"))
                     for c in t.find_all(by_class("framer-85s22j"), cfg["children"])}
    for i, card in enumerate(cards):
        inner_open = src.find(">", card["start"]) + 1
        inner_close = src.rfind("<", 0, card["end"])
        panel = CASE_HTML if card["start"] in desktop_cards else ""
        edits.append((inner_open, inner_close, CALC_HTML.replace("__ID__", f"pi-award-{i}") + panel))
    # hero title block gets a reveal on load
    hero_title = t.find(by_name("Title Block"))
    tag_end = src.find(">", hero_title["start"]) + 1
    tag = src[hero_title["start"]:tag_end]
    edits.append((hero_title["start"], tag_end, tag.replace('style="', 'style="--pi-appear:24px;', 1) if 'style="' in tag else tag[:-1] + ' style="--pi-appear:24px"' + ">"))
    html = src
    for start, end, new in sorted(edits, key=lambda e: -e[0]):
        html = html[:start] + new + html[end:]

    # --- global swaps
    html = replace_all(html, GLOBAL, "page", required=False)
    html = html.replace('<div class="framer-DJN29 framer-cqcfvd"></div>', f'<span class="pi-wordmark">{FIRM}</span>')
    html = re.sub(r'<a class="framer-18cgtl3 framer-1f2myp"[^>]*>.*?</a>', "", html, flags=re.S)
    html = re.sub(r'<a name="Nav Watch a demo" class="framer-cLKaN', '<a href="#hero" name="Start your case" class="framer-cLKaN', html, count=1)

    # --- scripts and Stack metadata out, ours in
    html = re.sub(r"<script\b.*?</script>", "", html, flags=re.S)
    html = re.sub(r"<meta\b[^>]*(?:name|property)=\"(?:description|robots|og:[^\"]+|twitter:[^\"]+|framer-search-index[^\"]*|generator)\"[^>]*>", "", html)
    html = re.sub(r"<link\b[^>]*rel=\"(?:canonical|icon)\"[^>]*>", "", html)
    html = re.sub(r"<title>.*?</title>", f"<title>{CONFIG['title']}</title>", html, count=1, flags=re.S)
    schema_block = re.search(r"<script type=\"application/ld\+json\">.*?</script>", SCHEMA.read_text(encoding="utf-8"), re.S).group(0)
    meta = (f'<meta name="description" content="{CONFIG["description"]}">'
            f'<link rel="canonical" href="https://{CONFIG["domain"]}/">'
            f'<meta name="robots" content="noindex, nofollow">{schema_block}{MOTION_CSS}')
    html = html.replace("</head>", meta + "</head>", 1)
    html = html.replace(' data-framer-hydrate-v2="', ' data-x-hydrate="', 1)
    html = html.replace("<!-- Made in Framer · framer.com -->", f"<!-- {FIRM} prototype: mystack.com clone with text swapped by tools/build_clone.py. Do not edit by hand. -->", 1)
    html = html.replace("</body>", MOTION_JS + "</body>", 1)

    # --- motion markers, then make everything else the bundle hid visible
    html = derevelo(html)
    html = mark_appear(html)
    html = unhide(html)
    html = strip_comments(html)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    body = html[html.find("<body"):]
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S)))
    for bad in ("Brutal Renewal", "Stack Health", "ICHRA", "$500", "Instant Quote", "Instant quote", "For Brokers", "benefits", "renewal", "employee", "$3,744", "Bronze", "Silver", "Gold", "Maria", "Monthly Budget", "benchmark"):
        if bad.lower() in text.lower():
            i = text.lower().find(bad.lower())
            raise SystemExit(f"build_clone: leftover {bad!r}: ...{text[max(0,i-60):i+60]}...")
    print(f"built {OUT.relative_to(ROOT)}: {len(html):,} bytes; reveals: {html.count('--pi-appear')}; calculators: {html.count('data-pi-calc')-1}; step-2 duplicates removed: {len(doomed)}; h1: {html.count('<h1')}")


if __name__ == "__main__":
    main()
