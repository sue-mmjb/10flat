# Audit directives: [FIRM NAME] personal injury site

Input for the `website-presubmission-audit` skill (its Step 0). Copy this file into the repo root when the site is built. Everything here comes from Tim's instructions of 30 October 2026 or is a placeholder Tim must fill. Tim's directives are final: the audit reports where the site contradicts them, nothing more.

## Business facts the site must state identically everywhere

| Fact | Value | Status |
|---|---|---|
| Firm name | [FIRM NAME] | Pending (Chandana producing 3 to 5 options) |
| Domain | https://[DOMAIN]/ | Pending |
| Address | [STREET ADDRESS, CITY, STATE ZIP] | Pending |
| Phone | [PHONE] | Pending |
| Email | [EMAIL] | Pending |
| Hours | [CONFIRM] | Pending |
| Jurisdiction | [CONFIRM] | Pending |
| Responsible attorney | [ATTORNEY NAME], [BAR NUMBER], [STATE] | Pending (Azure) |

The audit must fail any page where the footer, the contact page and the JSON-LD disagree on any of these.

## Pricing rule

Do not judge the prices. Flag only where two places disagree. The published figures are:

- Car accidents: 25% contingency. Confirmed by Tim.
- Medical malpractice: 33%. Confirmed by Tim.
- Dental malpractice: 33%. Confirmed by Tim.
- Amount due at the start: Tim said both "$500 dollars down" and "what you owe us today $0". Unresolved. Any page that states either figure as fact before Tim resolves it is a P0.
- Every other case type and rate is proposed only. Publishing one before Tim approves it is a P0.

## Structured data

- Every page: `LegalService` with the firm block.
- Home and Pricing: `FAQPage` whose question and answer text matches the visible FAQ character for character.
- No `AggregateRating`, `Review`, or `award` properties. The firm has none.

## Content that must not appear anywhere

| Category | Phrases | Why |
|---|---|---|
| Unconfirmed promises | "free consultation", "free case review", "no fee unless we win", "no win no fee", "nothing to lose" | Implied by Tim's "$0 today" but contradicted by "$500 down". Not confirmed. |
| Overclaiming | "specialist", "specialized", "board-certified", "best", "#1", "top-rated", "award-winning", "guarantee", "guaranteed", "painless" | Bar advertising rules; no credentials supplied. "Guarantee" is allowed only inside a disclaimer that says there is none, e.g. "do not guarantee". |
| Results | any dollar figure described as recovered, won or obtained; "millions recovered"; "track record" | No results exist. |
| Testimonials | any quoted client | None exist. |
| Attorney claims | years of experience, number of cases, "former insurance lawyer", any bio detail | None supplied. |
| Internal matters | "Iozera", "Kevin", "Azure", "Azra", "VN Group", ownership percentages, "AI-driven law firm" as a business description | Internal. Whether the site says "AI" at all is Tim's open question 4. |
| Placeholders | "[CONFIRM", "[FIRM NAME]", "[DOMAIN]", "[PHONE]", "[ATTORNEY", "lorem", "TODO", "example.com", "555-" | Unfinished content. |

## Allowed exceptions

- "$0" may appear only as the value of the calculator row "What you owe us today", and only after Tim confirms it.
- "guarantee" may appear only in the negative, in the calculator note and footer disclaimer.
- "AI" may appear only if Tim answers question 4 in `PI-Website-Content-Draft.md` with yes.

## Known risks to look at first

- The fee calculator is client-side JavaScript. Its default state must be server-rendered.
- The design is cloned from mystack.com, which uses scroll animations. Check every reveal for hidden-by-default content and reduced-motion handling.
- The FAQ accordion must keep every answer in the DOM when closed.
