# Audit directives: [FIRM NAME] personal injury site

Input for the `website-presubmission-audit` skill (its Step 0). Copy this file into the repo root when the site is built. Everything here comes from Tim's instructions of 30 October 2026 or is a placeholder Tim must fill. Tim's directives are final: the audit reports where the site contradicts them, nothing more.

## Business facts the site must state identically everywhere

| Fact | Value | Status |
|---|---|---|
| Firm name | 10flatlaw | Confirmed by Sue 31 Oct 2026 |
| Domain | https://10flatlaw.com/ | Confirmed by Sue 31 Oct 2026 ("website name is http://10flatlaw.com/") |
| Address | [STREET ADDRESS, CITY, STATE ZIP] | Pending |
| Phone | [PHONE] | Pending |
| Email | [EMAIL] | Pending |
| Hours | [CONFIRM] | Pending |
| Jurisdiction | [CONFIRM] | Pending |
| Responsible attorney | [ATTORNEY NAME], [BAR NUMBER], [STATE] | Pending (Azure) |

The audit must fail any page where the footer, the contact page and the JSON-LD disagree on any of these.

## Pricing rule

Do not judge the prices. Flag only where two places disagree. The published figures, from the 10flat brief Tim shared on 30 October 2026 (applied 31 October):

- Base attorney fee: 10% of the gross recovery on qualifying cases. Every case type on the site (car accident, medical injury, dental injury) shows the same 10%. A case-type control must not change the fee.
- Optional Premium (Attorney-Led): 25% total attorney fee. It replaces the 10% fee. Must be described as optional, client-chosen and signed; "no automatic upgrades".
- Upfront payment: "see your signed terms". Any "$0 upfront" or "$0 down" is a P0 until Tim confirms the agreement provides it.
- No hourly option. Any "$50" or "per hour" is a P0.
- The old 25% car / 33% malpractice figures are a P0 anywhere they survive.
- No fee increase at filing, trial or appeal is published. If one is introduced, the 10% claim must carry the qualification conspicuously.
- Every other case type and rate is proposed only. Publishing one before Tim approves it is a P0.
- Calculator figures must be labelled "after attorney fee, before costs and liens", never "what you keep" or "take home", with costs and liens shown as not yet estimated.

## Structured data

- Every page: `LegalService` with the firm block.
- Home and Pricing: `FAQPage` whose question and answer text matches the visible FAQ character for character.
- No `AggregateRating`, `Review`, or `award` properties. The firm has none.

## Content that must not appear anywhere

| Category | Phrases | Why |
|---|---|---|
| Unconfirmed promises | "free consultation", "free case review", "no fee unless we win", "no win no fee", "nothing to lose", "AI lawyer", "cheapest" | The 10flat brief forbids these outright; costs may still be owed after a loss. |
| Overclaiming | "specialist", "specialized", "board-certified", "best", "#1", "top-rated", "award-winning", "guarantee", "guaranteed", "painless" | Bar advertising rules; no credentials supplied. "Guarantee" is allowed only inside a disclaimer that says there is none, e.g. "do not guarantee". |
| Results | any dollar figure described as recovered, won or obtained; "millions recovered"; "track record" | No results exist. |
| Testimonials | any quoted client | None exist. |
| Attorney claims | years of experience, number of cases, "former insurance lawyer", any bio detail | None supplied. |
| Internal matters | "Iozera", "Kevin", "Azure", "Azra", "VN Group", ownership percentages, "AI-driven law firm" as a business description | Internal. Whether the site says "AI" at all is Tim's open question 4. |
| Placeholders | "[CONFIRM", "[FIRM NAME]", "[DOMAIN]", "[PHONE]", "[ATTORNEY", "lorem", "TODO", "example.com", "555-" | Unfinished content. |

## Allowed exceptions

- "$0 upfront" may appear only after Tim confirms the engagement agreement provides it.
- "guarantee" may appear only in the negative, in the calculator note and footer disclaimer.
- "AI" may appear only if Tim answers question 4 in `PI-Website-Content-Draft.md` with yes.

## Known risks to look at first

- The fee calculator is client-side JavaScript. Its default state must be server-rendered.
- The design is cloned from mystack.com, which uses scroll animations. Check every reveal for hidden-by-default content and reduced-motion handling.
- The FAQ accordion must keep every answer in the DOM when closed.
