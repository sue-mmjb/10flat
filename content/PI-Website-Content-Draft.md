# Personal Injury Law Firm Website: Content Draft

Prepared from the WhatsApp group chat of 30 October 2026 (Tim's messages and the Zoom meeting summary Ihna shared at 2:50 AM). Firm name is not yet decided, so `[FIRM NAME]` is used throughout.

**How to read this document.** Every statement is tagged with its source:

- **[TIM]** Tim's own words in the chat. Primary source of truth.
- **[MEETING]** The AI-generated Zoom summary Ihna posted. Reflects what Tim said on the call, but is second-hand and should be confirmed.
- **[REC]** My recommendation. Not confirmed by Tim.
- **[?]** Open question. Listed in Section 7.

---

## 1. Summary of Tim's intended website concept

Tim is launching two AI-driven law firms with Kevin and the lawyer (Azure). This document covers the personal injury firm only. **[MEETING]**

What Tim wants the personal injury website to be:

1. **A price-transparency site, not a traditional law firm site.** Tim's words: "basically price visibility for law stuff" and "a new way to promote lawfirm that i never saw before." **[TIM]**
2. **Modelled on mystack.com.** Tim chose this site as the design reference and Chandana is cloning it. It is a single-page, plain-spoken fintech landing page built around an interactive calculator. Tim did not choose any of the traditional law firm sites shared by Danish or Chandana. **[TIM]**
3. **Two hero lines, fixed by Tim:** "We're putting an end to high legal fees." and "We win when you win. Simple as that." **[TIM]**
4. **A fee calculator as the centrepiece.** A slider for the award amount that shows "what you owe us today $0," "what you get when we win your case," and the comparison "percentage based on industry." **[TIM]**
5. **Published pricing by case type.** Car accidents: $500 down and 25% contingency. Dental and medical malpractice: 33%. Tim asked AI to list other personal injury types, show prices, and propose their contingency rates. **[TIM]**
6. **Business model behind the pricing:** AI handles intake, questionnaires, document preparation and case management, with the lawyer providing judgment and final approval, so the firm can run high volume at low prices. **[MEETING]**
7. **Branding:** a non-personal-name brand with a corporate, global feel. Names are still being generated. **[MEETING]**

Case categories named for Firm A: motor vehicle accidents, premises liability, slip and fall, workplace accidents **[MEETING]**, plus dental and medical malpractice **[TIM]**.

---

## 2. Source map: exactly what Tim said

All times are 30 October 2026.

| Time | Tim's message | Used in |
|---|---|---|
| 12:43 AM | "I need 2 websites" | Scope |
| 12:44 AM | "And a different one dealing in personal injury" | Scope |
| 12:45 AM | "For personal injury its $500 dollars down and 25% contingency for car accidents" | Pricing |
| 12:45 AM | "33% for dental and medical malpractice" | Pricing |
| 12:45 AM | "Then ask ai for list of possible personal injury and show those prices and ask it to make up their own contingency" | Pricing table |
| 12:46 AM | "Maybe find some reference sites first" | Design |
| 4:07 AM | "for personal injury" / "https://mystack.com/" | Design reference |
| 4:08 AM | "We're putting an end to high legal fees." | Hero H1 |
| 4:08 AM | "We win when you win. Simple as that." | Hero subhead |
| 4:09 AM | "then show sliding scale of award amount and what the client will net" | Calculator |
| 4:10 AM | "yeah..we make that a fee caculator" | Calculator |
| 4:10 AM | "what you owe us today $0" | Calculator output 1 |
| 4:10 AM | "what you get when we win your case" | Calculator output 2 |
| 4:10 AM | "and let them slide and show percenttage based on industry" | Calculator comparison |
| 4:10 AM | "that is a new way to promote lawfirm that i never saw before" | Positioning |
| 4:11 AM | "basically price visibility for law stuff" | Positioning |

Not applied to this site: Tim's 3:48 AM instruction "use this text" with the morninglightlaw.com link. Read in context, it follows his M&A design choice (vandijkenglas.nl, "replace masters of glass"), so I have treated it as M&A only. **[?]** See Q10.

---

## 3. Proposed sitemap and page structure

mystack.com is essentially one long landing page with a small number of supporting links. Cloning it means the home page carries almost everything. **[REC]**

```
Home (single long page, mirrors the mystack.com section order)
 ├── Hero
 ├── Pricing explained ("Know your fee before you start")
 ├── Fee calculator (interactive, slider)
 ├── Case types and fees (table)
 ├── How it works (3 steps)
 ├── "We win when you win"
 ├── Why the price is lower (technology + lawyer oversight)
 ├── Closing call to action
 └── Footer (disclaimers, attorney responsible, privacy, terms)

Supporting pages
 ├── /start            Case intake (the AI questionnaire)
 ├── /pricing          Full case-type and fee table, fee FAQ
 ├── /about            Firm, the responsible attorney, how we work
 ├── /contact
 ├── /privacy  /terms  /disclaimer
```

Sections of mystack.com that have no equivalent yet and should be left out until real content exists: "Our trusted partners" logo row, the named testimonial, the five anonymous testimonials, and the carrier logo row. **[REC]** See Q9.

---

## 4. Draft content

### 4.1 Home page

#### Hero

**H1:** We're putting an end to high legal fees. **[TIM]**

**Subhead:** We win when you win. Simple as that. **[TIM]**

**Supporting line:** **[REC]**
Personal injury representation with the fee published up front. Move the slider, see what you'd keep.

**Primary button:** See what you'd keep **[REC]**
**Secondary button:** Start your case **[REC]**

---

#### Section: Know your fee before you start **[REC, built on TIM]**

Most people never find out what a lawyer will cost until the case is over. We think that's backwards.

At [FIRM NAME] the fee is a fixed percentage, published on this page, agreed before we lift a finger. No hourly billing. No surprise deductions at the end.

---

#### Section: Fee calculator **[TIM, layout REC]**

This replaces the "Set a budget" calculator on mystack.com. Tim's three required outputs are in bold.

**Heading:** What would you actually take home?

**Intro:** Slide to the amount you expect to recover. We'll show you our fee and what you keep, next to what a typical firm would charge.

Controls:

- **Case type** (dropdown): Car accident · Medical malpractice · Dental malpractice · [other types from the table in 4.2]
- **Expected settlement or award** (slider): range to be confirmed. Suggested $10,000 to $1,000,000, default $100,000. **[?]** Q6

Outputs:

| Label | Value | Source |
|---|---|---|
| **What you owe us today** | **$0** | **[TIM]** but conflicts with "$500 down". **[?]** Q1 |
| Our fee when we win | 25% (car accident) or 33% (malpractice) of the slider amount | **[TIM]** |
| **What you get when we win your case** | Slider amount minus our fee | **[TIM]** |
| What you'd keep with a typical firm | Slider amount minus [industry %] | **[TIM]** asked for an industry comparison. Figure to be verified. **[?]** Q7 |
| Difference | Highlighted | **[REC]** |

Worked example (car accident, $100,000 recovery, 25%):

- What you owe us today: $0
- Our fee when we win: $25,000
- What you get when we win: $75,000
- With a typical [industry %] fee you'd keep: [$ amount]

**Required note under the calculator:** **[REC, compliance]**
The figures shown are illustrative only. They are not a prediction, promise or guarantee of any outcome or amount. Every case is different. [Statement on whether case costs such as filing fees and expert fees are deducted separately. **[?]** Q2]

---

#### Section: Case types and fees (home page summary) **[TIM]**

**Heading:** One published rate for every kind of case.

Short version of the full table in 4.2. On the home page show only the confirmed rows:

| Case type | Today | When we win |
|---|---|---|
| Car accidents | $500 **[TIM]** | 25% **[TIM]** |
| Medical malpractice | [$500 or $0] **[?]** | 33% **[TIM]** |
| Dental malpractice | [$500 or $0] **[?]** | 33% **[TIM]** |

Link: See all case types and fees → /pricing

---

#### Section: How it works **[MEETING, copy REC]**

This replaces mystack.com's "You set the budget / Your team shops / The plan goes with them" trio.

**Heading:** Three steps. No waiting room.

**1. Tell us what happened.**
Answer a short set of questions online, at your own pace. Upload what you have: photos, police report, medical bills. If something is missing, we'll ask.

**2. We build your case.**
Our system organises your facts and documents and prepares the paperwork. Our attorney reviews every case and makes every legal decision. **[?]** Q4 on how much to say about AI.

**3. We pursue your recovery.**
You see the fee before we start. You see what you keep when we win.

---

#### Section: We win when you win **[TIM line, copy REC]**

**Heading:** We win when you win.

Our fee is a percentage of your recovery. That means we only do well when you do. No conflicts. No asterisks. **[REC: the last two phrases mirror mystack.com's tone. Replace if Tim wants original wording.]**

[If we don't recover anything for you, you don't owe us a contingency fee. **[?]** Q1: only publish if true given the $500 down payment.]

---

#### Section: Why our fee is lower **[MEETING, copy REC]**

**Heading:** Lower fees aren't a gimmick. They're a design.

Traditional firms charge high percentages because they run on paperwork and hours. We built [FIRM NAME] around technology that handles the intake, the document assembly and the case tracking, so our attorney spends time on your case, not on admin. That's the saving we pass on. **[?]** Q4

---

#### Closing call to action **[REC, mirrors mystack.com closing]**

**Heading:** You've been through enough. Let us handle the legal part.

**Button:** Start your case
**Secondary link:** See what you'd keep

---

#### Footer **[REC, compliance]**

- [FIRM NAME] · Attorney responsible for this content: [Attorney name, bar number, jurisdiction] **[?]** Q3, Q5
- Attorney advertising. Prior results do not guarantee a similar outcome.
- Fee percentages and the calculator are illustrative and subject to a written fee agreement.
- Privacy Policy · Terms of Use · Disclaimer
- © 2026 [FIRM NAME]

---

### 4.2 /pricing page: full case types and fees

**Heading:** Every case type. Every fee. Published.

**Intro:** We don't negotiate fees case by case behind closed doors. Here is what we charge, for everything we handle.

Tim asked AI to list other personal injury types and propose their contingency rates. Rows marked **Confirmed** come from Tim. Rows marked **Proposed** are my suggestions and need Tim's and Azure's sign-off before publication. Case types marked † were named in the meeting summary as categories Firm A will handle.

| Case type | Pay today | Fee when we win | Status |
|---|---|---|---|
| Car accidents † | $500 | 25% | **Confirmed [TIM]** |
| Medical malpractice | [?] | 33% | **Confirmed fee [TIM]**, down payment unclear |
| Dental malpractice | [?] | 33% | **Confirmed fee [TIM]**, down payment unclear |
| Truck, motorcycle, rideshare, pedestrian and bicycle accidents | [?] | 25% | Proposed: same tier as car accidents |
| Slip and fall / premises liability † | [?] | 25% | Proposed |
| Dog bites and animal attacks | [?] | 25% | Proposed |
| Workplace accidents † | [?] | 25% | Proposed, but see Q8 (workers' compensation fee caps) |
| Product liability | [?] | 33% | Proposed |
| Nursing home abuse and neglect | [?] | 33% | Proposed |
| Wrongful death | [?] | 33% | Proposed |

**Proposed logic for the two tiers [REC]:** 25% for cases that are usually resolved through an insurance claim and rarely need expert witnesses. 33% for cases that normally require expert testimony and litigation (malpractice, product liability, wrongful death, institutional abuse). This keeps Tim's two existing rates and avoids a third tier the calculator would have to explain.

**Fee FAQ [REC, answers need confirmation]**

- **What does "pay today" cover?** [To be defined. **[?]** Q1]
- **Are case costs separate from the fee?** [To be defined. **[?]** Q2]
- **Does the percentage change if the case goes to trial?** [To be defined. **[?]** Q2]
- **How do I know what I'd keep?** Use the calculator. The percentage never changes from what is published here.

---

### 4.3 /start page: case intake **[MEETING]**

**Heading:** Start your case. It takes about ten minutes.

**Intro:** Answer a few questions about what happened. You can stop and come back. Nothing here commits you to anything.

Intake flow (the AI questionnaire described in the meeting):

1. What type of injury or incident
2. When and where it happened
3. Who was involved
4. Injuries and treatment so far
5. Documents you already have (upload)
6. Contact details

**Button:** Submit my case

**Note under the form [REC, compliance]:** Submitting this form does not create an attorney-client relationship. We will review your answers and contact you. [Statement on how and when the attorney reviews the submission. **[?]** Q4]

---

### 4.4 /about page

**Heading:** A law firm built for the way people actually get hurt.

**Body [REC]:** People don't plan for a car accident or a surgery that goes wrong. When it happens, they shouldn't need to guess what a lawyer will cost or wait weeks for an answer. [FIRM NAME] was built to make personal injury representation faster to start and clear on price.

**The attorney [PLACEHOLDER]:** Name, jurisdiction, bar admission, photo. **[?]** Q3. No biography or credentials should be written until Azure provides them.

**Our approach [MEETING]:** Technology handles the routine. Our attorney handles the law. Every legal decision on your case is made by a licensed lawyer.

---

### 4.5 /contact page

**Heading:** Talk to us.

Phone, email, hours, office address or "serving [jurisdiction]". All **[PLACEHOLDER]**. **[?]** Q5

---

## 5. Recommended calls to action

All **[REC]**, derived from Tim's stated objective of price visibility and the mystack.com pattern of one repeated primary action.

| Placement | Label | Why |
|---|---|---|
| Hero, primary | **See what you'd keep** | Pushes the visitor straight to the calculator, which is the site's main idea. Equivalent of mystack's "Instant quote". |
| Hero, secondary | **Start your case** | Leads to the AI intake, which is the conversion the business model depends on. |
| Under calculator | **Start your case** | The moment the visitor has seen the number is the moment to ask. |
| Pricing table | **Start your case** | Same. |
| Closing section | **Start your case** | Repeats the primary action, as mystack repeats "Instant Quote". |
| Sticky header | **Start your case** | Always available. |

Avoid "Free consultation" until Tim confirms it. It is implied by "$0 today" but not stated, and it conflicts with "$500 down".

---

## 6. Design notes carried over from Tim's instructions

- Clone mystack.com's layout and section order. Tim: "ok can we try that". Chandana: "I'll clone these". **[TIM]**
- Tone follows the reference: plain, confident, short sentences. The two hero lines set the register. **[TIM]**
- Tile images for the M&A site will be abstract building photos from iStock. Tim did not specify imagery for the personal injury site. **[?]** Q11

---

## 7. Unresolved questions for Tim

1. **$500 down versus "$0 today".** Tim said car accidents are "$500 dollars down" and, later, that the calculator should show "what you owe us today $0". Which is correct? Is the $500 waived, refundable, deducted from the fee, or only for some case types? The hero promise and the whole fee section depend on this.
2. **Case costs.** Are filing fees, expert witness fees and medical record costs paid by the client, advanced by the firm and deducted from the recovery, or included in the percentage? The calculator cannot be honest without this.
3. **The responsible attorney.** Most bar rules require a named, licensed attorney responsible for the firm's advertising. Is Azure the attorney of record, and is Azure licensed in the jurisdiction where the firm will practise? Can we have name, bar number and a short bio?
4. **How visibly should the site mention AI?** The business model is AI-driven, but the meeting summary flags that the team must first confirm regulatory limits on AI-led intake and client-facing advice. Should the public site say "AI", say "technology", or say nothing about how the work is done?
5. **Jurisdiction.** Which state or country will the firm practise in? Advertising rules, required disclaimers and the lawfulness of the fee structure all depend on it.
6. **Calculator range.** What minimum, maximum and default should the award slider use?
7. **Industry comparison figure.** Tim wants the calculator to show the "percentage based on industry". What figure should we use, and can Azure supply a citable source? I have not put a number in the draft.
8. **Workplace accidents.** In many jurisdictions these fall under workers' compensation, where attorney fees are capped by statute. Should workplace accidents stay in the fee table, and at what rate?
9. **Testimonials and partner logos.** mystack.com relies on them. The firm has none yet. Leave those sections out, or does Tim want placeholders?
10. **Morning Light Law text.** Tim's "use this text" for morninglightlaw.com came right after the M&A design choice. I have treated it as M&A only. Correct?
11. **Imagery for the personal injury site.** Abstract buildings were specified for M&A. What should this site use?
12. **Proposed case types and rates.** Does Tim approve the proposed rows and the 25% / 33% tiering in the pricing table, or want changes before Azure reviews it?
13. **Firm name.** Needed before any copy is final. Chandana is producing 3 to 5 options.

---

## 8. Alignment checklist

| Tim's instruction | Where it is followed |
|---|---|
| A separate website for personal injury | This document is scoped to the personal injury site only |
| "$500 dollars down and 25% contingency for car accidents" | Pricing table, calculator, home page summary. Flagged the $0 conflict rather than resolving it myself |
| "33% for dental and medical malpractice" | Pricing table, calculator case-type options |
| "ask ai for list of possible personal injury and show those prices and ask it to make up their own contingency" | Section 4.2: proposed case types with proposed rates, each marked Proposed and routed to Q12 |
| "Maybe find some reference sites first" / mystack.com chosen | Sitemap and section order mirror mystack.com; sections with no real content yet are omitted |
| "We're putting an end to high legal fees." | Hero H1, verbatim |
| "We win when you win. Simple as that." | Hero subhead, verbatim; reprised as a section heading |
| "show sliding scale of award amount and what the client will net" | Calculator slider and "What you get when we win your case" output |
| "what you owe us today $0" | Calculator output, verbatim label, with the $500 conflict flagged |
| "what you get when we win your case" | Calculator output, verbatim label |
| "show percentage based on industry" | Calculator comparison row; figure left blank pending Q7 |
| "price visibility for law stuff" | Site concept, pricing page, every CTA points at the calculator or the published fees |
| Non-personal-name brand with corporate, global feel (meeting) | `[FIRM NAME]` placeholder; no founder or lawyer name used in branding |
| AI intake, document prep, lawyer oversight (meeting) | How it works, /start intake, /about approach; prominence of "AI" left to Q4 |
| Compliance concerns on AI and non-attorney involvement (meeting) | Disclaimers in footer, calculator and intake; attorney placeholder; Q3, Q4, Q5 |

---

## 9. Cross-check: statements I could not support from the conversation

These appear in the draft only as recommendations or placeholders, never as facts:

- Any "free consultation" or "no fee unless we win" promise. Implied by "$0 today" but contradicted by "$500 down". Bracketed, not published.
- Any industry contingency percentage. Tim asked for the comparison but gave no number. Left blank.
- All case types other than car accidents, medical malpractice, dental malpractice, motor vehicle accidents, premises liability, slip and fall and workplace accidents. Marked Proposed.
- All contingency rates other than 25% (car) and 33% (medical and dental malpractice). Marked Proposed.
- Treatment of case costs. Not discussed. Left as a question.
- Attorney name, credentials, bar admissions, years of experience, results, case counts, testimonials, partner logos. None exist in the conversation. Placeholders only.
- Jurisdiction and office details. Not discussed. Placeholders only.
- The $5,000 flat fee and $50 per hour figures from the meeting summary. These were described there as "sample pricing suggested" for the business model, not as website pricing, and Tim's later chat messages gave different, specific numbers. Not used.
- Ownership structure, Kevin, Azure's equity, VN Group, investor relationships. Internal matters, deliberately excluded from all copy.
