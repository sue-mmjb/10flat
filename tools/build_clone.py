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
from build_site import Tree, by_name, by_class, derevelo, unhide, strip_comments, CONFIG, SCHEMA, FAQ_GROUPS, sync_schema_faq  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "mystack-index.html"
OUT = ROOT / "site" / "index.html"
FIRM = CONFIG["firm"]
BRAND = CONFIG.get("brand", "10flat")

# ----------------------------------------------------------------------------
# Text swaps. Left = exact text in the clone (curly quotes as in the source).
# ----------------------------------------------------------------------------
GLOBAL = [
    ('href="./brokers">For Brokers', 'href="#we-win-when">Pricing'),
    (">Instant Quote<", ">Start your case<"),            # nav and closing CTA
    (">Instant quote<", ">See your fee<"),                # hero button
    ("We’re putting an end to the Brutal Renewal.", "We’re putting an end to high legal fees."),
    ("You know what’s absurd? A surprise 20% hike on your team’s group plan. But that’s commonplace today. That’s why we built Stack.",
     "We win when you win. Simple as that. Most injury firms take 33–40% of your settlement. We take 10%, and it stays 10% even if we go to trial. Technology does the paperwork. Your lawyer does the lawyering."),
    (">Set a budget.<", ">Less paperwork.<"),
    (">Skip the headache.<", ">More money to you.<"),
    ("Give your team an allowance for health benefits and they’ll choose a plan that’s right for them. You pick a budget. Stack handles the rest.",
     "When a firm charges 33–40%, that fee pays for paperwork staff, billboards and expensive offices. None of that makes your case stronger, but it all comes out of your settlement. We charge less because we spend less, not because we do less. Our fee is 10%, calculated after case costs, and it never goes up, even at trial."),
    ("Set your benchmark plan and contribution to see your budget. You’re in total control.",
     "Type or slide to a settlement amount. You’ll see our 10% fee next to the fee at a typical 33% firm, and how much more of your settlement you keep."),
    (">Your team shops for benefits.<", ">Tell us what happened.<"),
    ("Each employee builds a stack of health benefits that’s right for them.",
     "Message us on WhatsApp. Tell us what happened and send any photos or documents you have. A Texas attorney will review your case, usually [the same day]. It’s free to find out if we can help."),
    # the mock app card inside step 2 (phone and tablet variants): the case dashboard from the 10flat brief
    (">Maria R.<", ">Your case<"), (">Designer<", ">Car accident<"), (">Full-Time<", ">10% fee, after costs<"),
    (">$575/mo<", ">$85,500<"), (">Total Allowance<", ">After fee and costs (example)<"), (">Maria’s Stack<", ">Documents received<"),
    (">Stackables<", ">View your documents<"), (">Whoop<", ">Police report<"), (">Carbon Health<", ">Medical bills · Photos<"),
    (">Stack Save HSA<", ">Your fee: 10%<"), (">$50 Employer + $50 Maria<", ">Never goes up, even at trial<"),
    (">Pre-Tax Savings<", ">Calculated after case costs<"), (">Stack Pay<", ">If there is no recovery<"),
    (">0% Interest<", ">No fee<"), (">Pay over time<", ">No case costs<"), (">Coming Soon<", ">No decision needed right now<"),
    (">Dental Plan<", ">Your attorney<"), (">Family Plan<", ">Licensed in Texas<"),
    (">Silver HMO Family Plan<", ">Next step: awaiting medical records<"), (">health Plan<", ">Car accident<"), (">Health Premium<", ">Current stage: evidence collection<"),
    (">Bronze<", ">Car accident<"), (">Silver<", ">Medical injury<"), (">Gold<", ">Dental injury<"),   # pill variants outside the card
    # logo rows kept as tiles; headings say what they are
    (">Our trusted partners<", ">Partner logos (placeholder tiles)<"),
    (">Insurance carriers available through stack<", ">One fee: 10% of your recovery, calculated after case costs. It never goes up, even at trial. Car accidents · Medical injury · Dental injury. Se habla español.<"),
    # we win when
    ("We win when you and your team are <span", "We win when <span"),
    (">happy.</span>", ">you win.</span>"),
    ("We’re not selling your team a plan. We’re helping them find the right one.",
     "The insurance company decides how much to pay based on your case, not on what your lawyer charges. A lower fee doesn’t mean a smaller settlement. It means you keep more of it."),
    (">No conflicts.<", ">No markup on costs.<"), (">No asterisks.<", ">No admin fees.<"),
    (">Doug Buckley<", ">Client testimonial<"), (">Black Kahawa Coffee<", ">Placeholder until we have real ones<"),
    # quote carousel
    (">We make an instant impact<", ">We charge less because we spend less.<"),
    ('We make an <br class="framer-text">instant impact', 'We charge less because<br class="framer-text">we spend less.'),
    ("“I renewed the same plan four years in a row because changing felt impossible. Stack makes it feel possible.”",
     "When a firm charges 33–40%, that fee pays for much more than your lawyer’s time. It pays for staff who type letters and track deadlines by hand, for billboards and TV ads, and for expensive offices. None of that makes your case stronger. But it all comes out of your settlement."),
    ("“Our renewal rates have been 15 to 20% year over year, which is just asinine, but you know, that's life.”",
     "Technology handles the paperwork. It organises your photos, police report and medical records the moment you send them, requests missing records, builds a timeline of your treatment, totals your bills and tracks every deadline. Your lawyer does the lawyering. A licensed Texas attorney reviews and approves every important step."),
    ("“It’s all just so much busy work.”", "A broken arm is worth the same whether your lawyer charges 10% or 40%. The insurance company decides how much to pay based on your case, not on what your lawyer charges. What the fee changes is how much of that settlement you keep."),
    ("“We’ve been hit the last two years with 20% increases in terms of our premiums, year over year, and those costs compound.”",
     "You see everything on your phone: every document, every update, every offer. You hear from us first. You choose your attorney from the team members available for your case. For every offer we show what you’d actually keep. You decide, with a call from your attorney before you do. Se habla español."),
    ("“There are real challenges to fitting a one-size-fits-all type of deal for our overall demographic.”",
     "10% fee, calculated after case costs. It never goes up, even at trial. No fee and no costs if we don’t recover money for you. No markup on case costs. No admin fees. A licensed Texas attorney is responsible for your case. No pressure. It’s your case and your decision."),
    (">General Contractor (9 employees)<", ">Where your money goes at a typical firm<"), (">Architecture Firm (28 employees)<", ">What we do differently<"),
    (">Law Firm (4 employees)<", ">Lower percentage, not lower amount<"), (">Creative Agency (70 employees)<", ">Better service, not less service<"), (">Pizza Chain (110 employees)<", ">Our promises<"),
    (">Head of HR<", f">{BRAND}<"), (">Owner<", f">{BRAND}<"),
    # closing
    ('You’ve got a business<br class="framer-text">to run. Let Stack handle the benefits part.', 'You’ve been through enough.<br class="framer-text">Let us handle the legal part.'),
    # footer
    (">Privacy Policy<", ">Privacy<"), (">Terms of Use<", ">Terms<"),
    ("© 2026 Stack Healthcare, Inc. All rights reserved.", f"© 2026 {BRAND}. All rights reserved."),
]

SCOPED = {
    "SET A BUDGET": [
        (">You set the budget.<", ">See what you keep.<"),
    ],
    "WE BUILT STACK": [
        ("We built Stack to give you and your team ", "Three steps. "),
        (">control</span>.", ">No waiting room</span>."),
        (">You set the budget.<", ">1. Tell us what happened.<"),
        ("Pick a monthly amount you can contribute. That’s your number. It doesn’t move unless you want it to. No surprise renewals.",
         "Message us on WhatsApp. Tell us what happened and send any photos or documents you have. A Texas attorney will review your case, usually [the same day]. It’s free to find out if we can help."),
        (">Your team builds their plan.<", ">2. We build your case.<"),
        ("Stack guides each employee to coverage that fits them like their favorite pair of pants. If they're HSA-eligible, we help them maximize HSA funding to build a healthier financial future.",
         "Our system organises your photos, police report and medical records the moment you send them. It requests missing records, builds a timeline of your treatment, totals your bills, drafts letters and tracks every deadline. A trained case team checks the work."),
        (">The plan goes with them.<", ">3. We pursue your recovery.<"),
        ("If someone leaves your team, the plan leaves with them, because it’s their plan. That’s how insurance should work.",
         "Your attorney spends time where it counts: reviewing your case, advising you and negotiating with the insurance company. For every offer we show what you’d actually keep. You make every settlement decision, with a call from your attorney before you do. If the insurer won’t make a fair offer, we file a lawsuit, and your fee stays 10%."),
    ],
}

FOOTER_DISCLAIMER = (
    f'{FIRM} [PLLC], Texas. '
    'Our fee is 10% of the amount recovered, calculated after case costs are repaid. If there is no recovery, you owe no fee and no case costs. '
    'Medical bills and liens are paid from your recovery. Every case is different, and past results do not guarantee future results. '
    f'{FIRM} uses software, including AI, and a supervised case team to prepare work; a licensed attorney reviews and approves legal work. '
    'Contacting us does not create an attorney-client relationship until a fee agreement is signed. '
    '[Not certified by the Texas Board of Legal Specialization, if applicable.] Attorney advertising. '
    'Typical fee figures based on [Texas Fee Index, date]. The calculator is an example only.'
)

# The step-1 card's insides were drawn by Framer's bundle on the live site (the
# $3,744 budget, the 80% slider). This is our version with Tim's numbers.
CALC_HTML = f"""
<div class="pi-c" data-pi-calc>
  <div class="pi-c-sec pi-c-top">
    <div><div class="pi-c-label">You keep this much more than at a 33% firm</div><div class="pi-c-big" data-out="more">$21,850</div></div>
    <div class="pi-c-tag"><span>10% fee, after case costs</span><i></i><span>Stays 10% at trial</span></div>
  </div>
  <div class="pi-c-sec">
    <div class="pi-c-label">Case type</div>
    <div class="pi-c-pills" role="group" aria-label="Case type">
      <button type="button" class="pi-c-pill is-on">Car accident</button>
      <button type="button" class="pi-c-pill">Medical injury</button>
      <button type="button" class="pi-c-pill">Dental injury</button>
    </div>
  </div>
  <div class="pi-c-sec">
    <div class="pi-c-row"><label class="pi-c-label" for="__ID__-amount">If your case settles for</label><input class="pi-c-amount" id="__ID__-amount" type="text" inputmode="numeric" value="$100,000" autocomplete="off"></div>
    <input class="pi-c-range" id="__ID__" type="range" min="10000" max="1000000" step="1000" value="100000" aria-label="Settlement amount" aria-valuetext="$100,000" style="--p:9.1%">
  </div>
  <div class="pi-c-sec pi-c-rows">
    <div class="pi-c-row"><label class="pi-c-label" for="__ID__-costs">Case costs (example, you can change it)</label><input class="pi-c-amount pi-c-costs" id="__ID__-costs" type="text" inputmode="numeric" value="$5,000" autocomplete="off"></div>
    <div class="pi-c-row"><span class="pi-c-label">Fee at a 33% firm</span><span class="pi-c-val pi-c-dim" data-out="fee33">$31,350</span></div>
    <div class="pi-c-row"><span class="pi-c-label">Fee at {BRAND} (10%)</span><span class="pi-c-val" data-out="fee">$9,500</span></div>
    <div class="pi-c-row"><span class="pi-c-label">You keep, after fee and costs</span><span class="pi-c-val" data-out="keep">$85,500</span></div>
  </div>
  <div class="pi-c-foot">
    <div class="pi-c-next">Next, tell us what happened.</div>
    <a class="pi-c-btn" href="#product-step-2">Start your case</a>
    <p class="pi-c-disc">Fees are figured after case costs at both firms. Medical bills and liens are paid from the settlement the same way at any firm. Example only; every case is different.</p>
  </div>
</div>
"""

CASE_HTML = f"""
<div class="pi-case" data-pi-case hidden>
  <div class="pi-case-head"><div><div class="pi-case-name">Your case</div><div class="pi-c-label">Car accident · 10% fee</div></div><div><div class="pi-c-big" style="font-size:26px">$85,500</div><div class="pi-c-label" style="text-align:right">After fee and costs (example)</div></div></div>
  <div class="pi-c-label">Based on a $100,000 settlement with $5,000 case costs. Medical bills and liens are paid from the recovery.</div>
  <div class="pi-case-item"><span class="pi-case-ic" style="background:#ffe435">&#9776;</span><div><b>Documents received</b><span>Police report · Medical bills · Photos · View your documents</span></div></div>
  <div class="pi-case-item"><span class="pi-case-ic" style="background:#ffa9d8">10</span><div><b>Your fee: 10%</b><span>Calculated after case costs. Never goes up, even at trial.</span></div></div>
  <div class="pi-case-item"><span class="pi-case-ic" style="background:#a9d300">$</span><div><b>If there is no recovery</b><span>No fee and no case costs. No markup on costs. No admin fees.</span></div></div>
  <div class="pi-case-item"><span class="pi-case-ic" style="background:#f97815">&#9679;</span><div><b>Your attorney</b><span>Licensed Texas attorney · Request a call</span></div></div>
  <div class="pi-case-stage"><b>Current stage:</b> Evidence collection · <b>Next step:</b> Awaiting medical records · No decision needed right now</div>
  <div class="pi-case-prem"><b>When an offer arrives</b> you see the offer, the case costs, the 10% fee, your medical bills and liens, and what you’d actually keep. Your attorney calls you before you decide anything.<span class="pi-case-choices"><span class="is-on">Talk to my attorney</span><span>Ask a question</span></span></div>
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
.pi-track > *{scroll-snap-align:start;transform:none!important;opacity:1!important;position:relative!important;top:auto!important;bottom:auto!important;left:auto!important;height:100%!important}  /* the bundle leaves each card at its pre-appear translateX offset, and its carousel variant parks the first card absolutely under the second */
[data-framer-name="Arrow Left"],[data-framer-name="Arrow Right"]{cursor:pointer}
/* Quote cards: the testimonial preset (28px GT Alpina, 72px padding, 400px card) was sized for one-line quotes; ours are paragraphs */
.framer-E2WzL.framer-9l7otk{--1oqahgf:44px 44px 40px 44px!important}
.framer-E2WzL .framer-cn8rb9 p.framer-text.framer-styles-preset-1fc2js5{--framer-font-size:22px;--framer-line-height:1.4em;--framer-letter-spacing:-.15px}
.framer-E2WzL .framer-16qio8u p.framer-text.framer-styles-preset-7jf1zc{--framer-font-size:11px;--framer-letter-spacing:.7px;--framer-line-height:1.3em}
.framer-E2WzL .framer-16qio8u p.framer-text.framer-styles-preset-15qf7x7{--framer-font-size:15px}
.framer-qS6iJ .framer-1dbzg9h{height:auto!important;min-height:400px;align-items:stretch}
@media(max-width:1199px) and (min-width:810px){.framer-E2WzL .framer-cn8rb9 p.framer-text.framer-styles-preset-1fc2js5{--framer-font-size:18px}.framer-E2WzL.framer-9l7otk{--1oqahgf:36px 36px 32px 36px!important}}
@media(max-width:809px){.framer-E2WzL .framer-cn8rb9 p.framer-text.framer-styles-preset-1fc2js5{--framer-font-size:17px;--framer-line-height:1.42em}.framer-E2WzL.framer-9l7otk{--1oqahgf:30px 26px 26px 26px!important}}
/* Step drawings: PNGs at their natural aspect instead of the SVGs' fixed .92 box */
.framer-hd6jU .framer-dlhvuy,.framer-hd6jU .framer-qptr4j,.framer-hd6jU .framer-1xu5j0d{aspect-ratio:auto!important;height:auto!important}
/* FAQ */
.pi-faq-sec{width:100%;padding:120px 24px 100px;box-sizing:border-box;background:#f7f5ef;font-family:"Instrument Sans",system-ui,sans-serif;color:#140c0a;position:relative}
.pi-faq-wrap{max-width:860px;margin:0 auto}
.pi-faq-h{font:800 clamp(40px,5.5vw,72px)/.98 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.02em;margin:0 0 18px}
.pi-faq-lead{font:500 20px/1.4 "GT Alpina Medium","Instrument Sans",serif;margin:0 0 16px;max-width:640px;color:#2d2926}
.pi-faq-g{font:800 26px/1.1 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.01em;margin:52px 0 6px}
.pi-faq{border-bottom:1px solid #c9c4bb}
.pi-faq summary{cursor:pointer;list-style:none;padding:18px 48px 18px 0;position:relative;font:700 17px/1.35 "Instrument Sans",system-ui,sans-serif}
.pi-faq summary::-webkit-details-marker{display:none}
.pi-faq summary::after{content:"+";position:absolute;right:6px;top:50%;transform:translateY(-50%);font:600 28px/1 "Instrument Sans",system-ui,sans-serif}
.pi-faq[open] summary::after{content:"\\2212"}
.pi-faq summary:focus-visible{outline:3px solid #140c0a;outline-offset:3px}
.pi-faq p{margin:0;padding:0 0 20px;font:400 16px/1.55 "Instrument Sans",system-ui,sans-serif;color:#2d2926;max-width:720px}
@media(max-width:809.98px){.pi-faq-sec{padding:72px 20px 56px}.pi-faq-g{font-size:22px;margin-top:40px}.pi-faq summary{font-size:16px}}
/* Accent words in headings: the bundle's 60% yellow on off-white is unreadable; a dark amber keeps the hue at 3.7:1 */
[style*="token-9700579c"]{--token-9700579c-8505-41af-81b6-a348c67b82f2:#9a7a00!important}
/* Calculator card */
.pi-c{width:100%;max-width:430px;margin:0 auto;padding:0 32px;box-sizing:border-box;display:flex;flex-direction:column;font-family:"Instrument Sans",system-ui,sans-serif;color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);text-align:left}
.pi-c-sec{padding:20px 0;border-top:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#e3ded2)}
.pi-c-sec:first-child{border-top:0;padding-top:0}
.pi-c-top{display:flex;flex-direction:column;align-items:flex-start;gap:14px;padding-bottom:24px}
.pi-c-row{display:flex;justify-content:space-between;align-items:center;gap:12px}
.pi-c-row .pi-c-label{flex:1}
.pi-c-label{font-size:13px;color:#5f564a;line-height:1.35}
.pi-c-big{font:800 44px/1 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.02em;margin-top:10px;font-variant-numeric:tabular-nums}
.pi-c-val{font:700 16px/1 "Instrument Sans",system-ui,sans-serif;font-variant-numeric:tabular-nums;white-space:nowrap}
.pi-c-tag{display:flex;align-items:center;gap:10px;flex:none;background:var(--token-4c494f9f-03b3-4eac-88e8-f5161b116659,#f4efe1);border-radius:8px;padding:9px 12px;font:600 12px/1 "Instrument Sans",system-ui,sans-serif;white-space:nowrap}
.pi-c-tag i{width:1px;height:14px;background:#c9c4bb}
.pi-c-pills{display:flex;background:var(--token-4c494f9f-03b3-4eac-88e8-f5161b116659,#f4efe1);border-radius:999px;padding:5px;gap:4px;margin-top:14px}
.pi-c-pill{flex:1;border:0;background:transparent;border-radius:999px;padding:0 6px;font:700 14px/1 "Instrument Sans",system-ui,sans-serif;color:inherit;cursor:pointer;height:46px}
.pi-c-pill.is-on{background:var(--token-dfd7ceb1-6225-41fe-9a08-4ed6d573c4d7,#ffe435)}
.pi-c-pill:focus-visible,.pi-c-range:focus-visible,.pi-c-btn:focus-visible,.pi-c-amount{border:0;background:transparent;text-align:right;width:130px;padding:0;color:inherit;font:800 22px/1 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.pi-c-range{-webkit-appearance:none;appearance:none;width:100%;height:6px;border-radius:3px;margin:22px 0 4px;cursor:pointer;background:linear-gradient(to right,#140c0a var(--p,9%),#e9e4d6 var(--p,9%))}
.pi-c-range::-webkit-slider-thumb{-webkit-appearance:none;width:22px;height:22px;border-radius:50%;background:#140c0a;border:0}
.pi-c-range::-moz-range-thumb{width:22px;height:22px;border-radius:50%;background:#140c0a;border:0}
.pi-c-range::-moz-range-track{height:6px;border-radius:3px;background:transparent}
.pi-c-rows{display:flex;flex-direction:column;gap:10px}
.pi-c-foot{border-top:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#e3ded2);margin:4px -32px 0;padding:22px 32px 0;display:flex;flex-direction:column;align-items:center;gap:14px}
.pi-c-next{font-size:13px;color:#5f564a}
.pi-c-btn{display:block;width:100%;text-align:center;background:var(--token-dfd7ceb1-6225-41fe-9a08-4ed6d573c4d7,#ffe435);border-radius:999px;padding:19px 0;font:700 13px/1 "Instrument Sans",system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:inherit;text-decoration:none}
.pi-c-disc{font-size:11px;line-height:1.45;color:#5f564a;margin:0;text-align:center}
.pi-case{width:100%;max-width:430px;margin:0 auto;padding:0 32px;box-sizing:border-box;display:flex;flex-direction:column;gap:12px;font-family:"Instrument Sans",system-ui,sans-serif;color:#140c0a;text-align:left}
.pi-case[hidden]{display:none}
.pi-case-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;border-bottom:1px solid #c9c4bb;padding-bottom:12px}
.pi-case-name{font:800 18px/1.1 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif}
.pi-case-item{display:flex;gap:12px;align-items:center;background:#f4efe1;border-radius:12px;padding:12px}
.pi-case-item b{display:block;font-size:14px}
.pi-case-item span:last-child{font-size:12px;color:#5f564a}
.pi-case-ic{flex:none;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font:700 13px/1 "Instrument Sans",system-ui,sans-serif}
.pi-c,.pi-case{transition:opacity .35s ease}
[data-framer-name="Container Configurator"] [data-framer-name="Bronze"],[data-framer-name="Container Configurator Mobile 2"] [data-framer-name="Bronze"]{width:100%!important;max-width:470px!important;margin:0 auto!important;padding:44px 0!important;box-sizing:border-box}
.pi-c-amount:focus-visible{outline:3px solid #140c0a;outline-offset:2px}
.pi-c-dim{color:#5f564a;font-weight:600}
.pi-c-amount.pi-c-costs{font:700 16px/1 "Instrument Sans",system-ui,sans-serif;letter-spacing:0;width:96px;border-bottom:1px dashed #c9c4bb;border-radius:0}
.pi-case-stage{font-size:12px;color:#5f564a;line-height:1.4}
.pi-case-prem{font-size:12px;line-height:1.4;background:#fff;border:1px solid #c9c4bb;border-radius:12px;padding:12px}
.pi-case-choices{display:flex;gap:6px;margin-top:8px}
.pi-case-choices span{flex:1;text-align:center;border:1px solid #140c0a;border-radius:999px;padding:7px 4px;font-weight:700;font-size:11px}
.pi-case-choices span.is-on{background:#ffe435}
.pi-hero-video{width:min(620px,100%)!important;height:auto!important;aspect-ratio:16/9!important;display:block;background:transparent;mix-blend-mode:darken;object-fit:cover;border-radius:0;-webkit-mask-image:linear-gradient(to right,transparent,#000 9%,#000 91%,transparent),linear-gradient(to bottom,transparent,#000 9%,#000 91%,transparent)!important;mask-image:linear-gradient(to right,transparent,#000 9%,#000 91%,transparent),linear-gradient(to bottom,transparent,#000 9%,#000 91%,transparent)!important;-webkit-mask-composite:source-in;mask-composite:intersect}
@media(max-width:809.98px){.pi-hero-video{width:100%!important}}
/* Closing headline on phones: its wrapper shrink-wraps to the unbroken line width, so the h1 never wraps */
@media(max-width:809.98px){[data-framer-name="CTA"] .framer-81bid4{width:100%!important;max-width:100%!important}}
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
  .pi-c,.pi-case{padding:0 18px}
  .pi-c-foot{margin-left:-18px;margin-right:-18px;padding-left:18px;padding-right:18px}
  .pi-c-pill{font-size:12px;padding:10px 2px;height:auto;line-height:1.15}
  .pi-c-tag{font-size:11px;padding:8px 10px;gap:6px 10px;white-space:normal;flex-wrap:wrap;max-width:100%}
  .pi-c-tag i{display:none}
  .pi-c-big{font-size:38px}
  .pi-c-amount{font-size:20px;width:110px}
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

  /* 4b. Hero video: respect reduced motion */
  [].forEach.call(document.querySelectorAll('.pi-hero-video, .pi-watch-video'), function (heroVideo) {
    if (reduce) { heroVideo.removeAttribute('autoplay'); heroVideo.pause(); return; }
    var kick = function () { if (heroVideo.paused) { var p = heroVideo.play(); if (p && p.catch) p.catch(function () {}); } };
    heroVideo.addEventListener('canplay', kick);
    ['scroll', 'pointerdown', 'touchstart', 'keydown'].forEach(function (ev) { window.addEventListener(ev, kick, { once: true, passive: true }); });
    document.addEventListener('visibilitychange', function () { if (!document.hidden) kick(); });
    kick();
  });

  /* 5. Calculator cards (one per breakpoint variant). From the client explainer: the 10% fee is
     calculated after case costs, next to a typical 33% firm figured the same way. Case costs default
     to an example (5%, to the nearest $500: $1,000 / $2,000 / $5,000 for the explainer's three rows)
     and can be edited. */
  function money(n) { return '$' + Math.round(n).toLocaleString('en-US'); }
  var RATE = 0.10, TYPICAL = 0.33;
  function autoCosts(a) { return Math.max(500, Math.round(a * 0.05 / 500) * 500); }
  [].forEach.call(document.querySelectorAll('[data-pi-calc]'), function (c) {
    var range = c.querySelector('.pi-c-range'), amountIn = c.querySelector('.pi-c-amount:not(.pi-c-costs)'), costsIn = c.querySelector('.pi-c-costs'), pills = c.querySelectorAll('.pi-c-pill');
    var min = Number(range.min), max = Number(range.max), costsManual = false;
    function set(sel, v) { var el = c.querySelector(sel); if (el) el.textContent = v; }
    function parse(v) { return Number(String(v).replace(/[^0-9]/g, '')); }
    function clampN(n) { return Math.min(max, Math.max(min, n)); }
    function costs(amount) { var n = costsManual ? parse(costsIn.value) : autoCosts(amount); return Math.min(amount * 0.9, Math.max(0, n)); }
    function render(amount) {
      var k = costs(amount), net = amount - k, fee = net * RATE, fee33 = net * TYPICAL;
      range.style.setProperty('--p', ((amount - min) / (max - min) * 100).toFixed(1) + '%');
      if (document.activeElement !== costsIn) costsIn.value = money(k);
      set('[data-out="fee"]', money(fee));
      set('[data-out="fee33"]', money(fee33));
      set('[data-out="more"]', money(fee33 - fee));
      set('[data-out="keep"]', money(net - fee));
      range.setAttribute('aria-valuetext', money(amount));
    }
    range.addEventListener('input', function () { amountIn.value = money(Number(range.value)); render(Number(range.value)); });
    amountIn.addEventListener('input', function () { var n = parse(amountIn.value); if (!n) return; n = clampN(n); range.value = n; render(n); });
    amountIn.addEventListener('blur', function () { var n = clampN(parse(amountIn.value) || Number(range.value)); range.value = n; amountIn.value = money(n); render(n); });
    costsIn.addEventListener('input', function () { costsManual = true; render(Number(range.value)); });
    costsIn.addEventListener('blur', function () { if (!parse(costsIn.value)) costsManual = false; render(Number(range.value)); });
    [].forEach.call(pills, function (p) {
      p.addEventListener('click', function () {
        [].forEach.call(pills, function (q) { q.classList.remove('is-on'); });
        p.classList.add('is-on'); set('[data-out="casetype"]', p.textContent);
      });
    });
    render(Number(range.value));
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



def faq_html():
    """The questions people ask, grouped; same source as the FAQPage schema in the head."""
    groups = "".join(
        f'<h3 class="pi-faq-g">{g["title"]}</h3>' + "".join(
            f'<details class="pi-faq"><summary>{i["q"]}</summary><p>{i["a"]}</p></details>' for i in g["items"])
        for g in FAQ_GROUPS)
    return ('<section class="pi-faq-sec" id="faq" aria-labelledby="pi-faq-h"><div class="pi-faq-wrap">'
            '<h2 id="pi-faq-h" class="pi-faq-h">Questions people ask.</h2>'
            '<p class="pi-faq-lead">Straight answers about the fee, what you keep and how a case with 10flat works. Items in [brackets] are still being confirmed.</p>'
            f'{groups}</div></section>')


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

    # --- hero illustration: Tim's gavel instead of Stack's turtle
    html = html.replace('https://framerusercontent.com/modules/FBm2eH5o7STzB0ruXyZj/sqYJJoCYRzvBBoSsyFCm/icon.svg', 'assets/gavel.mp4')
    # the <img> becomes a silent looping <video>; the poster is its first frame
    html, n_video = re.subn(
        r'<img([^>]*?)\s*alt(?:="[^"]*")?([^>]*)src="assets/gavel.mp4"([^>]*)>',
        r'<video\1\2\3 class="pi-hero-video" poster="assets/gavel-poster.jpg" autoplay muted loop playsinline preload="metadata" aria-hidden="true"><source src="assets/gavel.mp4" type="video/mp4"></video>',
        html, count=1)
    assert n_video == 1, 'hero video not placed'
    html = re.sub(r'(<video[^>]*class="framer-h3yKp framer-1qidnr3)"([^>]*?) class="pi-hero-video"', r'\1 pi-hero-video"\2', html, count=1)
    # --- the "Watch" tile: Stack's Wistia demo (poster image + WATCH button) becomes a silent looping clip
    html, n_watch = re.subn(
        r'<img src="https://framerusercontent\.com/images/CTtHYoCcpC6BgMBFg0T5nTlRvFs\.png[^>]*>',
        '<video class="pi-watch-video" poster="assets/watch-poster.jpg" autoplay muted loop playsinline preload="metadata" aria-label="City at dusk" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"><source src="assets/watch.mp4" type="video/mp4"></video>',
        html)
    assert n_watch >= 1, 'watch tile poster not found'
    html = re.sub(r'<div style="[^"]*" role="button" aria-label="WATCH video" tabindex="-?\d+"></div>', '', html)
    html = re.sub(r'<button style="[^"]*" aria-label="WATCH video">.*?</button>', '', html, flags=re.S)
    assert 'WATCH video' not in html, 'WATCH overlay still present'
    # --- closing image: Lady Justice (iStock 2214624729, licensed) instead of Stack's truck photo
    html, n_close = re.subn(r'https://framerusercontent\.com/images/xBb8xgSKGQQN7I5S0r0MxSStns\.png[^)"\s]*', 'assets/justice.jpg', html)
    assert n_close >= 1, 'closing image not found'
    # a dark scrim, heavier on the left where the headline sits, so the off-white text reads over the photo
    html = html.replace('background-image:url(assets/justice.jpg)', 'background-image:linear-gradient(90deg,rgba(20,12,10,.66) 0%,rgba(20,12,10,.5) 55%,rgba(20,12,10,.36) 100%),url(assets/justice.jpg)')
    # --- the three step drawings: Tim's set (phone and WhatsApp, case folders, scales and briefcase) instead of Stack's inline SVGs
    for n, cls in ((1, "dlhvuy"), (2, "qptr4j"), (3, "1xu5j0d")):
        html, k = re.subn(r'(<img alt class="framer-[A-Za-z0-9]+ framer-%s" src=")data:image/svg\+xml,[^"]*(")' % cls,
                          r'\g<1>assets/step-%d.png\g<2>' % n, html)
        assert k >= 1, 'step %d drawing not found' % n
    # --- the case card avatar: Tim's photo instead of Stack's stock portrait
    html, n_av = re.subn(r'https://framerusercontent\.com/images/mFmNcpd7kBFH15skVqgZeJ55uQ\.png[^"\s,]*', 'assets/avatar.jpg', html)
    assert n_av >= 1, 'avatar not found'
    # --- FAQ section before the footer (the bundle's #overlay sits between the page and the footer)
    assert html.count('<div id="overlay"></div>') == 1, 'overlay anchor'
    html = html.replace('<div id="overlay"></div>', faq_html() + '<div id="overlay"></div>', 1)
    # --- global swaps
    html = replace_all(html, GLOBAL, "page", required=False)
    html = html.replace('<div class="framer-DJN29 framer-cqcfvd"></div>', f'<span class="pi-wordmark">{BRAND}</span>')
    html = re.sub(r'<a class="framer-18cgtl3 framer-1f2myp"[^>]*>.*?</a>', "", html, flags=re.S)
    html = re.sub(r'<a name="Nav Watch a demo" class="framer-cLKaN', '<a href="#hero" name="Start your case" class="framer-cLKaN', html, count=1)

    # --- scripts and Stack metadata out, ours in
    html = re.sub(r"<script\b.*?</script>", "", html, flags=re.S)
    html = re.sub(r"<meta\b[^>]*(?:name|property)=\"(?:description|robots|og:[^\"]+|twitter:[^\"]+|framer-search-index[^\"]*|generator)\"[^>]*>", "", html)
    html = re.sub(r"<link\b[^>]*rel=\"(?:canonical|icon)\"[^>]*>", "", html)
    html = re.sub(r"<title>.*?</title>", f"<title>{CONFIG['title']}</title>", html, count=1, flags=re.S)
    sync_schema_faq()
    schema_block = re.search(r"<script type=\"application/ld\+json\">.*?</script>", SCHEMA.read_text(encoding="utf-8"), re.S).group(0)
    meta = (f'<meta name="description" content="{CONFIG["description"]}">'
            f'<link rel="canonical" href="https://{CONFIG["domain"]}/">'
            f'<meta name="robots" content="noindex, nofollow">{schema_block}{MOTION_CSS}')
    html = html.replace("</head>", meta + "</head>", 1)
    html = html.replace(' data-framer-hydrate-v2="', ' data-x-hydrate="', 1)
    html = html.replace("<!-- Made in Framer · framer.com -->", f"<!-- {BRAND} prototype: mystack.com clone with text swapped by tools/build_clone.py. Do not edit by hand. -->", 1)
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
    for bad in ("Brutal Renewal", "Stack Health", "ICHRA", "$500", "Instant Quote", "Instant quote", "For Brokers", "benefits", "renewal", "employee", "$3,744", "Bronze", "Silver", "Gold", "Maria", "Monthly Budget", "benchmark", "$50", "Car 25%", "Medical 33%", "Dental 33%", "25% when we win", "33% when", "What you get when we win", "Expected award", "$0 down", "Clearfee", "[FIRM NAME]", "AI lawyer", "no fee unless", "guaranteed", "gross recovery", "Premium", "Attorney-Led", "automatic upgrade", "Illustrative recovery", "before costs and liens", "10flatlaw", "[STATE]", "legal-service offering", "[ATTORNEY NAME", "[NAME]", "[WHATSAPP NUMBER]", "[CITY]", "[STREET ADDRESS]", "Azure", "Attorney responsible"):
        if bad.lower() in text.lower():
            i = text.lower().find(bad.lower())
            raise SystemExit(f"build_clone: leftover {bad!r}: ...{text[max(0,i-60):i+60]}...")
    print(f"built {OUT.relative_to(ROOT)}: {len(html):,} bytes; reveals: {html.count('--pi-appear')}; calculators: {html.count('data-pi-calc')-1}; step-2 duplicates removed: {len(doomed)}; h1: {html.count('<h1')}")


if __name__ == "__main__":
    main()
