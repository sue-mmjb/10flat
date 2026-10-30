# Tim's instructions for the personal injury website, verbatim

Source: WhatsApp group chat, 30 October 2026. Times are as shown in the chat export; the screenshot Sue saved on 30 October shows the same messages from 04:07 to 04:11. Spelling is Tim's own. Nothing here is paraphrased.

This file is the primary source of truth. Where any other document in this project disagrees with it, this file wins.

## The brief

| Time | From | Message |
|---|---|---|
| 12:43 AM | Tim | I need 2 websites |
| 12:44 AM | Tim | One for lawfirm dealing in mergers and aquisitioms |
| 12:44 AM | Tim | And a different one dealing in personal injury |
| 12:45 AM | Tim | For personal injury its $500 dollars down and 25% contingency for car accidents |
| 12:45 AM | Tim | 33% for dental and medical malpractice |
| 12:45 AM | Tim | Then ask ai for list of possible personal injury and show those prices and ask it to make up their own contingency |
| 12:46 AM | Chandana | Okay |
| 12:46 AM | Tim | Maybe find some reference sites first |

## The design reference and the calculator

| Time | From | Message |
|---|---|---|
| 04:07 | Tim | for personal injury |
| 04:07 | Tim | https://mystack.com/ |
| 04:08 | Tim | We're putting an end to high legal fees. |
| 04:08 | Tim | We win when you win. Simple as that. |
| 04:09 | Tim | then show sliding scale of award amount and what the client will net |
| 04:09 | Tim | do you see the slider? |
| 04:09 | Chandana | yes |
| 04:09 | Chandana | *(screenshot of the mystack "You set the budget" card: Total Monthly Budget $3,744, benchmark plan Bronze / Silver / Gold, employer contribution 80%)* This one? |
| 04:10 | Tim | yeah..we make that a fee caculator |
| 04:10 | Tim | what you owe us today $0 |
| 04:10 | Tim | what you get when we win your case |
| 04:10 | Tim | and let them slide and show percenttage based on industry |
| 04:10 | Tim | that is a new way to promote lawfirm that i never saw before |
| 04:11 | Tim | basically price visibility for law stuff |
| 04:11 | Tim | ok can we try that |
| 04:11 | Chandana | Yes, I'll clone these |
| 04:11 | Tim | ok |
| 04:12 | Tim | up to you chandana |
| 04:12 | Tim | if you think its faster to do yourself go ahead |
| 04:12 | Tim | we need the vn agreement done first |

## From the Zoom meeting the same night (AI-generated summary Ihna posted at 02:50)

Not Tim's words, so second-hand, but it is the only record of what he said on the call:

- Firm A: personal injury, handling broad categories such as motor vehicle accidents, premises liability, slip and fall, workplace accidents.
- Use AI to automate client intake, questionnaires, document preparation, case management; undercut market pricing.
- Branding: two branded, non-personal-name law firm names with a corporate, global feel. Chandana to ask AI for naming options.
- Lawyer oversight (Azure) for legal judgment, exceptions and final approvals.
- Non-attorney involvement must be structured to comply with ownership restrictions; the team must confirm regulatory limits on AI-led interviews and client-facing advice.

## Where each instruction landed on the site

| Instruction | Where |
|---|---|
| "$500 dollars down and 25% contingency for car accidents" | Pricing table and calculator. The $500 is shown as a [CONFIRM] chip because of the next line. |
| "what you owe us today $0" | Calculator row 1. Conflicts with "$500 down"; both shown, Tim to decide. |
| "33% for dental and medical malpractice" | Pricing table and calculator case types. |
| "ask ai for list of possible personal injury ... make up their own contingency" | Proposed list in `PI-Website-Content-Draft.md` section 4.2, not on the site until approved. |
| mystack.com as reference | The site is built from the mystack clone; same fonts, colours, nav, hero and footer. |
| "We're putting an end to high legal fees." | Hero headline, verbatim. |
| "We win when you win. Simple as that." | Hero subhead, verbatim, and the "We win when you win" section. |
| "sliding scale of award amount and what the client will net" | Calculator slider and "What you get when we win your case". |
| "make that a fee caculator" | The mystack "step 1" card became the calculator. |
| "show percenttage based on industry" | Comparison row in the calculator. Percentage is a [CONFIRM] chip. |
| "price visibility for law stuff" | The whole concept: every fee is published, every CTA points at the calculator. |

## Not applied to this site

- 03:48 "use this text" with the morninglightlaw.com link. Read in context (after "use this for m and a" and the vandijkenglas.nl choice) as the M&A site only.
- 03:49 "photos for tiles ... abstract images of buildings we can find from istock". Said for the M&A site. No imagery was specified for personal injury.

## Update: Tim's answer on the down payment (WhatsApp, 30 October 2026)

| Time | From | Message |
|---|---|---|
| 08:28 | Tim | *(quoting Sue's question 1)* I was thinking to collect $500 so we dont get people to waste time but then i remembered we can have ai do the initial consult by whatsapp |
| 08:29 | Tim | so $0 down would be very disruptive |
| 08:29 | Tim | $0 down, $50 per hour or 25% contingency |
| 08:29 | Tim | 33% for medical/dental |
| 08:29 | Tim | this would be ground breaking |

Applied: $0 down everywhere, the $500 is gone, the hourly option is shown next to the contingency rate, and the WhatsApp intake is mentioned in step 1 and the Start section. Still open: whether the client chooses hourly or percentage, whether hourly applies to malpractice, and the WhatsApp number.

## Update: the 10flat model (Perplexity research chat Tim shared as "10flat app.pdf", 30 to 31 October 2026)

Tim shared a 107-page research chat that works out a new fee model called 10flat. The messages from the group chat quoted inside it:

| Time | From | Message |
|---|---|---|
| 23:50, 10/30 | Tim | I think this is better than azhul idea to make a lawfirm where I help him with cases. Whst do you think chandana |
| 23:50, 10/30 | Chandana | Yes this would be very disruptive |

Tim's own prompts inside the chat (his words):

- "10flat is always available. If client wants to upgrade to premium that's up to them. Its a bolt on. Help us structure the pricing and language so 10flat is legal and ethical but we also want to provide full service human brick and mortar services in every u.s. state if the client chooses and only if client chooses. No bait and switch"
- "We cant charge 10% of award, can we"
- "this is the picture of the app. suggest content for 10flat law and make edit document" (with screenshots of the clone's calculator and step-2 card)

The chat's final answer (pages 89 to 91) is the brief applied to the site on 31 October 2026:

- Replace the 25% / 33% pricing with a genuine 10% base attorney fee. Premium is an optional 25% total fee, not an extra 25% and not required.
- Calculator: "Your fee, made clear"; "After attorney fee, before costs and liens" instead of "What you get when we win"; "Illustrative recovery amount" instead of "Expected award"; rows for attorney fee, after fee, case costs (not yet estimated), liens (not yet estimated); the amount editable as well as slidable; "Continue to case review".
- Remove the $50/hour option unless it is a separately defined service. Remove percentages from the case-type tabs; choosing medical or dental must not change the fee.
- Show "$0 upfront" only if the agreement actually provides it. Until then: "See your signed payment and case-cost terms."
- Case dashboard: documents received, attorney fee 10% confirmed in the signed agreement, upfront payment per the agreement, your attorney (name, firm, state), current stage, next step, no decision needed. Premium offered below, never forced: "The 25% fee replaces the 10% fee. Upgrade only if you choose and sign."
- Disclaimer under the calculator: illustration only, not a valuation, offer or guarantee; costs and liens may reduce what you receive; representation begins only after attorney acceptance and a signed agreement.
- Brand language: 10flat is a legal technology company, not a law firm; an independent licensed attorney or law firm represents the client; 10flat takes no portion of the settlement or attorney fee. Never say "AI lawyer", "no fee unless we win", "guaranteed", "cheapest".
- No automatic fee increases for filing suit, trial or appeal: the chat says 10flat "stays available", so none were introduced.

Not yet from Tim in his own words: the firm name is still the placeholder; "10flat" is used as the platform brand because the whole document is written around it.

## Update: domain (31 October 2026)

Sue, in the build session: "wesbite name is http://10flatlaw.com/". Applied: canonical URL and all schema URLs now use https://10flatlaw.com/. The site stays noindex until launch.

## Update: firm name (31 October 2026)

Sue, in the build session: "the firm name is 10flatlaw". Corrected the same day: "it's 10flat, not 10flatlaw". Applied: wordmark, page title, footer, copyright, attorney line and schema all say 10flat. The domain stays 10flatlaw.com. The old [FIRM NAME] placeholder is gone and the build now fails if it or "10flatlaw" reappears in the page text.

## Update: client explainer (31 October 2026)

Sue shared `10flat-client-explainer.pdf` ("Less Paperwork. More Money to You. How 10Flat Law charges 10%, and why a lower fee doesn't mean a smaller settlement") with "read this file and apply to the app as client". It is the client-facing version of the 10flat model and supersedes the research chat where they differ. Applied to both site versions:

- Fee: 10% of the amount recovered, **calculated after case costs are repaid**. It never goes up, even at trial. (The research chat said 10% of the gross recovery; the explainer wins.)
- No fee and no costs if there is no recovery. No markup on case costs. No admin fees. "$0 upfront" wording is no longer withheld: the explainer promises it.
- No Premium / Attorney-Led tier. The explainer promises the fee "never goes up" and says nothing about a 25% option, so Premium is removed from both sites. Flagged for Tim in QUESTIONS-FOR-TIM.md.
- A licensed Texas attorney is responsible for the case; the client chooses their attorney from the team members available. [STATE] placeholders are now Texas.
- Calculator rebuilt around the explainer's table: settlement amount, case costs (example, editable; 5% to the nearest $500 reproduces the explainer's $1,000 / $2,000 / $5,000 rows), fee at a 33% firm, fee at 10flat, what you keep, and the headline "You keep this much more than at a 33% firm". Footnote: "Fees are figured after case costs at both firms. Medical bills and liens are paid from the settlement the same way at any firm. Example only; every case is different."
- Copy taken from the explainer's sections: where the money goes at a typical firm, what we do differently, lower percentage does not mean lower amount, better service not less, our promises. Intake is "Message us on WhatsApp"; "Se habla español" is shown.
- Footer uses the explainer's legal paragraph (10flat [PLLC], attorney responsible, fee after costs, no recovery no fee, software including AI with a supervised case team, no attorney-client relationship until a fee agreement is signed, Texas Board of Legal Specialization line, Texas Fee Index citation). Placeholders in square brackets are still Tim's to fill.
