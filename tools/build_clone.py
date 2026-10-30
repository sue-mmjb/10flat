#!/usr/bin/env python3
"""Build site/index.html: the mystack.com clone with every tile and section
kept, and only the text swapped for the personal injury content.

Tim wants to see the cloned site as-is with our words in it. So, unlike
build_site.py (which rebuilds sections as clean HTML and lives at /v2),
this script keeps all of Stack's sections, illustrations, logo rows,
testimonial cards and quote carousel, and changes words only.

The one thing it must remove is Framer's JavaScript bundle: tested on
30 Oct 2026, the bundle re-renders the page from Stack's own data a few
seconds after load and puts "Brutal Renewal" back. Without the bundle the
scroll-pinned sections need a few CSS rules to sit still, applied below.

Run from the project root:
    python tools/build_clone.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site import Tree, by_name, by_class, by_id, derevelo, unhide, strip_comments, CONFIG, SCHEMA  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "mystack-index.html"
OUT = ROOT / "site" / "index.html"
FIRM = CONFIG["firm"]

# ----------------------------------------------------------------------------
# Text swaps. Left = exact text in the clone (curly quotes as in the source).
# Right = our content. Scoped to a section where the same string appears in
# two places with different meanings.
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
    (">Total Monthly Budget<", ">What you get when we win<"),
    (">benchmark plan<", ">Case type<"),
    (">Bronze<", ">Car 25%<"), (">Silver<", ">Medical 33%<"), (">Gold<", ">Dental 33%<"),
    (">employer contribution<", ">Expected award<"),
    (">OH<", ">$0<"),
    ("Next, your team shops for benefits.", "Next, tell us what happened."),
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
    (">Dental Plan<", ">Dental malpractice<"), (">Family Plan<", ">Medical malpractice<"),
    (">Silver HMO Family Plan<", ">Car accident · 25%<"), (">health Plan<", ">Case<"), (">Health Premium<", ">Our fee<"),
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

# "You set the budget." and friends mean one thing in the product demo and another in the three-step section
SCOPED = {
    "SET A BUDGET": [
        (">You set the budget.<", ">What would you actually take home?<"),
        (">$<", ">$75,000<"),  # the calculator's value slot, filled by JS on the live site
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

STATIC_CSS = """
<style id="pi-clone-static">
/* The Framer bundle is gone (it restores Stack's text), so freeze what it animated. */
.framer-xvfz0d,.framer-xvfz0d *{pointer-events:auto}
[data-framer-name="MAIN"] [data-framer-name="Absolute"]{position:relative!important;inset:auto!important;transform:none!important}
[data-framer-name="MAIN"] [data-framer-name="Viewport"]{height:auto!important;min-height:0!important;overflow:visible!important}
.framer-71z80s{height:auto!important;padding:120px 0!important}
.framer-882vmr{position:relative!important;height:auto!important;top:auto!important}
.framer-18uk1a7{height:auto!important}
.framer-1j23hd2-container{transform:none!important}
[data-framer-name="Card 1"],[data-framer-name="Card 2"],[data-framer-name="Card 3"]{transform:none!important}
[data-framer-name="TRUSTED PARTNERS"] div,[data-framer-name="TRUSTED PARTNERS"] ul,[data-framer-name="TRUSTED PARTNERS"] li,[data-framer-name="Tabs"]{opacity:1!important}
.framer-1ebd1db,.framer-TzIF9 .framer-1ebd1db{position:relative!important;height:auto!important;width:100%!important;flex:none!important;padding:120px 0 56px!important;bottom:auto!important}
.framer-1w3xnl7,.framer-TzIF9 .framer-1w3xnl7{height:auto!important;flex:none!important;width:100%!important}
.framer-8pye7d,.framer-TzIF9 .framer-8pye7d{width:auto!important;max-width:60%!important;height:auto!important;flex:none!important}
.framer-whz10a,.framer-TzIF9 .framer-whz10a{width:auto!important;max-width:420px!important;height:auto!important;flex:none!important}
.framer-xj49yz,.framer-TzIF9 .framer-xj49yz{height:auto!important;overflow:visible!important}
.framer-nh45d3,.framer-TzIF9 .framer-nh45d3{position:relative!important;top:auto!important;height:auto!important;width:100%!important}
.pi-wordmark{font:800 22px/1 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.02em;color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);white-space:nowrap;text-decoration:none}
.pi-footer-mark{font:800 clamp(56px,12vw,180px)/.9 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.04em;color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);margin:0}
.framer-e8x4r3 .hidden-yycdle{display:flex!important}
.framer-e8x4r3 button{display:none!important}
html{scroll-behavior:smooth}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media(max-width:809.98px){.framer-e8x4r3{padding:14px 16px}.framer-e8x4r3 .framer-1ezgx8l{display:none}
.framer-1w3xnl7,.framer-TzIF9 .framer-1w3xnl7{padding:0 20px!important;flex-direction:column!important;align-items:flex-start!important;gap:32px!important}
.framer-8pye7d,.framer-TzIF9 .framer-8pye7d,.framer-whz10a,.framer-TzIF9 .framer-whz10a{max-width:100%!important}}
</style>
"""


def replace_all(html, pairs, where):
    for old, new in pairs:
        if old not in html:
            raise SystemExit(f"build_clone: text not found in {where}: {old[:80]!r}")
        html = html.replace(old, new)
    return html


def main():
    src = SRC.read_text(encoding="utf-8")
    t = Tree(src)

    # --- section-scoped swaps first (by offset, from the end so offsets stay valid)
    edits = []
    for name, pairs in SCOPED.items():
        n = t.find(by_name(name))
        edits.append((n["start"], n["end"], replace_all(src[n["start"]:n["end"]], pairs, name)))
    # footer disclaimer and big wordmark, nav logo
    disc = t.find(by_name("Disclaimer"))
    disc_p = [c for c in disc["children"] if c["tag"] == "p"][0]
    open_tag = src[disc_p["start"]:src.find(">", disc_p["start"]) + 1]
    edits.append((disc_p["start"], disc_p["end"], f"{open_tag}{FOOTER_DISCLAIMER}</p>"))
    mark = t.find(by_class("framer-8pye7d"))
    edits.append((mark["start"], mark["end"], f'<div class="framer-8pye7d"><p class="pi-footer-mark">{FIRM}</p></div>'))
    html = src
    for start, end, new in sorted(edits, key=lambda e: -e[0]):
        html = html[:start] + new + html[end:]

    # --- global swaps
    html = replace_all(html, GLOBAL, "page")
    html = html.replace('<div class="framer-DJN29 framer-cqcfvd"></div>', f'<span class="pi-wordmark">{FIRM}</span>')
    html = re.sub(r'<a class="framer-18cgtl3 framer-1f2myp"[^>]*>.*?</a>', "", html, flags=re.S)  # footer link to Stack home
    html = re.sub(r'<a name="Nav Watch a demo" class="framer-cLKaN', '<a href="#hero" name="Start your case" class="framer-cLKaN', html, count=1)

    # --- scripts and Stack metadata out, ours in
    html = re.sub(r"<script\b.*?</script>", "", html, flags=re.S)
    html = re.sub(r"<meta\b[^>]*(?:name|property)=\"(?:description|robots|og:[^\"]+|twitter:[^\"]+|framer-search-index[^\"]*|generator)\"[^>]*>", "", html)
    html = re.sub(r"<link\b[^>]*rel=\"(?:canonical|icon)\"[^>]*>", "", html)
    html = re.sub(r"<title>.*?</title>", f"<title>{CONFIG['title']}</title>", html, count=1, flags=re.S)
    schema_block = re.search(r"<script type=\"application/ld\+json\">.*?</script>", SCHEMA.read_text(encoding="utf-8"), re.S).group(0)
    meta = (f'<meta name="description" content="{CONFIG["description"]}">'
            f'<link rel="canonical" href="https://{CONFIG["domain"]}/">'
            f'<meta name="robots" content="noindex, nofollow">{schema_block}{STATIC_CSS}')
    html = html.replace("</head>", meta + "</head>", 1)
    html = html.replace(' data-framer-hydrate-v2="', ' data-x-hydrate="', 1)
    html = html.replace("<!-- Made in Framer · framer.com -->", f"<!-- {FIRM} prototype: mystack.com clone with text swapped by tools/build_clone.py. Do not edit by hand. -->", 1)

    # --- make animated content visible without the bundle
    html = derevelo(html)
    html = unhide(html)
    html = strip_comments(html)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    # --- self-checks on visible text
    body = html[html.find("<body"):]
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S)))
    for bad in ("Brutal Renewal", "Stack Health", "ICHRA", "$500", "Instant Quote", "Instant quote", "For Brokers", "benefits", "renewal", "employee"):
        if bad.lower() in text.lower():
            i = text.lower().find(bad.lower())
            raise SystemExit(f"build_clone: leftover {bad!r}: ...{text[max(0,i-60):i+60]}...")
    print(f"built {OUT.relative_to(ROOT)}: {len(html):,} bytes; scripts: {len(re.findall(r'<script', html))} (0 = Framer bundle removed); h1: {html.count('<h1')}")


if __name__ == "__main__":
    main()
