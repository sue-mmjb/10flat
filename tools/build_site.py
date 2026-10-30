#!/usr/bin/env python3
"""Build site/v2/index.html (the rebuilt version) for the [FIRM NAME] personal injury site from the
mystack.com Framer clone in source/mystack-index.html.

What it keeps from the clone: the <head> styles (fonts, colour tokens, type
presets, breakpoints), the nav, the hero, the "We win when" block, the footer
and the SVG sprite used by the pill buttons.

What it drops: every <script> (the Framer bundle re-renders the page from its
own data and would overwrite our text), the product demo, partner and carrier
logos, testimonials and the pinned CTA. Those are replaced with plain HTML and
one small inline script for the calculator.

Run from the project root:
    python tools/build_site.py

Everything the client still has to confirm is in CONFIG below and is shown on
the page inside a highlighted [CONFIRM ...] chip so nobody mistakes it for a
decision.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "mystack-index.html"
OUT = ROOT / "site" / "v2" / "index.html"
SCHEMA = ROOT / "content" / "schema" / "home.html"

# ----------------------------------------------------------------------------
# Content. Confirmed by Tim unless marked CONFIRM.
# ----------------------------------------------------------------------------
CONFIG = {
    "firm": "10flat",
    "brand": "10flat",
    "domain": "10flatlaw.com",
    "title": "10% Injury Fee, Even at Trial | 10flat",
    "description": "Most injury firms take 33–40% of your settlement. 10flat takes 10%, calculated after case costs, and it stays 10% even at trial. Technology does the paperwork. A licensed Texas attorney does the lawyering.",
    "noindex": True,  # prototype. Set False at launch.
    # One fee for every case type. From the 10flat client explainer, 31 Oct 2026.
    "rates": [
        {"key": "car", "label": "Car accident", "rate": 0.10},
        {"key": "med", "label": "Medical injury", "rate": 0.10},
        {"key": "dent", "label": "Dental injury", "rate": 0.10},
    ],
    # Explainer: "No fee and no costs if we don't recover money for you." and "It never goes up, even at trial."
    "today_display": "$0 fee, $0 costs",
    "trial": "Still 10%",
    # Explainer compares with a 33% firm; its footnote cites "[Texas Fee Index, date]".
    "industry_rate": 0.33,
    "industry_confirm": "CONFIRM: Texas Fee Index citation and date",
    # Example case costs: 5% of the settlement to the nearest $500, which reproduces the explainer's table ($1,000 / $2,000 / $5,000).
    "costs_share": 0.05,
    # CONFIRM: slider range.
    "slider_min": 10000,
    "slider_max": 1000000,
    "slider_step": 1000,
    "slider_default": 100000,
}

FAQ_PATH = ROOT / "content" / "faq.json"   # single source for both sites and the FAQPage schema
FAQ_GROUPS = json.loads(FAQ_PATH.read_text(encoding="utf-8"))["groups"]
FAQ = [(i["q"], i["a"]) for g in FAQ_GROUPS for i in g["items"]]


def sync_schema_faq():
    """Rewrite the FAQPage node in content/schema/home.html from content/faq.json."""
    text = SCHEMA.read_text(encoding="utf-8")
    m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', text, re.S)
    data = json.loads(m.group(2))
    node = next(n for n in data["@graph"] if n["@type"] == "FAQPage")
    node["mainEntity"] = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]
    new = m.group(1) + "\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n" + m.group(3)
    SCHEMA.write_text(text[:m.start()] + new + text[m.end():], encoding="utf-8")

# ----------------------------------------------------------------------------
# Tiny HTML tree with byte offsets, so we can slice the clone safely.
# ----------------------------------------------------------------------------
VOID = {"img", "br", "meta", "link", "input", "hr", "source", "wbr", "area", "base", "col", "embed", "param", "track"}


class Tree(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.line_starts = [0] + [m.end() for m in re.finditer("\n", src)]
        self.stack, self.nodes = [], []
        self.feed(src)

    def off(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        n = {"tag": tag, "attrs": dict(attrs), "start": self.off(), "end": None, "children": []}
        (self.stack[-1]["children"] if self.stack else self.nodes).append(n)
        if tag in VOID:
            n["end"] = self.src.find(">", n["start"]) + 1
        else:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()
            self.stack_last_end()

    def stack_last_end(self):
        pass

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                e = self.off()
                n = self.stack[i]
                n["end"] = self.src.find(">", e) + 1
                for k in self.stack[i + 1:]:
                    k["end"] = k["end"] or e
                del self.stack[i:]
                break

    def find_all(self, pred, nodes=None, out=None):
        out = [] if out is None else out
        for n in (self.nodes if nodes is None else nodes):
            if pred(n):
                out.append(n)
            self.find_all(pred, n["children"], out)
        return out

    def find(self, pred):
        r = self.find_all(pred)
        if not r:
            raise SystemExit(f"build: could not find node for {pred.__doc__ or pred}")
        return r[0]

    def html(self, n):
        return self.src[n["start"]:n["end"]]

    def inner(self, n):
        open_end = self.src.find(">", n["start"]) + 1
        close_start = self.src.rfind("<", 0, n["end"])
        return self.src[open_end:close_start]


def by_name(name):
    def p(n):
        return n["attrs"].get("data-framer-name") == name
    p.__doc__ = f"data-framer-name={name}"
    return p


def by_class(cls):
    def p(n):
        return cls in (n["attrs"].get("class") or "").split()
    p.__doc__ = f"class={cls}"
    return p


def by_id(i):
    def p(n):
        return n["attrs"].get("id") == i
    p.__doc__ = f"id={i}"
    return p


# ----------------------------------------------------------------------------
# Transformations applied to copied Framer markup
# ----------------------------------------------------------------------------
def derevelo(html):
    """Framer's text-reveal component ships an animated copy and a static
    fallback. Keep only the fallback's contents so nothing overlaps or hides."""
    t = Tree(html)
    out, pos = [], 0
    for n in sorted(t.find_all(lambda n: "revelo" in (n["attrs"].get("class") or "").split()
                               and "words" in (n["attrs"].get("class") or "").split()),
                    key=lambda n: n["start"]):
        if n["start"] < pos:
            continue
        fb = [c for c in n["children"] if "revelo-fallback" in (c["attrs"].get("class") or "")]
        if not fb:
            continue
        out.append(html[pos:n["start"]])
        out.append(t.inner(fb[0]))
        pos = n["end"]
    out.append(html[pos:])
    return "".join(out)


def unhide(html):
    """Appear/scroll animations leave elements at opacity 0 until the bundle
    runs. Make them visible."""
    html = re.sub(r"will-change:transform;opacity:0(?:\.001)?;transform:[^;\"]*", "opacity:1;transform:none", html)
    html = re.sub(r"opacity:0\.001;transform:[^;\"]*", "opacity:1;transform:none", html)
    return html


def strip_comments(html):
    return re.sub(r"<!--\$-->|<!--/\$-->", "", html)


def replace_once(html, old, new, where):
    if old not in html:
        raise SystemExit(f"build: expected text not found in {where}: {old!r}")
    return html.replace(old, new, 1)


# ----------------------------------------------------------------------------
# Pieces
# ----------------------------------------------------------------------------
def pill_button(src_button_html, text, href, extra_class=""):
    """Reuse the clone's black pill button (text + arrow circle)."""
    b = strip_comments(src_button_html)
    b = re.sub(r"<p class=\"framer-text framer-styles-preset-ivrpyo\"([^>]*)>[^<]*</p>",
               lambda m: f"<p class=\"framer-text framer-styles-preset-ivrpyo\"{m.group(1)}>{text}</p>", b, count=1)
    b = b.replace("<a class=\"framer-Xp2gR", f"<a href=\"{href}\" class=\"pi-btn {extra_class} framer-Xp2gR", 1)
    b = re.sub(r'\sdata-highlight="true"|\stabindex="0"', "", b)
    return b


def chip(text):
    return f'<mark class="pi-confirm">[{text}]</mark>'


def money(n):
    return "$" + f"{n:,.0f}"


def build_sections(btn):
    c = CONFIG
    rates_json = json.dumps({r["key"]: r["rate"] for r in c["rates"]})
    options = "".join(f'<option value="{r["key"]}">{r["label"]} ({int(round(r["rate"]*100))}%)</option>' for r in c["rates"])
    d = c["slider_default"]
    r0 = c["rates"][0]["rate"]
    k0 = max(500, round(d * c["costs_share"] / 500) * 500)
    net0 = d - k0
    fee0, keep0, ind0 = net0 * r0, net0 - net0 * r0, net0 * c["industry_rate"]

    calculator = f"""
<section class="pi-section pi-yellow" id="calculator" aria-labelledby="calc-h">
  <div class="pi-wrap pi-center">
    <h2 id="calc-h" class="framer-text framer-styles-preset-9kqwf9 pi-h2">Less paperwork. More money to you.</h2>
    <p class="framer-text framer-styles-preset-1fc2js5 pi-lead">Most injury firms take 33–40% of your settlement. We take 10%, calculated after case costs, and it stays 10% even if we go to trial. Your fee doesn’t decide how much your case is worth. Your injuries, your medical bills, the facts and the insurance coverage do. What the fee changes is how much of the settlement you keep.</p>
  </div>
  <div class="pi-wrap">
    <div class="pi-card">
      <p class="framer-text framer-styles-preset-lit60w pi-step">step 1</p>
      <h3 class="framer-text framer-styles-preset-1jvhhyw pi-h3">See what you keep.</h3>
      <p class="framer-text framer-styles-preset-u2fub4 pi-muted">Slide to the amount you expect to recover. We show example case costs, our 10% fee, the fee at a typical 33% firm, and how much more you keep.</p>
      <div class="pi-calc">
        <div class="pi-field">
          <label for="case-type" class="framer-text framer-styles-preset-7jf1zc">Case type</label>
          <select id="case-type" class="pi-select framer-text framer-styles-preset-u2fub4">{options}</select>
        </div>
        <div class="pi-field">
          <label for="amount" class="framer-text framer-styles-preset-7jf1zc">If your case settles for <span class="pi-amount-out" id="amount-out">{money(d)}</span></label>
          <input id="amount" class="pi-range" type="range" min="{c['slider_min']}" max="{c['slider_max']}" step="{c['slider_step']}" value="{d}" aria-valuetext="{money(d)}">
          <div class="pi-range-ends framer-text framer-styles-preset-10holly"><span>{money(c['slider_min'])}</span><span>{money(c['slider_max'])}</span></div>
          <p class="pi-note framer-text framer-styles-preset-10holly">Slider range {chip('CONFIRM: minimum, maximum and default')}</p>
        </div>
        <dl class="pi-results">
          <div class="pi-row"><dt class="framer-text framer-styles-preset-u2fub4">If there is no recovery</dt><dd class="framer-text framer-styles-preset-1jvhhyw pi-num" id="out-today">{c['today_display']}</dd></div>
          <div class="pi-row"><dt class="framer-text framer-styles-preset-u2fub4">Case costs (example)</dt><dd class="framer-text framer-styles-preset-1jvhhyw pi-num pi-num-dim" id="out-costs">{money(k0)}</dd></div>
          <div class="pi-row"><dt class="framer-text framer-styles-preset-u2fub4">Fee at a {int(round(c['industry_rate']*100))}% firm <span class="pi-rowchip">{chip(c['industry_confirm'])}</span></dt><dd class="framer-text framer-styles-preset-1jvhhyw pi-num pi-num-dim" id="out-industry">{money(ind0)}</dd></div>
          <div class="pi-row"><dt class="framer-text framer-styles-preset-u2fub4">Our fee <span id="out-rate">({int(round(r0*100))}%)</span>, calculated after case costs</dt><dd class="framer-text framer-styles-preset-1jvhhyw pi-num" id="out-fee">{money(fee0)}</dd></div>
          <div class="pi-row pi-row-hero"><dt class="framer-text framer-styles-preset-u2fub4">You keep, after fee and costs</dt><dd class="framer-text framer-styles-preset-1jvhhyw pi-num pi-num-big" id="out-keep">{money(keep0)}</dd></div>
          <div class="pi-row pi-row-diff"><dt class="framer-text framer-styles-preset-u2fub4">You keep this much more</dt><dd class="framer-text framer-styles-preset-1jvhhyw pi-num" id="out-diff">{money(ind0-fee0)}</dd></div>
        </dl>
        <p class="pi-note framer-text framer-styles-preset-u2fub4">Fees are figured after case costs at both firms. Medical bills and liens are paid from the settlement the same way at any firm.</p>
        <p class="pi-fine framer-text framer-styles-preset-10holly">Example only. Not a prediction, promise or guarantee of any outcome or amount. Every case is different.</p>
      </div>
      <a class="pi-next framer-text framer-styles-preset-15qf7x7" href="#start">Next, tell us what happened. &rarr;</a>
    </div>
  </div>
</section>
"""

    rows = "".join(
        f'<tr><th scope="row" class="framer-text framer-styles-preset-u2fub4">{r["label"] if r["key"] != "car" else "Car accidents"}</th>'
        f'<td class="framer-text framer-styles-preset-u2fub4">{c["today_display"]}</td>'
        f'<td class="framer-text framer-styles-preset-1jvhhyw pi-rate">{int(round(r["rate"]*100))}%</td>'
        f'<td class="framer-text framer-styles-preset-u2fub4">{c["trial"]}</td></tr>'
        for r in c["rates"])
    pricing = f"""
<section class="pi-section pi-offwhite" id="pricing" aria-labelledby="pricing-h">
  <div class="pi-wrap pi-center">
    <h2 id="pricing-h" class="framer-text framer-styles-preset-9kqwf9 pi-h2">One fee for every case. It never goes up.</h2>
    <p class="framer-text framer-styles-preset-1fc2js5 pi-lead">We don’t negotiate fees case by case behind closed doors. Here is what we charge, for everything we handle, whether the case settles or goes to trial.</p>
  </div>
  <div class="pi-wrap">
    <table class="pi-table">
      <thead><tr><th scope="col" class="framer-text framer-styles-preset-7jf1zc">Case type</th><th scope="col" class="framer-text framer-styles-preset-7jf1zc">If there is no recovery</th><th scope="col" class="framer-text framer-styles-preset-7jf1zc">Fee, after case costs</th><th scope="col" class="framer-text framer-styles-preset-7jf1zc">At trial</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p class="pi-note pi-center framer-text framer-styles-preset-10holly">Other case types and rates are proposed only and will be added once approved. {chip('CONFIRM: proposed case types, see content pack section 4.2')}</p>
  </div>
</section>
"""

    steps = f"""
<section class="pi-section pi-offwhite pi-tight" id="how" aria-labelledby="how-h">
  <div class="pi-wrap pi-center">
    <h2 id="how-h" class="framer-text framer-styles-preset-9kqwf9 pi-h2">Three steps. No waiting room.</h2>
  </div>
  <div class="pi-wrap">
    <ol class="pi-steps">
      <li><span class="framer-text framer-styles-preset-lit60w pi-step">1</span><h3 class="framer-text framer-styles-preset-1jvhhyw pi-h3">Tell us what happened.</h3><p class="framer-text framer-styles-preset-1fc2js5">Message us on WhatsApp. Tell us what happened and send any photos or documents you have. A Texas attorney will review your case, usually [the same day]. It’s free to find out if we can help.</p></li>
      <li><span class="framer-text framer-styles-preset-lit60w pi-step">2</span><h3 class="framer-text framer-styles-preset-1jvhhyw pi-h3">We build your case.</h3><p class="framer-text framer-styles-preset-1fc2js5">Our system organises your photos, police report and medical records the moment you send them. It requests missing records, builds a timeline of your treatment, totals your bills, drafts letters and tracks every deadline. A trained case team checks the work.</p></li>
      <li><span class="framer-text framer-styles-preset-lit60w pi-step">3</span><h3 class="framer-text framer-styles-preset-1jvhhyw pi-h3">We pursue your recovery.</h3><p class="framer-text framer-styles-preset-1fc2js5">Your attorney spends time where it counts: reviewing your case, advising you and negotiating with the insurance company. For every offer we show what you’d actually keep. You make every settlement decision, with a call from your attorney before you do. If the insurer won’t make a fair offer, we file a lawsuit, and your fee stays 10%.</p></li>
    </ol>
  </div>
</section>
"""

    why = f"""
<section class="pi-section pi-cream" id="why" aria-labelledby="why-h">
  <div class="pi-wrap pi-center">
    <h2 id="why-h" class="framer-text framer-styles-preset-9kqwf9 pi-h2">We charge less because we spend less, not because we do less.</h2>
    <p class="framer-text framer-styles-preset-1fc2js5 pi-lead">When a firm charges 33–40%, that fee pays for paperwork staff, billboards and expensive offices. None of that makes your case stronger, but it all comes out of your settlement. At {c['firm']} technology does the paperwork other firms pay people to do. A trained case team checks the work, and a licensed Texas attorney reviews and approves every important step. No billboards, no marble lobby. Think of it like online banking: it got faster and cheaper because the routine work became automatic.</p>
  </div>
</section>
"""

    faq_items = "".join(
        f'<h3 class="framer-text framer-styles-preset-1jvhhyw pi-h3 pi-faq-g">{g["title"]}</h3>' + "".join(
            f'<details class="pi-faq"><summary class="framer-text framer-styles-preset-1fc2js5">{i["q"]}</summary>'
            f'<p class="framer-text framer-styles-preset-u2fub4">{i["a"]}</p></details>' for i in g["items"])
        for g in FAQ_GROUPS)
    faq = f"""
<section class="pi-section pi-offwhite" id="faq" aria-labelledby="faq-h">
  <div class="pi-wrap pi-center">
    <h2 id="faq-h" class="framer-text framer-styles-preset-9kqwf9 pi-h2">Questions people ask before they start.</h2>
  </div>
  <div class="pi-wrap pi-narrow">{faq_items}</div>
</section>
"""

    start = f"""
<section class="pi-section pi-yellow" id="start" aria-labelledby="start-h">
  <div class="pi-wrap pi-center">
    <h2 id="start-h" class="framer-text framer-styles-preset-9kqwf9 pi-h2">Start your case. It takes about ten minutes.</h2>
    <p class="framer-text framer-styles-preset-1fc2js5 pi-lead">Message us on WhatsApp, or answer a few questions here. You can stop and come back. Nothing here commits you to anything. It’s free to find out if we can help.</p>
    <p class="framer-text framer-styles-preset-u2fub4 pi-muted">Tell us what happened and send any photos or documents you have. A Texas attorney will review your case, usually [the same day]. Se habla español, from your first message to your settlement.</p>
  </div>
  <div class="pi-wrap pi-narrow">
    <form class="pi-card pi-form" id="intake" novalidate>
      <p class="framer-text framer-styles-preset-lit60w pi-step">step 2</p>
      <h3 class="framer-text framer-styles-preset-1jvhhyw pi-h3">Tell us what happened.</h3>
      <div class="pi-field"><label for="f-type" class="framer-text framer-styles-preset-7jf1zc">1. What type of injury or incident</label><select id="f-type" name="type" class="pi-select framer-text framer-styles-preset-u2fub4"><option value="">Choose one</option>{options}<option value="other">Something else</option></select></div>
      <div class="pi-field"><label for="f-when" class="framer-text framer-styles-preset-7jf1zc">2. When and where it happened</label><input id="f-when" name="when" type="text" class="pi-input framer-text framer-styles-preset-u2fub4" autocomplete="off"></div>
      <div class="pi-field"><label for="f-who" class="framer-text framer-styles-preset-7jf1zc">3. Who was involved</label><input id="f-who" name="who" type="text" class="pi-input framer-text framer-styles-preset-u2fub4" autocomplete="off"></div>
      <div class="pi-field"><label for="f-injury" class="framer-text framer-styles-preset-7jf1zc">4. Your injuries and treatment so far</label><textarea id="f-injury" name="injury" rows="4" class="pi-input framer-text framer-styles-preset-u2fub4"></textarea></div>
      <div class="pi-field"><label for="f-docs" class="framer-text framer-styles-preset-7jf1zc">5. Documents you already have (photos, police report, medical bills)</label><input id="f-docs" name="docs" type="file" multiple class="pi-input pi-file framer-text framer-styles-preset-u2fub4"></div>
      <div class="pi-field"><label for="f-contact" class="framer-text framer-styles-preset-7jf1zc">6. How to reach you</label><input id="f-contact" name="contact" type="text" class="pi-input framer-text framer-styles-preset-u2fub4" autocomplete="off" placeholder="Phone or email"></div>
      <button type="submit" class="pi-submit framer-text framer-styles-preset-ivrpyo">Submit my case</button>
      <p class="pi-form-msg framer-text framer-styles-preset-u2fub4" id="intake-msg" hidden>Thank you. This prototype is not connected to the office yet, so nothing was sent. {chip('CONFIRM: where submissions go')}</p>
      <p class="pi-fine framer-text framer-styles-preset-10holly">Contacting us does not create an attorney-client relationship until a fee agreement is signed. A Texas attorney reviews your answers and will contact you. {chip('CONFIRM: response time, and whether first contact is by text, call or email')}</p>
    </form>
  </div>
</section>
"""

    cta = f"""
<section class="pi-section pi-cream pi-cta" id="cta" aria-labelledby="cta-h">
  <div class="pi-wrap pi-center">
    <h2 id="cta-h" class="framer-text framer-styles-preset-g3m289 pi-h2">You've been through enough. Let us handle the legal part.</h2>
    <div class="pi-btnrow">{btn('Start your case', '#start')}</div>
  </div>
</section>
"""
    return calculator, pricing, steps, why, faq, start, cta, rates_json


PI_CSS = """
<style id="pi-styles">
/* ---- [FIRM NAME] additions on top of the Framer export ---- */
html{scroll-behavior:smooth}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
.framer-xvfz0d{pointer-events:auto}
.pi-section{pointer-events:auto;width:100%;padding:120px 76px;display:flex;flex-direction:column;align-items:center;gap:56px;position:relative}
.pi-tight{padding-top:40px}
.pi-yellow{background:var(--token-dfd7ceb1-6225-41fe-9a08-4ed6d573c4d7,#ffe435)}
.pi-offwhite{background:var(--token-7cae8dd2-24df-443f-a575-fbb10e3d85a1,#f7f5ef)}
.pi-cream{background:var(--token-4c494f9f-03b3-4eac-88e8-f5161b116659,#f4efe1)}
.pi-wrap{width:100%;max-width:1100px;display:flex;flex-direction:column;gap:24px}
.pi-narrow{max-width:820px}
.pi-center{align-items:center;text-align:center}
.pi-center .framer-text{--framer-text-alignment:center}
.pi-h2{--framer-text-color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);max-width:900px}
.pi-h3{--framer-font-size:34px;--framer-line-height:1.05em;--framer-text-color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a)}
.pi-lead{--framer-text-color:var(--token-0fbfde70-3fa3-4b81-b4fe-9e6f34be838d,#2d2926);max-width:760px}
.pi-muted{--framer-text-color:var(--token-0fbfde70-3fa3-4b81-b4fe-9e6f34be838d,#2d2926)}
.pi-step{--framer-text-color:var(--token-0fbfde70-3fa3-4b81-b4fe-9e6f34be838d,#2d2926);text-transform:uppercase;letter-spacing:.08em}
.pi-card{background:var(--token-7cae8dd2-24df-443f-a575-fbb10e3d85a1,#f7f5ef);border:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb);border-radius:28px;padding:48px;display:flex;flex-direction:column;gap:20px;width:100%}
.pi-calc{display:flex;flex-direction:column;gap:28px;margin-top:12px}
.pi-field{display:flex;flex-direction:column;gap:10px}
.pi-field label{display:flex;justify-content:space-between;gap:16px;align-items:baseline;flex-wrap:wrap}
.pi-amount-out{font-variant-numeric:tabular-nums}
.pi-select,.pi-input{width:100%;background:#fff;border:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb);border-radius:12px;padding:14px 16px;font:inherit;color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a)}
.pi-file{padding:10px}
.pi-select:focus-visible,.pi-input:focus-visible,.pi-range:focus-visible,.pi-submit:focus-visible,.pi-btn:focus-visible,.pi-faq summary:focus-visible,.pi-next:focus-visible{outline:3px solid var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);outline-offset:3px}
.pi-range{width:100%;accent-color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);height:44px;cursor:pointer}
.pi-range-ends{display:flex;justify-content:space-between;--framer-text-color:#5f564a}
.pi-results{margin:0;display:flex;flex-direction:column;border-top:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb)}
.pi-row{display:grid;grid-template-columns:1fr auto;gap:8px 24px;align-items:center;padding:18px 0;border-bottom:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb)}
.pi-row dt{--framer-text-color:var(--token-0fbfde70-3fa3-4b81-b4fe-9e6f34be838d,#2d2926)}
.pi-row dd{margin:0}
.pi-rowchip{grid-column:1/-1;margin:0}
.pi-num{--framer-font-size:30px;--framer-line-height:1em;--framer-text-color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);font-variant-numeric:tabular-nums;text-align:right}
.pi-num-big{--framer-font-size:48px}
.pi-num-dim{--framer-text-color:#5f564a}
.pi-row-hero{background:var(--token-dfd7ceb1-6225-41fe-9a08-4ed6d573c4d7,#ffe435);margin:0 -24px;padding:22px 24px;border-radius:16px;border-bottom:0}
.pi-row-diff dt{--framer-font-weight:700}
.pi-fine{--framer-text-color:#5f564a}
.pi-note{--framer-text-color:#5f564a}
.pi-next{--framer-text-color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);text-decoration:none;align-self:flex-start;padding:8px 0}
.pi-next:hover{text-decoration:underline}
.pi-confirm{display:inline-block;background:#fff;border:1.5px dashed var(--token-76f4be20-9375-4d38-806a-aa3dc90a1b1c,#f97815);color:#8a3f00;border-radius:8px;padding:2px 8px;font:600 12px/1.4 "Instrument Sans",system-ui,sans-serif;letter-spacing:0;vertical-align:middle;white-space:normal}
.pi-table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb);border-radius:20px;overflow:hidden}
.pi-table th,.pi-table td{text-align:left;padding:22px 28px;border-bottom:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb);vertical-align:middle}
.pi-table thead th{background:var(--token-4c494f9f-03b3-4eac-88e8-f5161b116659,#f4efe1);--framer-text-color:#5f564a;text-transform:uppercase;letter-spacing:.06em}
.pi-table tbody tr:last-child td,.pi-table tbody tr:last-child th{border-bottom:0}
.pi-rate{--framer-font-size:34px;--framer-line-height:1em;--framer-text-color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a)}
.pi-steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:40px}
.pi-steps li{display:flex;flex-direction:column;gap:16px;padding:36px;border:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb);border-radius:24px;background:#fff}
.pi-steps p{--framer-text-color:var(--token-0fbfde70-3fa3-4b81-b4fe-9e6f34be838d,#2d2926);--framer-font-size:20px}
.pi-faq{border-bottom:1px solid var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb)}
.pi-faq-g{margin:44px 0 6px}
.pi-faq summary{cursor:pointer;padding:22px 44px 22px 0;position:relative;list-style:none;--framer-text-color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a)}
.pi-faq summary::-webkit-details-marker{display:none}
.pi-faq summary::after{content:"+";position:absolute;right:4px;top:50%;transform:translateY(-50%);font:600 30px/1 "Instrument Sans",system-ui,sans-serif}
.pi-faq[open] summary::after{content:"\\2212"}
.pi-faq p{padding:0 0 24px;--framer-text-color:var(--token-0fbfde70-3fa3-4b81-b4fe-9e6f34be838d,#2d2926);max-width:720px}
.pi-form{gap:22px}
.pi-submit{align-self:flex-start;background:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);color:var(--token-7cae8dd2-24df-443f-a575-fbb10e3d85a1,#f7f5ef);--framer-text-color:var(--token-7cae8dd2-24df-443f-a575-fbb10e3d85a1,#f7f5ef);border:0;border-radius:50px;padding:17px 28px;min-height:44px;cursor:pointer;text-transform:uppercase;letter-spacing:.04em}
.pi-form-msg{--framer-text-color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a)}
.pi-btnrow{display:flex;justify-content:center;margin-top:8px}
.pi-btn{text-decoration:none}
.pi-cta{padding:160px 76px}
/* Nav: wordmark instead of the Stack logo, no hamburger, show items on small screens */
.pi-wordmark{font:800 22px/1 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.02em;color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);white-space:nowrap}
.framer-e8x4r3 .hidden-yycdle{display:flex!important}
/* "We win when" block: it shared its row with a testimonial we removed */
.framer-1jmthpb,.framer-TzIF9 .framer-1jmthpb{width:100%;max-width:820px}
.framer-1g735ip,.framer-TzIF9 .framer-1g735ip{justify-content:center!important}
[id]{scroll-margin-top:96px}
/* Footer: was pinned to the viewport bottom by the bundle. !important beats Framer's per-breakpoint rules. */
.framer-1ebd1db,.framer-TzIF9 .framer-1ebd1db{position:relative!important;height:auto!important;width:100%!important;flex:none!important;padding:120px 0 56px!important;bottom:auto!important}
.framer-1w3xnl7,.framer-TzIF9 .framer-1w3xnl7{height:auto!important;flex:none!important;width:100%!important;flex-direction:row!important;justify-content:space-between!important;align-items:flex-end!important;gap:40px!important;padding:0 40px!important}
.framer-8pye7d,.framer-TzIF9 .framer-8pye7d{width:auto!important;max-width:60%!important;height:auto!important;flex:none!important}
.framer-whz10a,.framer-TzIF9 .framer-whz10a{width:auto!important;max-width:380px!important;height:auto!important;flex:none!important}
.framer-xj49yz,.framer-TzIF9 .framer-xj49yz{pointer-events:auto;height:auto!important;overflow:visible!important}
.framer-nh45d3,.framer-TzIF9 .framer-nh45d3{position:relative!important;top:auto!important;height:auto!important;width:100%!important}
/* Nav: transparent over the hero, solid once the page scrolls */
.framer-e8x4r3{transition:background-color .2s ease,box-shadow .2s ease}
.framer-e8x4r3.pi-nav-solid{background:rgba(247,245,239,.94);box-shadow:0 1px 0 var(--token-f4c92abb-11df-44de-9d88-b3a28d1e0eaf,#c9c4bb);backdrop-filter:blur(8px)}
.pi-footer-mark{font:800 clamp(56px,12vw,180px)/.9 "Perfektta ExtraBold","Instrument Sans",system-ui,sans-serif;letter-spacing:-.04em;color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);word-break:break-word}
.pi-footer-links{display:flex;gap:24px;flex-wrap:wrap}
.pi-footer-links a{--framer-text-color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1,#140c0a);text-decoration:underline;text-underline-offset:3px;padding:6px 0}
@media(max-width:1199.98px){.framer-e8x4r3{padding:20px 28px}}
@media(max-width:809.98px){
  .pi-section{padding:72px 20px;gap:36px}
  .pi-cta{padding:96px 20px}
  .pi-card{padding:28px 20px;border-radius:20px}
  .pi-steps{grid-template-columns:1fr;gap:20px}
  .pi-steps li{padding:26px}
  .pi-h3{--framer-font-size:28px}
  .pi-num{--framer-font-size:24px}
  .pi-num-big{--framer-font-size:36px}
  .pi-row{grid-template-columns:1fr;gap:6px}
  .pi-num{text-align:left}
  .pi-row-hero{margin:0 -12px;padding:18px 12px}
  .pi-table th,.pi-table td{padding:14px 12px}
  .pi-rate{--framer-font-size:26px}
  .framer-e8x4r3{padding:14px 16px}
  .framer-e8x4r3 .framer-1ezgx8l{display:none}
  .pi-wordmark{font-size:18px}
  .framer-1ebd1db,.framer-TzIF9 .framer-1ebd1db{padding:72px 0 40px!important}
  .framer-1w3xnl7,.framer-TzIF9 .framer-1w3xnl7{padding:0 20px!important;flex-direction:column!important;align-items:flex-start!important;gap:32px!important}
  .framer-8pye7d,.framer-TzIF9 .framer-8pye7d{max-width:100%!important}
  .framer-whz10a,.framer-TzIF9 .framer-whz10a{max-width:100%!important}
}
</style>
"""

PI_JS = """
<script>
(function(){
  var RATES = __RATES__;
  var INDUSTRY = __INDUSTRY__, COSTS = __COSTS__;
  var sel = document.getElementById('case-type'), rng = document.getElementById('amount');
  if (!sel || !rng) return;
  var out = {
    amount: document.getElementById('amount-out'), rate: document.getElementById('out-rate'),
    fee: document.getElementById('out-fee'), keep: document.getElementById('out-keep'), costs: document.getElementById('out-costs'),
    industry: document.getElementById('out-industry'), diff: document.getElementById('out-diff')
  };
  function money(n){ return '$' + Math.round(n).toLocaleString('en-US'); }
  function update(){
    var amount = Number(rng.value), rate = RATES[sel.value] || 0;
    var costs = Math.max(500, Math.round(amount * COSTS / 500) * 500), net = amount - costs;
    var fee = net * rate, keep = net - fee, ind = net * INDUSTRY;
    out.amount.textContent = money(amount); rng.setAttribute('aria-valuetext', money(amount));
    out.rate.textContent = '(' + Math.round(rate * 100) + '%)';
    out.costs.textContent = money(costs); out.fee.textContent = money(fee); out.keep.textContent = money(keep);
    out.industry.textContent = money(ind); out.diff.textContent = money(ind - fee);
  }
  sel.addEventListener('change', update); rng.addEventListener('input', update); update();
  var nav = document.querySelector('.framer-e8x4r3');
  function onScroll(){ if (nav) nav.classList.toggle('pi-nav-solid', window.scrollY > 24); }
  window.addEventListener('scroll', onScroll, {passive: true}); onScroll();
  var form = document.getElementById('intake'), msg = document.getElementById('intake-msg');
  if (form) form.addEventListener('submit', function(e){ e.preventDefault(); msg.hidden = false; msg.scrollIntoView({block:'nearest'}); });
})();
</script>
"""


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------
def main():
    src = SRC.read_text(encoding="utf-8")
    t = Tree(src)
    c = CONFIG

    # --- head: keep styles and preloads, drop scripts, Stack metas and icons
    head_node = t.find(lambda n: n["tag"] == "head")
    head = t.inner(head_node)
    head = re.sub(r"<script\b.*?</script>", "", head, flags=re.S)
    head = re.sub(r"<title>.*?</title>", "", head, flags=re.S)
    head = re.sub(r"<meta\b[^>]*(?:name|property)=\"(?:description|robots|og:[^\"]+|twitter:[^\"]+|framer-search-index[^\"]*|generator)\"[^>]*>", "", head)
    head = re.sub(r"<link\b[^>]*rel=\"(?:canonical|icon)\"[^>]*>", "", head)
    head = re.sub(r"<!--[^$].*?-->", "", head, flags=re.S)  # html comments, keep <!--$-->
    sync_schema_faq()
    schema_block = re.search(r"<script type=\"application/ld\+json\">.*?</script>", SCHEMA.read_text(encoding="utf-8"), re.S).group(0)
    meta = f"""
  <title>{c['title']}</title>
  <meta name="description" content="{c['description']}">
  <link rel="canonical" href="https://{c['domain']}/">
  {'<meta name="robots" content="noindex, nofollow">' if c['noindex'] else ''}
  <meta property="og:type" content="website">
  <meta property="og:title" content="{c['title']}">
  <meta property="og:description" content="{c['description']}">
  <meta property="og:url" content="https://{c['domain']}/">
  {schema_block}
"""

    # --- wrappers
    main_div = t.find(by_id("main"))
    wrap1 = main_div["children"][1] if main_div["children"][0]["tag"] == "style" else main_div["children"][0]
    html_style = t.html(main_div["children"][0]) if main_div["children"][0]["tag"] == "style" else ""
    wrap1_open = src[wrap1["start"]:src.find(">", wrap1["start"]) + 1]
    wrap2 = [n for n in wrap1["children"] if "framer-hd6jU" in (n["attrs"].get("class") or "")][0]
    wrap2_open = src[wrap2["start"]:src.find(">", wrap2["start"]) + 1]
    main_node = t.find(by_name("MAIN"))
    main_open = src[main_node["start"]:src.find(">", main_node["start"]) + 1]

    # --- button template from the hero
    hero = t.find(by_name("HERO"))
    hero_btn_a = t.find_all(lambda n: n["tag"] == "a" and "framer-Xp2gR" in (n["attrs"].get("class") or ""), hero["children"])[0]
    btn_tpl = t.html(hero_btn_a)
    btn = lambda text, href, extra="": pill_button(btn_tpl, text, href, extra)

    # --- nav
    nav = t.find(by_name("Nav"))
    nav_html = t.html(nav)
    hamburger = [n for n in nav["children"] if n["tag"] == "button"]
    if hamburger:
        nav_html = nav_html.replace(t.html(hamburger[0]), "")
    nav_html = replace_once(nav_html, '<div class="framer-DJN29 framer-cqcfvd"></div>', f'<span class="pi-wordmark">{c["firm"]}</span>', "nav logo")
    nav_html = replace_once(nav_html, 'href="./brokers">For Brokers', 'href="#pricing">Pricing', "nav link")
    nav_html = re.sub(r'<a name="Nav Watch a demo" class="framer-cLKaN', '<a href="#start" name="Start your case" class="framer-cLKaN', nav_html, count=1)
    nav_html = replace_once(nav_html, ">Instant Quote</p>", ">Start your case</p>", "nav button")
    nav_html = nav_html.replace('data-framer-page-link-current="true"', "")
    nav_html = re.sub(r'\sdata-highlight="true"|\stabindex="0"', "", nav_html)
    nav_html = strip_comments(nav_html)

    # --- hero
    hero_html = t.html(hero)
    triggers = [n for n in hero["children"] if n["attrs"].get("data-framer-name") == "TRIGGERS"]
    if triggers:
        hero_html = hero_html.replace(t.html(triggers[0]), "")
    for turtle in t.find_all(by_name("Turtle"), hero["children"]):  # Stack's mascot illustration
        hero_html = hero_html.replace(t.html(turtle), "")
    hero_html = derevelo(hero_html)
    hero_html = unhide(hero_html)
    hero_html = replace_once(hero_html, "We’re putting an end to the Brutal Renewal.", "We’re putting an end to high legal fees.", "hero h1")
    hero_html = replace_once(hero_html,
        "You know what’s absurd? A surprise 20% hike on your team’s group plan. But that’s commonplace today. That’s why we built Stack.",
        "We win when you win. Simple as that. Most injury firms take 33–40% of your settlement. We take 10%, and it stays 10% even if we go to trial. Move the slider, see what you’d keep.", "hero p")
    hero_html = hero_html.replace(btn_tpl, btn("See what you’d keep", "#calculator"), 1)
    hero_html = strip_comments(hero_html)

    # --- we win when
    wwh = t.find(by_name("WE WIN WHEN"))
    wwh_html = t.html(wwh)
    content = [n for n in wwh["children"] if n["attrs"].get("data-framer-name") == "Content"][0]
    testimonial = [n for n in content["children"] if "framer-lstnog" in (n["attrs"].get("class") or "")]
    if testimonial:
        wwh_html = wwh_html.replace(t.html(testimonial[0]), "")
    # Stack's hand-drawn list icons (hand, asterisk, boxing glove) are its brand art; drop the icon slots
    benefits = t.find_all(by_name("Benefits List Section"), wwh["children"])
    if benefits:
        for svg in t.find_all(lambda n: n["attrs"].get("data-framer-component-type") == "SVG", benefits[0]["children"]):
            slot = t.find_all(lambda n: svg in n["children"], benefits[0]["children"])
            wwh_html = wwh_html.replace(t.html(slot[0] if slot else svg), "")
    wwh_html = derevelo(wwh_html)
    wwh_html = unhide(wwh_html)
    wwh_html = re.sub(r"We win when you and your team are <span([^>]*)>happy\.</span>", r"We win when <span\1>you win.</span>", wwh_html)
    wwh_html = wwh_html.replace("We’re not selling your team a plan. We’re helping them find the right one.",
                                "The insurance company decides how much to pay based on your case, not on what your lawyer charges. A lower fee doesn’t mean a smaller settlement. It means you keep more of it.")
    wwh_html = wwh_html.replace(">No conflicts.</p>", ">No markup on costs.</p>").replace(">No asterisks.</p>", ">No admin fees.</p>")
    wwh_html = strip_comments(wwh_html)
    for needed in ("you win.", "No markup on costs.", "No admin fees.", "Just someone in your corner."):
        if needed not in wwh_html:
            raise SystemExit(f"build: we-win-when text missing: {needed}")

    # --- footer
    footer_outer = t.find(by_class("framer-xj49yz"))
    footer_html = t.html(footer_outer)
    mark = t.find_all(by_class("framer-8pye7d"), footer_outer["children"])[0]
    footer_html = footer_html.replace(t.html(mark), f'<div class="framer-8pye7d"><p class="pi-footer-mark" aria-label="{c["firm"]}">{c["firm"]}</p></div>')
    disclaimer = t.find_all(by_name("Disclaimer"), footer_outer["children"])[0]
    disc_p = [n for n in disclaimer["children"] if n["tag"] == "p"][0]
    new_disc = (f'<p class="framer-text framer-styles-preset-10holly" dir="auto" style="--framer-text-color:var(--token-561f5218-1b33-40dd-8dce-1b36fc074fd1, rgb(20, 12, 10))">'
                f'{c["firm"]} {chip("PLLC")}, Texas.<br>'
                f'Our fee is 10% of the amount recovered, calculated after case costs are repaid. If there is no recovery, you owe no fee and no case costs. Medical bills and liens are paid from your recovery. Every case is different, and past results do not guarantee future results.<br>'
                f'{c["firm"]} uses software, including AI, and a supervised case team to prepare work; a licensed attorney reviews and approves legal work. Contacting us does not create an attorney-client relationship until a fee agreement is signed. {chip("Not certified by the Texas Board of Legal Specialization, if applicable")}. Attorney advertising. Typical fee figures based on {chip("Texas Fee Index, date")}. The calculator is an example only.</p>')
    footer_html = footer_html.replace(t.html(disc_p), new_disc)
    links = t.find_all(by_name("Links Container"), footer_outer["children"])[0]
    footer_html = footer_html.replace(t.html(links),
        '<div class="framer-p6032j pi-footer-links" data-framer-name="Links Container">'
        '<a class="framer-text framer-styles-preset-10holly" href="#privacy">Privacy</a>'
        '<a class="framer-text framer-styles-preset-10holly" href="#terms">Terms</a>'
        '<a class="framer-text framer-styles-preset-10holly" href="#disclaimer">Disclaimer</a></div>')
    footer_html = re.sub(r"© 2026 Stack Healthcare, Inc\. All rights reserved\.", f"© 2026 {c['firm']}. All rights reserved.", footer_html)
    footer_html = footer_html.replace("Stack Healthcare", c["firm"])
    footer_html = strip_comments(footer_html)
    # the big-logo link next to the disclaimer pointed at Stack's home
    footer_html = re.sub(r'<a class="framer-18cgtl3 framer-1f2myp"[^>]*>.*?</a>', "", footer_html, flags=re.S)

    # --- svg sprite (arrow icon in pill buttons)
    sprite = t.find(by_id("svg-templates"))
    sprite_html = t.html(sprite)

    # --- new sections
    calculator, pricing, steps, why, faq, start, cta, rates_json = build_sections(btn)
    js = PI_JS.replace("__RATES__", rates_json).replace("__INDUSTRY__", str(c["industry_rate"])).replace("__COSTS__", str(c["costs_share"]))

    body_open = src[t.find(lambda n: n["tag"] == "body")["start"]:]
    body_open = body_open[:body_open.find(">") + 1]
    html_open = src[t.find(lambda n: n["tag"] == "html")["start"]:]
    html_open = html_open[:html_open.find(">") + 1]

    page = f"""<!doctype html>
<!-- Built by tools/build_site.py from source/mystack-index.html. Do not edit by hand; edit the script and rebuild. -->
{html_open}
<head>
{head.strip()}
{meta}
{PI_CSS}
</head>
{body_open}
<div id="main">{html_style}{wrap1_open}
{nav_html}
{wrap2_open}{main_open}
{hero_html}
{calculator}
{pricing}
{steps}
{wwh_html}
{why}
{faq}
{start}
{cta}
</div></div>
{footer_html}
</div></div>
{sprite_html}
{js}
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")

    # --- self-checks
    for forbidden in ("Stack", "Brutal Renewal", "Instant quote", "Instant Quote", "For Brokers", "ICHRA", "hs-scripts", "googletagmanager", "script_main"):
        hits = [m.start() for m in re.finditer(forbidden, page)]
        hits = [h for h in hits if not (forbidden == "Stack" and page[h-1:h+7] in ("[Stack", "Stack T", "Stack S", "Stack s", "Stack M") and "data-framer-name" in page[max(0,h-40):h])]
        if hits and forbidden != "Stack":
            raise SystemExit(f"build: leftover '{forbidden}' at {hits[:3]}")
    visible_faq = re.findall(r'<details class="pi-faq"><summary[^>]*>(.*?)</summary><p[^>]*>(.*?)</p></details>', page, re.S)
    schema = json.loads(re.search(r"<script type=\"application/ld\+json\">(.*?)</script>", schema_block, re.S).group(1))
    faq_node = next(n for n in schema["@graph"] if n["@type"] == "FAQPage")["mainEntity"]
    for (q, a), s in zip(visible_faq, faq_node):
        if q != s["name"] or a != s["acceptedAnswer"]["text"]:
            raise SystemExit(f"build: FAQ text differs from schema: {q!r}")
    assert page.count("<h1") == 1, "expected exactly one h1"
    print(f"built {OUT.relative_to(ROOT)}: {len(page):,} bytes; {page.count('pi-confirm')} CONFIRM chips; FAQ in sync with schema; 1 h1")


if __name__ == "__main__":
    main()
