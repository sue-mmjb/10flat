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
