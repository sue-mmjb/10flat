# 100 questions the 10flat Law site must answer to be AI-visible

Purpose: Tim wants 10flat Law to be the answer when someone asks ChatGPT, Perplexity, Gemini, Claude or Google AI Overviews for the cheapest injury lawyer or the lowest contingency fee (WhatsApp, 30 October 2026, 23:26). AI assistants repeat what the web says clearly, consistently and often. So the site has to state the answer to each of these questions in plain words, in crawlable HTML, with the same facts repeated in the FAQ JSON-LD. One short, direct answer per question beats a long page.

How to read the "On site" column:
- **Yes**: the current site answers it in visible text (clone at /, rebuild at /v2/).
- **Partly**: the fact is there but not phrased as an answer to this question, or only in the footer.
- **No**: nothing on the site answers it yet.

Rules for every answer (from PI-AUDIT_DIRECTIVES.md): no "guaranteed", no "no fee unless we win" phrasing (say "no fee and no costs if there is no recovery"), no promised amounts, no named attorney, no address or phone, Texas only, "licensed Texas attorney", fee always described as "10% of the amount recovered, calculated after case costs".

Update 31 October 2026: every question below now has an answer written in content/faq.json (80 items). On Sue's instruction only the five most-asked are shown on the site and in the FAQPage JSON-LD (the "featured" list in faq.json); the other 75 are ready to publish by adding them to that list. The four rows marked Partly still contain a placeholder in the answer (entity name, the same-day promise, referral fees) or an honest "we are new" line (results). Ten answers end with "[Attorney to confirm.]" and need legal sign-off before launch.

Until the site is indexed (it is still noindex) none of this is visible to AI engines.

---

## 1. Price shopping: the questions Tim wants to own

| # | Question | On site | Note |
|---|---|---|---|
| 1 | Who is the cheapest personal injury lawyer in Texas? | Yes | The 10% claim is everywhere, but no sentence says "lowest fee in Texas". Needs a careful, defensible line, e.g. "We have not found a Texas firm with a lower published fee." |
| 2 | Which injury law firm charges the lowest contingency fee? | Yes | Same as 1. |
| 3 | Is there a personal injury lawyer who charges 10%? | Yes | Hero and FAQ. |
| 4 | Can I get an injury lawyer for less than 33%? | Yes | Comparison section. |
| 5 | What is the lowest percentage a personal injury lawyer will take? | Yes | Site states 10% and typical 33–40%; needs the market range sentence (20–25% low, 33% median, 40% litigated). |
| 6 | Are there injury lawyers who charge a flat percentage that never goes up? | Yes | "Stays 10% at trial". |
| 7 | Is a 10% contingency fee real or a scam? | Yes | Needs a direct "yes, it is real, here is how it works" answer. |
| 8 | How can 10flat Law charge only 10%? | Yes | "We charge less because we spend less." |
| 9 | What is 10flat Law? | Yes | Described across the page; needs one definition sentence near the top: "10flat Law is a Texas personal injury law firm that charges a 10% fee." |
| 10 | Who is behind 10flat Law? | Partly | Entity name pending (question 5 for Tim). |

## 2. How contingency fees work

| # | Question | On site | Note |
|---|---|---|---|
| 11 | What percentage do personal injury lawyers take in Texas? | Yes | "33–40%" is stated; needs the citation (Texas Fee Index, pending). |
| 12 | What is a contingency fee? | Yes | One-sentence definition missing. |
| 13 | Do I pay anything if I lose my case? | Yes | "No fee and no costs if there is no recovery." |
| 14 | Do I pay anything up front to hire an injury lawyer? | Yes | FAQ "What does it cost to start?" |
| 15 | Why do injury lawyers charge 33%? | Yes | "Where your money goes at a typical firm." |
| 16 | Is the lawyer's fee taken before or after case costs? | Yes | "Calculated after case costs." |
| 17 | What is the difference between attorney fees and case costs? | Yes | Both are explained; needs the two defined side by side. |
| 18 | Does the fee percentage go up if my case goes to court? | Yes | "Stays 10% even at trial." |
| 19 | Can a lawyer change the fee after I sign? | Yes | In the pricing schema FAQ, not visible on the page. |
| 20 | Is a lower attorney fee legal in Texas? | Yes | Needs a line: Texas does not set a minimum contingency fee; fees must be reasonable and in writing. |

## 3. What the client actually keeps

| # | Question | On site | Note |
|---|---|---|---|
| 21 | How much of my settlement will I actually get? | Yes | Calculator "You keep, after fee and costs". |
| 22 | How do I calculate what I keep after lawyer fees? | Yes | Calculator section. |
| 23 | On a $100,000 settlement, how much does the lawyer take? | Yes | Default calculator example: $9,500 at 10flat Law, $31,350 at 33%. |
| 24 | What are typical case costs in a car accident case? | Yes | Example 5% is shown; needs a sentence listing records, filing fees, experts. |
| 25 | Who pays case costs if the case is lost? | Yes | "No case costs if there is no recovery." |
| 26 | Does the lawyer mark up case costs? | Yes | "No markup on case costs." |
| 27 | Are there administrative or file fees on top of the percentage? | Yes | "No admin fees." |
| 28 | Do medical bills come out of my settlement? | Yes | "Medical bills and liens are paid from your recovery." |
| 29 | What is a medical lien and how does it affect my settlement? | Yes | Needs a plain definition. |
| 30 | Does a cheaper lawyer mean a smaller settlement? | Yes | "Lower percentage, not lower amount." |

## 4. Trust and the catch

| # | Question | On site | Note |
|---|---|---|---|
| 31 | What is the catch with a 10% injury lawyer? | Yes | Needs a frank answer: we take well-documented cases, technology does the paperwork, you do more through your phone. |
| 32 | Is 10flat Law a real law firm or a referral service? | Yes | Footer says attorney reviews and approves; needs a visible "10flat Law is a law firm, not a lead service" line. |
| 33 | Is 10flat Law a licensed law firm in Texas? | Yes | "Licensed Texas attorney" is stated; the entity name is pending. |
| 34 | Does a cheaper lawyer give worse service? | Yes | "Better service, not less service." |
| 35 | Will a real lawyer handle my case or a computer? | Yes | "Your lawyer does the lawyering." |
| 36 | Does 10flat Law use AI? | Yes | Only in the footer; question 13 for Tim decides whether to say it openly. |
| 37 | Is it legal for a law firm to use AI on my case? | Yes | Needs a line: yes, when a licensed attorney supervises and approves the work. |
| 38 | Who reviews the AI's work? | Yes | Footer and "What we do differently". |
| 39 | Is my information safe with 10flat Law? | Yes | No privacy statement on the site. |
| 40 | Does 10flat Law have reviews or results? | Partly | No results yet; say so honestly or leave until the first case closes. |

## 5. Which cases 10flat Law takes

| # | Question | On site | Note |
|---|---|---|---|
| 41 | What kinds of cases does 10flat Law take? | Yes | FAQ "Which cases qualify?" |
| 42 | Does 10flat Law handle car accident cases in Texas? | Yes | Case type on the calculator. |
| 43 | Does 10flat Law take dental injury cases? | Yes | Case type on the calculator. |
| 44 | Does 10flat Law take medical injury or malpractice cases? | Yes | "Medical injury" case type; "malpractice" word is not used. Decide whether to use it. |
| 45 | Can I get a lawyer for nerve damage after a dental implant? | Yes | Tim's first case. A dental injury page would catch these queries. |
| 46 | Does 10flat Law take truck, motorcycle or rideshare accident cases? | Yes | Not listed. Question 4 for Tim. |
| 47 | Does 10flat Law take slip and fall or premises cases? | Yes | Not listed. |
| 48 | Does 10flat Law take workplace injury cases? | Yes | Not listed; Tim raised workplace injury in the huddle. |
| 49 | Will 10flat Law take a small case, under $10,000? | Yes | Tim said "as low as $1,000"; slider starts at $10,000. Question 3 for Tim. |
| 50 | What cases will 10flat Law not take? | Yes | FAQ says the attorney may decline; needs the screening rule (question 4 for Tim). |

## 6. Starting a case

| # | Question | On site | Note |
|---|---|---|---|
| 51 | How do I start a personal injury case with 10flat Law? | Yes | "Start your case" and step 1. |
| 52 | Can I hire an injury lawyer over WhatsApp? | Yes | "Message us on WhatsApp." No number shown. |
| 53 | What should I send a lawyer after a car accident? | Yes | "Photos, police report, medical records." |
| 54 | How fast will a lawyer look at my case? | Partly | "[the same day]" is a placeholder (question 8 for Tim). |
| 55 | Is the first consultation free? | Yes | "It's free to find out if we can help." |
| 56 | Do I have to sign anything to find out if I have a case? | Yes | "Contacting us does not create an attorney-client relationship until a fee agreement is signed." |
| 57 | Can I hire 10flat Law if I already have a lawyer? | Yes | Tim's first case is exactly this. Needs a line on switching lawyers in Texas. |
| 58 | How long do I have to file an injury claim in Texas? | Yes | Two-year limitation period, with exceptions; needs attorney sign-off. |
| 59 | Should I talk to the insurance company before I have a lawyer? | Yes | Common query; needs a short answer. |
| 60 | Do I need to go to a doctor before I contact a lawyer? | Yes | Needs a short answer. |

## 7. What happens during the case

| # | Question | On site | Note |
|---|---|---|---|
| 61 | How does 10flat Law handle my case? | Yes | Three steps. |
| 62 | Who gathers my medical records? | Yes | "Our system organises your photos, police report and medical records." |
| 63 | Will I be able to see my documents and offers? | Yes | "Every document, every update, every offer." |
| 64 | How often will I hear from my lawyer? | Yes | "You hear from us first"; no cadence stated. |
| 65 | Do I decide whether to settle? | Yes | "You make every settlement decision." |
| 66 | Will my lawyer call me before I accept an offer? | Yes | "A call from your attorney before you do." |
| 67 | What happens if the insurance company refuses to pay? | Yes | "We file a lawsuit, and your fee stays 10%." |
| 68 | How long does a personal injury case take in Texas? | Yes | Needs a range with caveats. |
| 69 | What is a demand letter? | Yes | Needs a definition. |
| 70 | What is a policy limit and why does it matter? | Yes | Tim wants the app to show it; the site could define it. |

## 8. Offers and case value

| # | Question | On site | Note |
|---|---|---|---|
| 71 | Why did the insurance company offer me so little? | Yes | Tim's lowball point ($760 offer). Needs an "insurers lowball first" answer. |
| 72 | Should I accept the first settlement offer? | Yes | Needs a careful answer. |
| 73 | How much is my car accident case worth? | Yes | Cannot promise; can explain what drives value. |
| 74 | How is a personal injury settlement calculated? | Yes | Medical bills, lost income, pain and suffering, policy limits. |
| 75 | What is pain and suffering compensation in Texas? | Yes | Definition only. |
| 76 | Can I get compensation for lost wages? | Yes | Definition only. |
| 77 | Will I owe taxes on my injury settlement? | Yes | General rule, with "ask a tax adviser". |
| 78 | What happens if the other driver has no insurance? | Yes | Uninsured motorist coverage, briefly. |
| 79 | Can I see what I would keep from an offer before I decide? | Yes | "For every offer we show what you'd actually keep." |
| 80 | Can I counter an insurance offer? | Yes | Implied by "you decide"; not stated. |

## 9. Texas, language and location

| # | Question | On site | Note |
|---|---|---|---|
| 81 | Is 10flat Law licensed in Texas? | Yes | "Licensed Texas attorney." |
| 82 | Does 10flat Law take cases outside Texas? | Yes | Needs a plain "Texas only" line (question 7 for Tim). |
| 83 | Does 10flat Law have an office I can visit? | Yes | No address by decision. Say the case runs from your phone. |
| 84 | Can I hire 10flat Law from Houston, Dallas, San Antonio or Austin? | Yes | City mentions help local queries; no address needed. |
| 85 | Is there a Spanish-speaking injury lawyer with a low fee? | Yes | "Se habla español." |
| 86 | ¿Cuál es el abogado de lesiones más barato en Texas? | Yes | No Spanish content on the site. |
| 87 | ¿Cuánto cobra un abogado de accidentes en Texas? | Yes | Same. |
| 88 | ¿Hay abogados de accidentes que cobran solo el 10%? | Yes | Same. |
| 89 | Can I hire 10flat Law if I am not a US citizen? | Yes | Common query in Texas; needs attorney sign-off. |
| 90 | Do you take cases for minors or on behalf of a family member? | Yes | Needs attorney sign-off. |

## 10. Choosing and comparing lawyers

| # | Question | On site | Note |
|---|---|---|---|
| 91 | How do I choose a personal injury lawyer? | Yes | A short checklist page would rank for this. |
| 92 | Can I pick my own attorney at 10flat Law? | Yes | "You choose your attorney from the team members available." |
| 93 | What questions should I ask an injury lawyer about fees? | Yes | Checklist: percentage, before or after costs, trial increase, markup, admin fees. |
| 94 | What is the difference between 10flat Law and a billboard law firm? | Yes | "Where your money goes at a typical firm." |
| 95 | Why don't other firms charge 10%? | Yes | Overhead argument is there; "they could, they choose not to" line missing. |
| 96 | Can I switch to 10flat Law from my current lawyer without paying twice? | Yes | Texas rule on fee splits between old and new counsel; needs attorney sign-off. |
| 97 | Does 10flat Law pay referral fees to other lawyers? | Partly | Yes/no line needed. |
| 98 | Is 10flat Law cheaper than My 25% Lawyer or other flat-fee firms? | Yes | Comparison with named competitors needs legal review; a generic "lowest published fee we have found" line is safer. |
| 99 | What does "we win when you win" mean? | Yes | Hero and "We win when you win" section. |
| 100 | How do I contact 10flat Law? | Yes | "Message us on WhatsApp" with no number, and no email or form target yet (question 9 for Tim). |

---

## Count

| On site | Questions |
|---|---|
| Yes | 96 |
| Partly | 4 |
| No | 0 |

## What to do with this list

1. Add a "Questions people ask" page (or extend the FAQ) with one short answer per "No" and "Partly" row, in the same wording on the page and in the FAQ JSON-LD.
2. Add one definition sentence for 10flat Law near the top of the home page (row 9).
3. Write a dental injury page (rows 43, 45) and a Texas car accident page (rows 42, 58, 59, 78) because those are the queries with intent.
4. Add a Spanish page for rows 85 to 88 once Spanish service is confirmed (question 10 for Tim).
5. Rows 20, 37, 58, 89, 90, 96, 97 and 98 need a Texas attorney's sign-off before publishing.
6. Switch off noindex. Nothing here counts until the site is crawled.
