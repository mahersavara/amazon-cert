# HANDOFF: AWS SAA-C03 exam booking + voucher research
Generated: 2026-10-20 01:10 (Asia/Saigon) · Session focus: verify WebSearch fix, choose AWS cert, find cheapest legit exam path, walk Pearson VUE booking to payment screen

## Goal
User (Vietnamese dev) decides whether/when to sit AWS SAA-C03 using the Pearson Global Retake promo, then DVA-C03 later. Agent role: research + browser navigation only; user pays/signs in themself.

## Why This Matters
- Promo = 50% off first attempt + free retake, but first attempt must be completed by 2026-11-17. Missing it = full price ($150 + 10% tax).
- HCMC test centers have no Nov availability; Hanoi does but may fill near deadline.

## Current State
- WebSearch/WebFetch fix (prior handoff) VERIFIED working in this session; `ANTHROPIC_DEFAULT_*_MODEL` vars unset.
- Recommendation given and accepted in principle: SAA-C03 first, DVA-C03 later (Q1 2027) using post-pass 50% benefit voucher.
- User opted in to Pearson Global Retake (confirmation email in user's Gmail, subject "Thank you for opting in!", contains the promo code — not copied here).
- Booking walked twice to Pearson "Enter payment and billing" screen; NOT paid, nothing booked. Last attempt: SAA-C03, English, in-person, Metaserv Company Limited (Hoan Kiem, Hanoi), Fri 2026-11-13 09:00 ICT. Order total with promo: subtotal 150.00, promo -75.00, tax 7.50, total USD 82.50 (without promo: 165.00).
- Pearson/AWS session expires after ~50 min idle; cart is lost on expiry. Unpaid cart does not hold the slot.
- User's latest stance: may study until early Nov and buy then. Agent advised booking now is safer (reschedule allowed up to 2x, ≥24h notice, must stay ≤ 11-17); refund-on-cancel for promo orders UNVERIFIED.
- User asked for full list of online voucher sellers despite advice; list delivered in chat (ITcert ~2.0M VND, CloudCert ~3.1M VND, Skycert, ITexamViet, SecByte ~$120, CertShopServices $119.99, SuperVoucher $119.95/$149, EvolveSkill $119, GetCertified4Less $125, ThunderCat via AWS Marketplace (business), Udemy ~10%). User has not chosen.

## Key Decisions and Why
- SAA before DVA: broader recognition in VN market, stable exam (no replacement announced), DVA excluded from Retake promo, DVA-C03 materials sparse until after 2026-12-01 GA.
- Hanoi Metaserv chosen for price check because all 5 HCMC centers had no Oct–Nov slots (Robusta 10-20 blocked by 24h rule).
- Agent never enters card data or passwords. Sign-in done by typing user's account email into Skill Builder login with existing Builder ID session (user explicitly asked); no password entered.
- AWS policy acceptance clicked only after explicit user approval in chat.

## Rejected Approaches and Traps
- Grey-market vouchers: AWS benefit vouchers are non-transferable; AWS may invalidate results (re:Post staff statement). Cannot combine any voucher with the Retake promo code. ~$76 Associate vouchers likely resold 50% benefit vouchers. SecByte red flags: +880 phone, bKash/Nagad, "exam_voucher_dumps" Telegram.
- re:Invent 2026 50% voucher: in-person attendees only ($2,499 pass) — not viable.
- AIF2CLOUD / CEE challenge: expired or region-locked.
- Reloading a tab while user is mid-sign-in interrupted their login once — don't reload user's sign-in tab.
- Claude-in-Chrome tab group can disappear if user closes/moves tabs; agent then cannot see user's tabs — open a new tab in own group instead.
- Pearson location search defaults to profile address (Hanoi outskirts); Next with no center checked resets search.
- Pearson page wording conflict ("pay full price" generic vs "50% off" AWS-specific) resolved by actual checkout: -75.00 applied.

## Verification Status
- Verified live (checkout screen): promo applies, total USD 82.50 incl. tax.
- Verified official: Pearson VUE Global Retake page (window 09-29→11-17-2026, retake 01-04→04-07-2027, DVA/SAP/MLA/ANS excluded); re:Invent FAQ; SAA-C03 still current, no C04 announced; DVA-C03 reg opens 2026-10-27, GA 2026-12-01.
- Verified on seller pages only (not independently): all third-party voucher prices/terms.
- Unverified: refund on cancel for promo orders; tax treatment when paying with third-party voucher; post-pass 50% voucher validity (wiki says while cert active).
- Not done: ESL +30 min accommodation (must be requested in AWS Certification account BEFORE scheduling).

## Relevant Files and Pointers
- Prior handoff: `plans/reports/handoff-20261019-1538-aws-dva-research-and-websearch-fix.md`
- Settings fix: `C:\Users\kdlin\.claude\settings.json` (env block removed), `settings.9router.json` (router config + token — do not paste), backup `settings.json.bak-261019`
- https://www.pearsonvue.com/us/en/test-takers/free-retake.html
- https://cp.certmetrics.com/amazon/en/schedule/schedule-exam (AWS Certification portal)
- https://aws.amazon.com/events/reinvent/faqs/
- https://aws.amazon.com/certification/certified-solutions-architect-associate/
- Course prices verified: Tutorials Dojo SAA practice $14.99; Cantrill SAA $40; CloudMentor (VN) 3,680,000 VND, starts 2026-10-22.

## Open Work and Dependencies
- Payment/booking decision is the user's; depends on study readiness and slot availability before 2026-11-17.
- If booking: optional ESL accommodation request first; user signs in and enters card themself.
- Study plan not yet written; depends on user's AWS experience level (asked, not answered).
- DVA-C03 full exam guide available from 2026-10-27.

## Unresolved Questions
- User's prior AWS hands-on experience?
- Book now vs wait until early Nov?
- Whether user's employer is an AWS Partner (possible APCR voucher).

---
Fresh-agent prompt:
> Read `F:\Work\ericodyssey\Amazon_Cert\plans\reports\handoff-20261020-0110-aws-saa-exam-booking-and-vouchers.md` and the prior handoff it links. Verify time-sensitive claims (promo window, slot availability) against live pages before advising. Never enter card data or passwords. Reply to user in Vietnamese.
