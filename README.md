# [FIRM NAME] personal injury website

Prototype of the personal injury law firm site Tim asked for on 30 October 2026, built on the mystack.com clone he chose as the design reference.

**Live preview:** https://personal-injury-law-nine.vercel.app/ (clone) and https://personal-injury-law-nine.vercel.app/v2/ (rebuilt). Vercel redeploys automatically on every push to `main`.

## Folders

| Folder | What it is |
|---|---|
| `site/` | The built website, two versions. `site/index.html` is the **clone**: mystack.com with every tile, illustration and logo row kept and only the text swapped, so Tim sees the cloned site as he asked. `site/v2/index.html` is the **rebuilt** version: same look, but the sections are clean HTML with a working calculator, pricing table, FAQ and intake form. Vercel serves this folder, so the clone is at `/` and the rebuilt version at `/v2/`. |
| `source/` | The untouched mystack.com clone (`mystack-index.html`). Never edit it. |
| `tools/` | `build_site.py` generates `site/index.html` from the clone plus the content below. |
| `content/` | Tim's verbatim instructions (`TIM-INSTRUCTIONS.md`, the source of truth), the approved copy (`PI-Website-Content.txt`), the strategy and open questions (`PI-Website-Content-Draft.md`), the developer spec (`PI-Website-Content-Pack.md`), the audit directives, and the JSON-LD in `schema/`. |

## Rebuild after a change

Edit `tools/build_site.py` (the `CONFIG` and `FAQ` blocks at the top hold every piece of text that is likely to change) for the rebuilt version, or the swap lists in `tools/build_clone.py` for the clone, then:

```bash
python tools/build_clone.py
```

```bash
python tools/build_site.py
```

The clone drops Framer's JavaScript bundle on purpose: tested 30 October 2026, the bundle re-renders the page from Stack's data a few seconds after load and puts Stack's text back. The CSS block in `build_clone.py` freezes the scroll animations the bundle used to drive. Two things in the clone are placeholders by nature: the partner and insurance-carrier logo rows are Stack's logos kept as tiles, and the testimonial photo and quote cards are Stack's layouts with placeholder text.

The script refuses to build if the FAQ text no longer matches `content/schema/home.html`, if any Stack text survives, or if there is not exactly one h1.

To view it locally:

```bash
python -m http.server 8765 --directory site
```

then open http://localhost:8765/.

## What is placeholder

Everything inside an orange dashed `[CONFIRM ...]` chip on the page, and the firm name. The chips are deliberate: they show Tim exactly which decisions are still open. Section 7 of `content/PI-Website-Content-Draft.md` lists the same questions. The page carries `noindex` until launch (`CONFIG["noindex"]`).

## Before this can go live

1. **Fonts.** The clone loads Perfektta ExtraBold, GT Alpina and Instrument Sans from Framer's servers under mystack.com's licence. Perfektta and GT Alpina are commercial fonts. Before launch, either buy licences or swap to open fonts and self-host them.
2. **Framer-hosted assets.** Font files and the button arrow still come from `framerusercontent.com`. If Stack unpublishes or changes its site, they break. Self-host them.
3. **The intake form** does nothing yet. It needs a destination (email, CRM or the AI intake system from the meeting) and the attorney's sign-off on the no-relationship wording.
4. **Legal review.** The responsible attorney must approve the fee wording, the calculator disclaimer, the footer and whether the site may mention AI.
5. **Run the audit skill** (`website-presubmission-audit`) with `content/PI-AUDIT_DIRECTIVES.md` once the placeholders are filled.
