# CSR 5-Year Co-Funded Pilot — Email Template Review
## RoboPirate | "Pay for 1 Year, Run for 5 Years"
### Ready for Raj Template Import

---

## 📧 EMAIL 1 — DAY 1: THE HOOK
**Subject:** `{{COMPANY_NAME}} — A 5-Year STEM Pilot Where You Pay Nothing in Year 1`

**Story:** Open with the problem — most CSR programs are one-day workshops with no lasting impact. Then introduce the **Co-Funded Pilot** as the alternative: CSR pays Year 1, municipality only commits from Year 2 after seeing results. Zero risk. The exit clause is highlighted upfront. Ends with a soft call to action (20-minute call).

**Key lines:**
- "Most CSR education programs follow the same pattern: one workshop, one photo-op, one report."
- "What if a corporate CSR partner paid for the entire first year... and your municipality only started paying from Year 2, after you saw measurable student outcomes?"
- "If Year 1 outcomes don't meet agreed benchmarks, the municipality can exit with 90 days' notice — no penalty, no claim on installed hardware."

---

## 📧 EMAIL 2 — DAY 3: THE PROOF
**Subject:** `{{CSR_HEAD_NAME}}, This Model Already Worked — Twice. Here's the Evidence`

**Story:** Two hard case studies with real numbers, real schools, real media coverage. **Veer Baji Prabhu Vidyalaya** (Pune, Cummins-funded) — full academic year, Grades 1-7, independent builds, local employment. **Sangli District Collector's Pilot** — endorsed by Shri Ashok Kakade IAS, hearing-impaired school, 3D printing, public exhibition, media coverage (ABP Majha, Star News Marathi). The message: "This is not a first attempt."

**Key lines:**
- "A government school with limited access to structured STEM learning... The CSR partner wanted verifiable impact — not a one-day workshop photo-op."
- "If it worked in the most challenging setting, it works anywhere."
- "85+ CSR labs across 6 states. 55,000+ students. 1.5 lakh+ projects."

---

## 📧 EMAIL 3 — DAY 5: THE NUMBERS
**Subject:** `{{COMPANY_NAME}} — The Math: ₹12L CSR + ₹28L You = 400 Students × 5 Years`

**Story:** Full financial breakdown table. Year-by-year funding split. Per-student math (₹1,000/year vs ₹2,050 standalone = 51% saving). What RoboPirate provides vs what the municipality provides. Exit protection restated. The message: "This is structured, outcome-linked, and financially transparent."

**Key lines:**
- "₹40,00,000 ÷ 400 students ÷ 5 years = ₹1,000 per student per year"
- "Standalone private rate = ₹2,050 per student per year. This model delivers a 51% saving."
- "The school simply opens the door. We handle everything else."
- "This is not a donation. This is a structured, outcome-linked, 5-year partnership."

---

## 📧 EMAIL 4 — DAY 7: THE STRUCTURE
**Subject:** `{{CSR_HEAD_NAME}}, The 90-Day Launch Plan — From MoU to First Class`

**Story:** Week-by-week implementation timeline. MoU signing → Lab build → Trainer onboarding → Soft launch → Full operations. Also includes the "Fully Managed" table showing who does what. The message: "We have a playbook. This is not experimental."

**Key lines:**
- "Week 1-2: MoU Signing & School Selection... Week 3-5: Lab Build... Week 6-8: Trainer Onboarding..."
- "Most STEAM initiatives fail because responsibilities are split — one vendor sends kits, another sends a teacher, a third owns curriculum. Accountability vanishes. RoboPirate solves this by owning the entire delivery."
- "The school simply opens the door. We handle everything else."

---

## 📧 EMAIL 5 — DAY 10: THE CLOSE
**Subject:** `{{CSR_HEAD_NAME}}, Final Call — FY 2026-27 Budget Window Closes Soon`

**Story:** Respectful urgency. Restates the full offer. Lists all 7 ready references. Creates a deadline (April 2026 = new FY start). The message: "This is a pilot with an exit door. The students entering Grade 5 this July won't get this year back."

**Key lines:**
- "April 2026 is the start of the new financial year for both corporate CSR and municipal budgets."
- "We are not asking for a leap of faith. We are asking for a pilot — with an exit door built in."
- "The students entering Grade 5 this July won't get this year back."
- "P.S. — References from Veer Baji (Cummins), Sangli Collector's Office, and our active municipal partnerships are available on request."

---

## 🎯 How to Get These Into Raj

### Option A: Gmail Drafts (Easiest)
1. Open Gmail → Compose
2. To: `om@robopirate.in` (yourself)
3. Subject: Use exactly `CSR EMAIL 1`, `CSR EMAIL 2`, `CSR EMAIL 3`, `CSR EMAIL 4`, `CSR EMAIL 5`
4. Body: Paste the HTML content from `CSR_5YEAR_TEMPLATES.py`
5. Save as Draft (do NOT send)
6. In Raj → Templates tab → "Sync from Gmail"
7. Raj will auto-detect the subjects and load them

### Option B: Direct Import
- Open `CSR_5YEAR_TEMPLATES.py` in the code
- Each template has the full HTML string ready
- Copy/paste into the Raj Templates tab directly

### Option C: New Sequence
- If you want this as a **separate sequence** (e.g., `csr_pcmc` instead of `csr`):
- We can add a new entry to `SEQUENCES` in `engine.py`
- Then the templates auto-load under that new sequence ID

---

## 📊 What Makes This Sequence Different

| Standard CSR Sequence | 5-Year Co-Funded Sequence |
|----------------------|---------------------------|
| General CSR mandate alignment | Specific "pay Year 1, run 5 years" model |
| Impact metrics (generic) | Exact per-student math (₹1,000 vs ₹2,050) |
| Sangli report (general) | Week-by-week 90-day launch plan |
| Meeting request | Exit clause + formal review checkpoint |
| Standard close | "Students entering Grade 5 won't get this year back" |

---

## ✅ Next Steps — Pick One

1. **"Push these into Gmail drafts for me"** — I'll write a script that creates the 5 drafts via Gmail API
2. **"Add this as a new sequence in Raj"** — I'll modify `engine.py` to add `csr_pcmc` as a 3rd sequence
3. **"I want to read the full email text first"** — I'll generate a clean PDF/Word of all 5 emails for your review
4. **"Something's off in the tone"** — Tell me which email and I'll rewrite it

**What would you like to do?**
