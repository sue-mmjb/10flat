"""Parts every page shares: <head> (link preview, icons, analytics), navigation, footer, fonts, base styles, and
finalize(), which strips source comments and checks a page before it is written.

Pages: tools/build_home.py (home, case-type pages, /fees, share pages, 404, robots, sitemap) and tools/build_start.py
(/start, /es/start, /privacy, /terms). tools/build.py runs both.
"""
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site import CONFIG  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
FIRM = CONFIG["firm"]
URL = CONFIG.get("site_url") or f"https://{CONFIG['domain']}"

CASE_PAGES = [  # slug, nav label, calculator type key, /start incident value
    ("car-accident", "Car accidents", "car", "Car accident"),
    ("truck-accident", "Truck accidents", "truck", "Truck accident"),
    ("slip-and-fall", "Slip and fall", "fall", "Slip and fall"),
    ("medical-injury", "Medical injury", "medical", "Medical injury"),
    ("dental-injury", "Dental injury", "dental", "Dental injury"),
]

# Vercel Web Analytics: cookieless page views once it is switched on in the Vercel project (Analytics > Enable).
ANALYTICS = ("<script>window.va=window.va||function(){(window.vaq=window.vaq||[]).push(arguments)};"
             "window.track=function(n,d){try{window.va('event',{name:n,data:d})}catch(e){}};</script>"
             '<script defer src="/_vercel/insights/script.js"></script>')

FONTS = """
@font-face{font-family:"Perfektta ExtraBold";src:url("https://framerusercontent.com/assets/ehgAhB5skp3UmdaHTx9XRxEGak.woff2");font-display:swap;font-weight:800}
@font-face{font-family:"GT Alpina Medium";src:url("https://framerusercontent.com/assets/akcrPmCPzVvRITrHAHEcGkGliuE.woff2");font-display:swap;font-weight:500}
@font-face{font-family:"Instrument Sans";src:url("https://fonts.gstatic.com/s/instrumentsans/v4/pximypc9vsFDm051Uf6KVwgkfoSxQ0GsQv8ToedPibnr-yp2JGEJOH9npSTF-QfwmS0v3_7Y.woff2");font-display:swap;font-weight:400}
@font-face{font-family:"Instrument Sans";src:url("https://fonts.gstatic.com/s/instrumentsans/v4/pximypc9vsFDm051Uf6KVwgkfoSxQ0GsQv8ToedPibnr-yp2JGEJOH9npSQb_gfwmS0v3_7Y.woff2");font-display:swap;font-weight:600}
"""

BASE_CSS = """
:root{--ink:#140c0a;--muted:#5f564a;--yellow:#ffe435;--egg:#f7f5ef;--sand:#e9dfc2;--field:#f4efe1;--line:#e3ded2;--white:#fff;--err:#b3261e;--ok:#2f6b3a}
*{box-sizing:border-box}
[hidden]{display:none!important}
html,body{margin:0;background:var(--egg);color:var(--ink);font:400 16px/1.5 "Instrument Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit}
.skip{position:absolute;left:12px;top:-60px;z-index:50;background:var(--ink);color:#fff;padding:10px 16px;border-radius:10px;font-weight:600;text-decoration:none}
.skip:focus{top:12px}
.nav{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:28px;padding:16px 32px;background:rgba(247,245,239,.94);backdrop-filter:blur(8px)}
.mark{font:800 26px/1 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.03em;text-decoration:none;margin-right:auto}
.navlinks{display:flex;gap:24px;font:600 15px/1 "Instrument Sans",sans-serif}
.navlinks a{text-decoration:none}
.navlinks a:hover{text-decoration:underline;text-underline-offset:4px}
.navbtn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 20px;border-radius:999px;background:var(--ink);color:var(--yellow);font:600 15px/1 "Instrument Sans",sans-serif;text-decoration:none}
.navbtn:hover{background:#2c211d}
.lang{font:600 15px/1 "Instrument Sans",sans-serif;text-decoration:underline;text-underline-offset:4px}
h1{font:800 clamp(40px,5vw,64px)/.95 "Perfektta ExtraBold","Instrument Sans",sans-serif;letter-spacing:-.03em;margin:0 0 24px}
footer{border-top:1px solid var(--line);padding:28px 32px 40px;max-width:1180px;margin:0 auto;font-size:12.5px;line-height:1.55;color:var(--muted)}
footer p{margin:0 0 12px}
.flinks{display:flex;flex-wrap:wrap;gap:8px 20px;align-items:center}
.flinks a{color:var(--ink);text-underline-offset:3px}
@media(max-width:760px){
  .navlinks{display:none}.nav{padding:12px 20px;gap:12px}.mark{font-size:22px}.navbtn{min-height:40px;padding:0 16px;font-size:14px}
  .has-mbar .nav .navbtn{display:none}
  footer{padding:24px 20px 36px}
}
"""

FOOT_EN = (
    f"{FIRM} PLLC, Texas, a law firm owned only by licensed attorneys. Our fee is 10% of the total amount recovered at every "
    "stage, including trial; case costs and liens are paid from your share after the fee. If there is no recovery, you owe no "
    "fee and no case costs. Every case is different, and past results do not guarantee future results. "
    f"{FIRM} uses software, including AI, and a supervised case team to prepare work; a licensed attorney reviews and approves "
    "legal work. The software company, 10flat Technologies, is paid a fixed fee and never shares in a recovery or a fee. "
    "Contacting us does not create an attorney-client relationship until a fee agreement is signed. Attorney advertising. "
    "Fee comparisons use a one-third (33%) fee, common for Texas injury cases. The calculator is an illustration, not a promise of any outcome."
)

FOOT_ES = (
    f"{FIRM} PLLC, Texas, un bufete de abogados cuyos dueños son solo abogados con licencia. Nuestros honorarios son el 10% del "
    "monto total recuperado en cada etapa, incluso en juicio; los gastos del caso y los gravámenes se pagan de su parte después "
    "de los honorarios. Si no hay recuperación, no debe honorarios ni gastos del caso. Cada caso es diferente. "
    "Comunicarse con nosotros no crea una relación abogado-cliente hasta que se firme un acuerdo de honorarios. Publicidad de abogados."
)


def head(title, desc, path, extra_css="", full_title=None, lang="en", og_image=None, og_title=None, og_alt=None):
    robots = '<meta name="robots" content="noindex, nofollow">' if CONFIG.get("noindex") else ""
    url = f"{URL}{path}"
    t = full_title or f"{title} | {FIRM}"
    img = og_image or f"{URL}/og.png"
    ogt = og_title or t
    alt = og_alt or "10% fee. Even at trial. 10flat Law."
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{FIRM}">
<meta property="og:title" content="{ogt}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{alt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{ogt}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#ffe435">
{ANALYTICS}
<style>{FONTS}{BASE_CSS}{extra_css}</style>
</head>"""


def nav(start_button=True, lang_link=None):
    btn = ('<a class="navbtn" href="/start" onclick="track(\'start_click\',{from:\'nav\'})">Start your case</a>'
           if start_button else "")
    lang = f'<a class="lang" href="{lang_link[0]}" hreflang="{lang_link[2]}">{lang_link[1]}</a>' if lang_link else ""
    return (f'<a class="skip" href="#main">Skip to content</a>'
            f'<header class="nav"><a class="mark" href="/" aria-label="{FIRM} home">{FIRM}</a>'
            '<nav class="navlinks" aria-label="Main"><a href="/#how">How it works</a><a href="/fees">Fees</a><a href="/#faq">FAQ</a></nav>'
            f'{lang}{btn}</header>')


def nav_es():
    return (f'<a class="skip" href="#main">Saltar al contenido</a>'
            f'<header class="nav"><a class="mark" href="/" aria-label="{FIRM}, inicio">{FIRM}</a>'
            '<a class="lang" href="/start" hreflang="en">English</a></header>')


def footer(text=FOOT_EN):
    cases = "".join(f'<a href="/{slug}">{label}</a>' for slug, label, *_ in CASE_PAGES)
    return (f'<footer><p>{escape(text)}</p><p class="flinks">{cases}<a href="/fees">Fees</a></p>'
            f'<p class="flinks"><a href="/privacy">Privacy</a><a href="/terms">Terms</a>'
            f'<span>© 2026 {FIRM}. All rights reserved.</span></p></footer>')


def footer_es():
    return (f'<footer><p>{escape(FOOT_ES)}</p><p class="flinks"><a href="/privacy" hreflang="en">Privacidad (en inglés)</a>'
            f'<a href="/terms" hreflang="en">Términos (en inglés)</a><span>© 2026 {FIRM}. Todos los derechos reservados.</span></p></footer>')


# Wording the reviews asked to remove; a page that contains any of it is not written.
FLAGGED = (
    "Se habla", "smaller settlement", "worth the same", "not on what your lawyer charges", "Most injury firms take",
    "guaranteed", "after case costs", "never goes up", "Where a one-third fee goes", "Staff who type letters",
    "Expensive offices", "other firms pay staff", "from about $1,000 up", "never rules it out",
    "settled between the firms out of the fee", "meet your attorney before you sign", "WhatsApp us",
)
PEOPLE = re.compile(r"\b(Sue|Tim|Chandana|Kevin|Azure|Danish|Nguyen)\b")


def strip_comments(page):
    page = re.sub(r"<!--.*?-->", "", page, flags=re.S)

    def css(m):
        return m.group(1) + re.sub(r"/\*.*?\*/", "", m.group(2), flags=re.S) + m.group(3)

    def js(m):
        code = re.sub(r"/\*.*?\*/", "", m.group(2), flags=re.S)
        code = re.sub(r"(?m)^[ \t]*//[^\n]*\n", "", code)
        code = re.sub(r"(?m)(?<=[;{})])[ \t]+//[^\n]*$", "", code)
        return m.group(1) + code + m.group(3)

    page = re.sub(r"(<style[^>]*>)(.*?)(</style>)", css, page, flags=re.S)
    page = re.sub(r"(<script(?![^>]*application/ld\+json)[^>]*>)(.*?)(</script>)", js, page, flags=re.S)
    return page


def finalize(page, rel_path, n_h1=1, flagged=True):
    """Strip comments, check the page and write it under site/."""
    page = strip_comments(page)
    body = page[page.find("<body"):]
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S)))
    m = re.search(r"\[[^\]]{2,80}\]", text)
    if m:
        raise SystemExit(f"{rel_path}: placeholder on the page: {m.group(0)!r}")
    if flagged:
        for bad in FLAGGED:
            if bad.lower() in text.lower():
                raise SystemExit(f"{rel_path}: flagged wording {bad!r}")
    m = PEOPLE.search(page)
    if m:
        raise SystemExit(f"{rel_path}: a person's name is in the page source: {m.group(0)!r}")
    if body.count("<h1") != n_h1:
        raise SystemExit(f"{rel_path}: {body.count('<h1')} h1")
    for img in re.findall(r"<img\b[^>]*>", body):
        if not re.search(r'alt="[^"]+"', img):
            raise SystemExit(f"{rel_path}: image without alt text: {img[:80]}")
    out = SITE / rel_path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return page
