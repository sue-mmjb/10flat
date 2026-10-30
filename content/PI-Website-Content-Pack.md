# [FIRM NAME] Personal Injury Website: Audit-Ready Content Pack

Companion to `PI-Website-Content-Draft.md` (the strategy, source map and questions for Tim). This file is what the developer builds from. It is written so the site can pass the `website-presubmission-audit` skill without rework:

- Every page has one h1, a heading outline with no skipped levels, a title tag, a meta description, a canonical URL and alt text for every image.
- Every page's JSON-LD is in `schema/` as a file the audit script can validate. The FAQ text in the schema is identical to the visible FAQ text in this file, character for character.
- Nothing in the copy claims what Tim has not confirmed. Where a fact is still open, the copy carries a `[CONFIRM: ...]` placeholder. The audit directives in `PI-AUDIT_DIRECTIVES.md` treat any surviving `[CONFIRM` as a P0, so the site cannot ship with one by accident.
- Language: English only. Tim did not ask for a second language on this site.

Design reference is mystack.com, as Tim chose. Section order on the home page follows it.

---

## Global elements

**Site name:** [FIRM NAME]
**Domain:** `https://10flatlaw.com/` (all canonical URLs below use this)
**Default `<html lang>`:** `en`
**Primary CTA, repeated in header and at the end of every page:** Start your case → `/start`
**Secondary CTA:** See what you'd keep → `/#calculator`

**Header nav (in this order):** Pricing · How it works · About · Contact · [button] Start your case
**Footer, every page:**

- [FIRM NAME] · [Street address, City, State ZIP] · Text or call [PHONE]
- Attorney responsible for this website: [ATTORNEY NAME], [BAR NUMBER], licensed in [STATE]
- Attorney advertising. Prior results do not guarantee a similar outcome. Fee percentages are subject to a written fee agreement. The calculator is illustrative only.
- Privacy · Terms · Disclaimer · © 2026 [FIRM NAME]

Build note: the footer must be in server-rendered HTML on every page. The audit checks that the address and phone in the footer match the JSON-LD on every page.

---

## Page 1: Home

| Field | Value |
|---|---|
| URL | `/` |
| Canonical | `https://10flatlaw.com/` |
| Title (≤60 chars) | Personal Injury Lawyers With Published Fees \| [FIRM NAME] |
| Meta description (≤155 chars) | See our fee before you hire us. 25% for car accidents, 33% for medical and dental malpractice. Slide to see what you'd keep when we win. |
| h1 | We're putting an end to high legal fees. |
| LCP element | Hero h1 (text). No hero image, so nothing to preload. |
| Schema | `schema/home.html` (LegalService + FAQPage + WebSite) |

### Hero

**h1:** We're putting an end to high legal fees.
**Subhead (p):** We win when you win. Simple as that.
**Supporting line (p):** Personal injury representation with the fee published up front. Move the slider, see what you'd keep.
**Buttons:** [primary] See what you'd keep → `#calculator` · [secondary] Start your case → `/start`

Build note: no `opacity: 0` on hero text before JS runs. If the hero animates in, animate from visible with a reduced-motion fallback.

### h2: Know your fee before you start

Most people never find out what a lawyer will cost until the case is over. We think that's backwards.

At [FIRM NAME] the fee is a fixed percentage, published on this page, agreed in writing before we lift a finger. No hourly billing. No surprise deductions at the end.

### h2: What would you actually take home? (`id="calculator"`)

**Intro (p):** Slide to the amount you expect to recover. We'll show you our fee and what you keep, next to what a typical firm would charge.

**Controls**

- Label: Case type. Select: Car accident (25%) · Medical malpractice (33%) · Dental malpractice (33%). Add further types only when Tim approves the pricing table.
- Label: Expected settlement or award. Range slider, `[CONFIRM: minimum]` to `[CONFIRM: maximum]`, default `[CONFIRM: default]`, step $1,000. Must be a native `<input type="range">` with a visible numeric value and `aria-valuetext` in dollars.

**Outputs (each a labelled row, server-rendered with the default values so the numbers exist without JS)**

| Label | Formula |
|---|---|
| What you owe us today | $0 (confirmed by Tim, 30 Oct 08:29) |
| Our fee when we win | amount × rate |
| What you get when we win your case | amount − (amount × rate) |
| What you'd keep with a typical firm's fee | amount − (amount × `[CONFIRM: industry %]`) |
| Difference | row 3 − row 4, highlighted |

**Note (p, directly under the outputs, always visible):** These figures are illustrative only. They are not a prediction, promise or guarantee of any outcome or amount. Every case is different. `[CONFIRM: sentence on whether case costs such as filing fees and expert fees are deducted separately]`

Build note: the calculator is the one piece of client-side JavaScript on the page. Render the default state on the server so the labels and default numbers are in the HTML. The audit treats a calculator that is empty without JS as hidden content.

### h2: One published rate for every kind of case

| Case type | Today | When we win |
|---|---|---|
| Car accidents | $0 | 25%, or $50 per hour `[CONFIRM: client chooses?]` |
| Medical malpractice | $0 | 33% `[CONFIRM: hourly option?]` |
| Dental malpractice | $0 | 33% `[CONFIRM: hourly option?]` |

**Link:** See all case types and fees → `/pricing`

### h2: Three steps. No waiting room.

**h3: 1. Tell us what happened.**
Answer a short set of questions online, at your own pace. Upload what you have: photos, police report, medical bills. If something is missing, we'll ask.

**h3: 2. We build your case.**
Our system organises your facts and documents and prepares the paperwork. Our attorney reviews every case and makes every legal decision.

**h3: 3. We pursue your recovery.**
You see the fee before we start. You see what you keep when we win.

### h2: We win when you win.

Our fee is a percentage of your recovery. That means we only do well when you do. `[CONFIRM: If we don't recover anything for you, you don't owe us a contingency fee.]`

### h2: Lower fees aren't a gimmick. They're a design.

Traditional firms charge high percentages because they run on paperwork and hours. We built [FIRM NAME] around technology that handles the intake, the document assembly and the case tracking, so our attorney spends time on your case, not on admin. That's the saving we pass on. `[CONFIRM: whether to say "AI" instead of "technology"]`

### h2: Questions people ask before they start

Visible FAQ. Accordion is fine, but every answer must be in the HTML whether open or closed. This text is reproduced exactly in `schema/home.html`.

**Q:** What is your fee for a car accident case?
**A:** Our fee is 25% of what we recover for you. The percentage is published on this site and agreed in writing before we start.

**Q:** What is your fee for a medical or dental malpractice case?
**A:** Our fee is 33% of what we recover for you. The percentage is published on this site and agreed in writing before we start.

**Q:** What does it cost to start my case?
**A:** Nothing. There is no down payment. Our fee is either $50 per hour or a percentage of what we recover, agreed in writing before we start. [CONFIRM: whether the client chooses between hourly and percentage]

**Q:** What happens if you don't win?
**A:** [CONFIRM: whether any amount is owed if there is no recovery]

**Q:** How does the fee calculator work?
**A:** Choose your case type and slide to the amount you expect to recover. The calculator shows our fee at the published percentage and what you would keep. The figures are illustrative only and are not a prediction or guarantee of any outcome.

**Q:** How do I start?
**A:** Answer a short set of questions online and upload any documents you have. Our attorney reviews your answers and contacts you. Submitting the questionnaire does not create an attorney-client relationship.

### Closing (h2)

**h2:** You've been through enough. Let us handle the legal part.
**Button:** Start your case → `/start`

---

## Page 2: Pricing

| Field | Value |
|---|---|
| URL | `/pricing` |
| Canonical | `https://10flatlaw.com/pricing` |
| Title | Personal Injury Fees, Published \| [FIRM NAME] |
| Meta description | Every case type we handle and the fee we charge, published in full. No hourly billing, no negotiation behind closed doors. |
| h1 | Every case type. Every fee. Published. |
| LCP element | h1 |
| Schema | `schema/pricing.html` (LegalService + FAQPage) |

**Intro (p):** We don't negotiate fees case by case behind closed doors. Here is what we charge, for everything we handle.

### h2: Confirmed rates

| Case type | Pay today | Fee when we win |
|---|---|---|
| Car accidents | `[CONFIRM: $500 or $0]` | 25% |
| Medical malpractice | `[CONFIRM]` | 33% |
| Dental malpractice | `[CONFIRM]` | 33% |

### h2: Other case types

Do not publish this section until Tim approves the proposed rows in `PI-Website-Content-Draft.md` section 4.2. When approved, add them to the table above and to the calculator's case-type select, and delete this heading.

### h2: How the fee works

**Q:** Is the percentage the same whether the case settles or goes to trial?
**A:** [CONFIRM: whether the rate changes if the case goes to trial]

**Q:** Are case costs included in the fee?
**A:** [CONFIRM: how filing fees, expert fees and record costs are handled]

**Q:** Can the fee change after we sign?
**A:** No. The percentage in your written fee agreement is the percentage you pay. It does not go up during the case.

### Closing

**h2:** See what you'd keep.
**Button:** Open the calculator → `/#calculator` · Start your case → `/start`

---

## Page 3: Start your case

| Field | Value |
|---|---|
| URL | `/start` |
| Canonical | `https://10flatlaw.com/start` |
| Title | Start Your Case Online \| [FIRM NAME] |
| Meta description | Tell us what happened in about ten minutes. Upload what you have. Our attorney reviews every submission. |
| h1 | Start your case. It takes about ten minutes. |
| Schema | `schema/start.html` (LegalService only; no FAQ on this page) |

**Intro (p):** Answer a few questions about what happened. You can stop and come back. Nothing here commits you to anything.

### h2: What we'll ask

1. What type of injury or incident
2. When and where it happened
3. Who was involved
4. Your injuries and treatment so far
5. Documents you already have (photos, police report, medical bills)
6. How to reach you

**Button:** Begin → (form)

**Note (p, under the form, always visible):** Submitting this questionnaire does not create an attorney-client relationship. Our attorney reviews your answers and will contact you. `[CONFIRM: response time, and whether the first contact is by text, call or email]`

Build note: the form must be a real `<form>` with labelled inputs and a submit `<button>`. Each step's heading is an h2. No step may be hidden with `display: none` from the server; use progressive disclosure that keeps every step in the DOM.

---

## Page 4: About

| Field | Value |
|---|---|
| URL | `/about` |
| Canonical | `https://10flatlaw.com/about` |
| Title | About [FIRM NAME] \| Personal Injury With Published Fees |
| Meta description | A personal injury firm built to be fast to start and clear on price. Every legal decision is made by a licensed attorney. |
| h1 | A law firm built for the way people actually get hurt. |
| Schema | `schema/about.html` (LegalService) |

**Body (p):** People don't plan for a car accident or a surgery that goes wrong. When it happens, they shouldn't need to guess what a lawyer will cost or wait weeks for an answer. [FIRM NAME] was built to make personal injury representation faster to start and clear on price.

### h2: Our attorney

`[CONFIRM: attorney name, jurisdiction, bar admission, two-sentence bio supplied by the attorney]`
**Image:** `[ATTORNEY PHOTO]`, alt: "[ATTORNEY NAME], attorney at [FIRM NAME]"

Do not write a biography, years of experience or results. None has been supplied.

### h2: How we work

Technology handles the routine. Our attorney handles the law. Every legal decision on your case is made by a licensed lawyer.

---

## Page 5: Contact

| Field | Value |
|---|---|
| URL | `/contact` |
| Canonical | `https://10flatlaw.com/contact` |
| Title | Contact [FIRM NAME] |
| Meta description | Text or call us, or start your case online. [CITY, STATE]. |
| h1 | Talk to us. |
| Schema | `schema/contact.html` (LegalService) |

**Phone:** `[PHONE]` as a `tel:` link
**Email:** `[EMAIL]` as a `mailto:` link
**Address:** `[Street address, City, State ZIP]` (must match footer and schema exactly)
**Hours:** `[CONFIRM: hours]`
**Button:** Start your case → `/start`

---

## Legal pages (stubs, required before launch)

`/privacy`, `/terms`, `/disclaimer`. Title and h1 as named. Body to be supplied by the attorney. Each gets `LegalService` schema only. Mark `noindex` until the attorney has supplied text.

---

## Site-wide technical requirements (what the audit checks)

- `robots.txt` allowing all, pointing at `sitemap.xml`. Sitemap lists `/`, `/pricing`, `/start`, `/about`, `/contact` and the three legal pages once indexable.
- Every page: exactly one h1, headings in order, unique title and meta description, canonical on `https://10flatlaw.com`, `<html lang="en">`.
- Fonts via `next/font`. Images via `next/image`, each with alt text as specified. No image over 300 KB.
- Any scroll-reveal: visible by default, animates only inside a `prefers-reduced-motion: no-preference` check, cleaned up on unmount.
- Footer address and phone identical on every page and identical to the JSON-LD.
- The calculator's default state rendered on the server.
