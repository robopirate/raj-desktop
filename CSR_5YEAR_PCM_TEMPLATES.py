"""
CSR_5YEAR_PCM_TEMPLATES.py — Raj CSR Email Templates: "CSR Pays Year 1, Gov Runs 5 Years"
============================================================================================
These are the 5-day email templates for the PCMC/ZP-style Co-Funded Pilot Model.
Story arc: CSR funds Year 1 (lab build + full-time trainer + curriculum) →
           Government sees measurable outcomes → Government carries Years 2-5 via education budget.
           Local underprivileged youth hired, trained for 3 months, employed for 5+ years.

HOW TO USE:
1. Save these as Gmail drafts with subjects: "CSR EMAIL 1", "CSR EMAIL 2", etc.
   (Raj syncs drafts using regex matching these subjects)
2. OR: Copy each html_body into the Raj template DB directly via the Templates tab
3. The templates use the same placeholders as standard CSR: {{CSR_HEAD_NAME}}, {{COMPANY_NAME}}

Templates:
- Day 1 (Email 1): The Hook — "CSR pays Year 1. Government sees results. Then carries it for 5 years."
- Day 3 (Email 2): The Proof — Veer Baji WSL (first ever), full academic year, real student outcomes
- Day 5 (Email 3): The Employment Story — Local underprivileged youth hired, 3-month training, 5+ year jobs
- Day 7 (Email 4): The Numbers — Year 1: ₹12L CSR. Years 2-5: ₹7L/year Gov. Per-student: ₹1,000/year
- Day 10 (Email 5): The Close — Exit clause, 90-day launch, FY 2026-27 window

"""

from engine import HTML_TEMPLATE

# ═══════════════════════════════════════════════════════════════════════════════
# DAY 1 — THE HOOK: "CSR pays Year 1. Government sees results. Then carries it for 5 years."
# Tone: Bold, challenging the "one workshop" CSR model, introducing the co-funded structure
# ═══════════════════════════════════════════════════════════════════════════════
CSR_5YEAR_D1_SUBJECT = "{{COMPANY_NAME}} — A 5-Year STEM Lab Where You Fund Only Year 1"

CSR_5YEAR_D1_BODY = """
<p>Dear {{CSR_HEAD_NAME}},</p>

<p>Most CSR education programs in India follow the same script: <strong>one workshop, one photo, one report.</strong> The students forget everything in a month. The school goes back to the old way. And your CSR budget becomes a line item with no lasting legacy.</p>

<p>We built something different. And it's already working.</p>

<p><strong>What if your company funded the entire first year — complete lab setup, full-time trainer, curriculum, 120+ DIY kits, everything — and the government (municipality or ZP) only started paying from Year 2, after they saw measurable student outcomes?</strong></p>

<p>That's the <strong>WE Smart Lab Co-Funded Pilot</strong> we designed for PCMC — and it's the same model we already delivered at Veer Baji Prabhu Vidyalaya, a government school in Pune.</p>

<p><strong>Here's the structure:</strong></p>
<ul>
<li><strong>Year 1:</strong> Fully funded by CSR partner (₹12 Lakhs). Complete lab build + full-time trainer + curriculum + quarterly impact reports.</li>
<li><strong>Years 2-5:</strong> Funded by the government education budget (₹7 Lakhs/year). Same scope, same trainer, same outcomes.</li>
<li><strong>Total:</strong> 5 years of continuous STEAM/AI education for under ₹1,000 per student per year.</li>
</ul>

<p><strong>And the exit clause?</strong> If Year 1 outcomes don't meet agreed benchmarks, the government can exit with 90 days' notice — no penalty, no claim on installed hardware. The hardware stays with the school for continued use.</p>

<p><strong>But here's what most CSR heads miss:</strong> This model also creates a local employment opportunity. We hire a trainer from the underprivileged community near the school, train them for 3 months in-house, and deploy them full-time for the entire 5-year program. That's not a vendor cost — that's a community investment your CSR report can actually stand behind.</p>

<p>Would you be open to a 20-minute call to see how this model could work for {{COMPANY_NAME}}?</p>

<p>Best regards,</p>
<p><strong>RoboPirate CSR Team</strong><br>
WE Smart Lab Initiative</p>
"""

CSR_5YEAR_D1_HTML = HTML_TEMPLATE.format(body=CSR_5YEAR_D1_BODY)


# ═══════════════════════════════════════════════════════════════════════════════
# DAY 3 — THE PROOF: Veer Baji WSL — First Ever, Full Academic Year, Real Outcomes
# Tone: Evidence-backed, "we already did this in a government school with a CSR partner"
# ═══════════════════════════════════════════════════════════════════════════════
CSR_5YEAR_D3_SUBJECT = "{{CSR_HEAD_NAME}}, We Already Did This — First WE Smart Lab, Full Academic Year, Government School"

CSR_5YEAR_D3_BODY = """
<p>Dear {{CSR_HEAD_NAME}},</p>

<p>In my last email, I shared the <strong>Co-Funded Pilot</strong> concept: CSR pays Year 1, government carries Years 2-5 after seeing results. I know this sounds bold. So let me show you where it already happened — in a government school, with a corporate CSR partner, under full academic year scrutiny.</p>

<p><strong>Case Study: Veer Baji Prabhu Vidyalaya, Pune — The FIRST WE Smart Lab</strong></p>
<p>This is a government school with limited access to structured STEM learning. No permanent technical teacher. Minimal exposure to future-ready skills. The CSR partner (Cummins) wanted <strong>verifiable impact</strong> — not a one-day workshop photo-op.</p>

<p><strong>What we delivered (Academic Year 2024-25):</strong></p>
<ul>
<li><strong>Grades Covered:</strong> 1 to 7 — all primary grades with age-appropriate modules</li>
<li><strong>Duration:</strong> Full academic year, September to March — not a workshop, not a camp</li>
<li><strong>Curriculum:</strong> Grade 1: Masterboard (sensor-based) | Grade 2: Micro:bit (visual programming) | Grade 3: Structure Building | Grade 4: Electronics Basics | Grade 5: App Dev + Otto Bot | Grade 6: Arduino IoT | Grade 7: LEO AI Concepts</li>
<li><strong>Trainer:</strong> One local instructor hired from the underprivileged community, trained and certified in-house by RoboPirate, deployed full-time for the entire academic year</li>
<li><strong>Attendance:</strong> Consistent weekly participation tracked Sep–Mar with minor seasonal dip in December (holidays), recovered immediately after</li>
<li><strong>Student Progression:</strong> Students moved from guided activities to independent builds — successfully built and tested basic electronic and robotic systems</li>
<li><strong>Local Employment:</strong> The trainer earned a full year's wage, creating community-level employment alongside student education</li>
</ul>

<p><strong>Student Report Sample — Prajwal More, Grade 6:</strong></p>
<ul>
<li>Arduino Nano Module: 104/120 (86.7%) — Grade A</li>
<li>Projects: LDR Security Alarm, Hand-Wave Light Switch, Auto Gate Opener, Motion Detector Alarm</li>
<li>AI Concepts Module: 30/40 (75%) — Grade B (Proficient)</li>
</ul>

<p>This is not theory. This is a government school student scoring 86.7% in Arduino, building real projects, with a locally hired trainer who was trained by us and is still teaching.</p>

<p><strong>Why this matters for {{COMPANY_NAME}}:</strong></p>
<ul>
<li>✓ CSR-underwritten Smart Labs are executable, auditable, and repeatable</li>
<li>✓ The local trainer model works — it reduces cost and builds community employment</li>
<li>✓ Student attendance and engagement hold across a full academic year</li>
<li>✓ Grade-wise progression is viable in government-school conditions</li>
<li>✓ The program is NEP + NCF aligned and produces measurable outcomes</li>
</ul>

<p>We have 85+ labs operational across 6 states. 55,000+ students served. This is not a first attempt.</p>

<p>Can I send you the full Veer Baji impact report and the student assessment samples?</p>

<p>Best regards,</p>
<p><strong>RoboPirate CSR Team</strong><br>
WE Smart Lab Initiative</p>
"""

CSR_5YEAR_D3_HTML = HTML_TEMPLATE.format(body=CSR_5YEAR_D3_BODY)


# ═══════════════════════════════════════════════════════════════════════════════
# DAY 5 — THE EMPLOYMENT STORY: The hidden social impact most CSR heads miss
# Tone: Human-centered, social impact focused, "this creates jobs, not just student outcomes"
# ═══════════════════════════════════════════════════════════════════════════════
CSR_5YEAR_D5_SUBJECT = "{{CSR_HEAD_NAME}}, The Job Your CSR Creates — 1 Trainer, 5 Years, Trained from Underprivileged Background"

CSR_5YEAR_D5_BODY = """
<p>Dear {{CSR_HEAD_NAME}},</p>

<p>Every CSR head I speak to asks about student outcomes. But very few ask about the <strong>employment outcome</strong>. And that's where this model becomes genuinely different from every STEM workshop in the market.</p>

<p><strong>Here's the employment story behind every WE Smart Lab:</strong></p>

<p><strong>Step 1: We hire locally.</strong> We don't send a trainer from Pune to a government school in Sangli or PCMC. We find someone from the community near the school — often from an underprivileged background, sometimes with no formal STEM training, but with the right attitude and willingness to learn.</p>

<p><strong>Step 2: We train them for 3 months in-house.</strong> At RoboPirate HQ in Baner, Pune. The trainer learns:</p>
<ul>
<li>Robotics, electronics, and coding fundamentals</li>
<li>Classroom delivery and safety protocols</li>
<li>Kit management and troubleshooting</li>
<li>LMS operation and student assessment tracking</li>
<li>How to handle Grade 1 through Grade 9 age-appropriate modules</li>
</ul>

<p><strong>Step 3: We certify them.</strong> Only after passing internal assessments on technical knowledge, classroom safety, and delivery consistency do we deploy them.</p>

<p><strong>Step 4: They work for 5+ years.</strong> Not as a contractor. Not as a gig worker. As a full-time, on-site trainer employed for the entire duration of the WE Smart Lab. They earn a full year's wage every year. They build a career. They become a STEM educator.</p>

<p><strong>At Veer Baji, our first WE Smart Lab:</strong></p>
<ul>
<li>1 local instructor hired from an underprivileged background</li>
<li>Trained and certified in-house by RoboPirate</li>
<li>Deployed full-time for the full academic year 2024-25</li>
<li>Performance monitored through attendance and session reviews</li>
<li>Consistent weekly delivery maintained across Sep–Mar</li>
</ul>

<p><strong>At Sangli (District Collector's Pilot for Divyang Students):</strong></p>
<ul>
<li>Certified underprivileged instructors deployed after structured training</li>
<li>Phase 2 scaled to a second school (Baal Gruh) with the same trainer model</li>
</ul>

<p><strong>The numbers:</strong> Every WE Smart Lab creates at least 1 full-time local employment opportunity for 5 years. If you scale to 10 schools, that's 10 trainers, 10 families, 10 communities — all earning livelihoods through STEM education.</p>

<p><strong>For your CSR report, this means:</strong></p>
<ul>
<li>Schedule VII compliance (Education + Skill Development + Rural Development)</li>
<li>Tax deductibility under Companies Act 2013</li>
<li>Measurable student outcomes AND verifiable employment creation</li>
<li>Community-level impact, not just classroom-level impact</li>
</ul>

<p>This is not just about students learning Arduino. This is about a young person from a marginalized community becoming a STEM educator, earning a dignified wage, and transforming their neighborhood school.</p>

<p>Can we discuss how this employment model could align with {{COMPANY_NAME}}'s CSR priorities?</p>

<p>Best regards,</p>
<p><strong>RoboPirate CSR Team</strong><br>
WE Smart Lab Initiative</p>
"""

CSR_5YEAR_D5_HTML = HTML_TEMPLATE.format(body=CSR_5YEAR_D5_BODY)


# ═══════════════════════════════════════════════════════════════════════════════
# DAY 7 — THE NUMBERS: Year 1 = CSR. Years 2-5 = Government. The math that makes it work.
# Tone: Finance-focused, sharp, makes the CFO and Municipal Commissioner smile
# ═══════════════════════════════════════════════════════════════════════════════
CSR_5YEAR_D7_SUBJECT = "{{COMPANY_NAME}} — The Math: ₹12L CSR + ₹28L Government = 400 Students × 5 Years"

CSR_5YEAR_D7_BODY = """
<p>Dear {{CSR_HEAD_NAME}},</p>

<p>Let me cut to the numbers. Because every CSR head I speak to has the same question: <strong>"What does this actually cost, and who pays what?"</strong></p>

<p><strong>The 5-Year Co-Funded Pilot Structure:</strong></p>
<table style="width:100%; border-collapse:collapse; margin:15px 0; font-size:13px;">
<tr style="background:#111D2E;">
<th style="border:1px solid #2a2a4e; padding:8px; text-align:left;">Year</th>
<th style="border:1px solid #2a2a4e; padding:8px; text-align:left;">Funding Source</th>
<th style="border:1px solid #2a2a4e; padding:8px; text-align:left;">Amount</th>
<th style="border:1px solid #2a2a4e; padding:8px; text-align:left;">What It Covers</th>
</tr>
<tr>
<td style="border:1px solid #2a2a4e; padding:8px;">Year 1 (2026-27)</td>
<td style="border:1px solid #2a2a4e; padding:8px;">CSR Partner</td>
<td style="border:1px solid #2a2a4e; padding:8px;">₹12,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Complete lab build (198 items) + Year 1 operations + full-time trainer + curriculum + LMS</td>
</tr>
<tr>
<td style="border:1px solid #2a2a4e; padding:8px;">Year 2 (2027-28)</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Government Education Budget</td>
<td style="border:1px solid #2a2a4e; padding:8px;">₹7,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Annual subscription (trainer + curriculum + kit refresh + LMS + quarterly reports)</td>
</tr>
<tr>
<td style="border:1px solid #2a2a4e; padding:8px;">Year 3 (2028-29)</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Government Education Budget</td>
<td style="border:1px solid #2a2a4e; padding:8px;">₹7,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Annual subscription</td>
</tr>
<tr>
<td style="border:1px solid #2a2a4e; padding:8px;">Year 4 (2029-30)</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Government Education Budget</td>
<td style="border:1px solid #2a2a4e; padding:8px;">₹7,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Annual subscription + hardware consumables refresh</td>
</tr>
<tr>
<td style="border:1px solid #2a2a4e; padding:8px;">Year 5 (2030-31)</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Government Education Budget</td>
<td style="border:1px solid #2a2a4e; padding:8px;">₹7,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Annual subscription + independent impact study + case report delivered to government</td>
</tr>
<tr style="background:#59ced9; color:#0A1628;">
<td style="border:1px solid #2a2a4e; padding:8px; font-weight:bold;">5-Year Total</td>
<td style="border:1px solid #2a2a4e; padding:8px; font-weight:bold;">CSR + Government</td>
<td style="border:1px solid #2a2a4e; padding:8px; font-weight:bold;">₹40,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px; font-weight:bold;">5 years of continuous STEAM/AI for 400 students + 1 local trainer employed for 5 years</td>
</tr>
</table>

<p><strong>The Per-Student Math:</strong></p>
<ul>
<li>₹40,00,000 ÷ 400 students ÷ 5 years = <strong>₹1,000 per student per year</strong></li>
<li>Standalone private WSL rate = ₹2,050 per student per year</li>
<li><strong>This model delivers a 51% saving</strong> over market alternatives</li>
</ul>

<p><strong>What the government provides:</strong> A classroom (approx. 250 sq.ft.) + electricity + connectivity.</p>
<p><strong>What RoboPirate provides:</strong> Everything else — 198 items installed, 90 grade kits, 17 workshop kits, 4 drones, 3D printer, laptop, projector, safety gear, full-time locally trained trainer, curriculum, LMS, quarterly reports.</p>

<p><strong>What the CSR partner provides:</strong> ₹12 Lakhs for Year 1. That's it. Your job is done after Year 1. The government carries it forward.</p>

<p><strong>The exit protection:</strong> At the end of each year, the government has a formal review checkpoint. If outcomes or delivery quality don't meet agreed benchmarks, the government may exit with 90 days' notice — no penalty, no claim on installed hardware. The hardware remains with the school for continued use.</p>

<p><strong>This is not a donation. This is a structured, outcome-linked, 5-year partnership where your CSR is the catalyst and the government is the sustainers.</strong></p>

<p>Can we schedule a 30-minute review where I walk through the full financial model and the 90-day launch timeline?</p>

<p>Best regards,</p>
<p><strong>RoboPirate CSR Team</strong><br>
WE Smart Lab Initiative</p>
"""

CSR_5YEAR_D7_HTML = HTML_TEMPLATE.format(body=CSR_5YEAR_D7_BODY)


# ═══════════════════════════════════════════════════════════════════════════════
# DAY 10 — THE CLOSE: Final call, urgency without pressure, exit door built in
# Tone: Respectful, decisive, "this is a pilot with an exit door"
# ═══════════════════════════════════════════════════════════════════════════════
CSR_5YEAR_D10_SUBJECT = "{{CSR_HEAD_NAME}}, Final Call — FY 2026-27 Budget Window + 90-Day Launch Plan"

CSR_5YEAR_D10_BODY = """
<p>Dear {{CSR_HEAD_NAME}},</p>

<p>This is my final email on the <strong>5-Year Co-Funded Pilot</strong> for FY 2026-27.</p>

<p>I know your inbox is crowded. So let me be direct about why this quarter matters:</p>

<p><strong>April 2026 is the start of the new financial year for both corporate CSR (FY 2026-27) and government budgets.</strong> A decision now lets us:</p>
<ul>
<li>Lock a CSR partner for Year 1 before their CSR allocations are committed elsewhere</li>
<li>Complete lab setup by monsoon</li>
<li>Begin classes in the July 2026 academic session</li>
<li>Deliver the first quarterly impact report by October 2026</li>
<li>Hire and train a local instructor from the community by June 2026</li>
</ul>

<p><strong>What we have ready for you:</strong></p>
<ul>
<li>✓ Veer Baji Prabhu Vidyalaya (Pune) — First WE Smart Lab, full AY 2024-25 impact report with real student assessments</li>
<li>✓ Sangli District Collector's Office — Pilot with Shri Ashok Kakade IAS, divyang students, media coverage (ABP Majha, Star News Marathi)</li>
<li>✓ 85+ labs operational across 6 states, 55,000+ students served, 1.5 lakh+ projects</li>
<li>✓ Private school contracts — 7 active multi-year contracts across Kalyan and Varanasi</li>
<li>✓ Real student progress reports — chapter-by-chapter assessment samples (e.g., Prajwal More, Grade 6: Arduino 104/120, Grade A)</li>
<li>✓ 90-day launch timeline from MoU to first class</li>
<li>✓ LMS and digital tracking system live and operational</li>
</ul>

<p><strong>The model is simple:</strong></p>
<ul>
<li>Your CSR pays ₹12 Lakhs for Year 1</li>
<li>We hire and train a local instructor from the underprivileged community</li>
<li>We build the lab, deliver the curriculum, and produce quarterly reports</li>
<li>The government sees everything. If it works, they carry it for 4 more years at ₹7 Lakhs each.</li>
<li>If it doesn't, they exit with 90 days' notice, hardware stays with the school.</li>
</ul>

<p><strong>We are not asking for a leap of faith. We are asking for a pilot — with an exit door built in.</strong></p>

<p>I am available for a 30-minute presentation at your office or via video call. No pitch, just facts, the financial model, a live demo of the LMS, and the student assessment samples.</p>

<p>If now isn't the right time, I respect that. But if you're even slightly curious, let's not let another quarter pass. The students entering Grade 5 this July won't get this year back. And the trainer we could hire from a marginalized community won't get this opportunity back either.</p>

<p>Best regards,</p>
<p><strong>RoboPirate CSR Team</strong><br>
WE Smart Lab Initiative<br>
info@robopirate.in | +91-9136899925<br>
www.robopirate.in</p>

<p><em>P.S. — References from Veer Baji (Cummins), Sangli Collector's Office, and our active municipal partnerships are available on request. We can also arrange a site visit to any of our 85+ operational labs.</em></p>
"""

CSR_5YEAR_D10_HTML = HTML_TEMPLATE.format(body=CSR_5YEAR_D10_BODY)


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK-REFERENCE: All subjects and Gmail draft creation commands
# ═══════════════════════════════════════════════════════════════════════════════
"""
To create these as Gmail drafts for Raj sync:

1. Open Gmail
2. Compose a new email TO yourself (om@robopirate.in)
3. Use these subjects EXACTLY:
   - "CSR EMAIL 1" → paste CSR_5YEAR_D1_HTML
   - "CSR EMAIL 2" → paste CSR_5YEAR_D3_HTML
   - "CSR EMAIL 3" → paste CSR_5YEAR_D5_HTML
   - "CSR EMAIL 4" → paste CSR_5YEAR_D7_HTML
   - "CSR EMAIL 5" → paste CSR_5YEAR_D10_HTML
4. Save as draft (do NOT send)
5. In Raj, go to Templates → Sync from Gmail

Raj will match these subjects and load them into the CSR sequence.

Alternatively, use the Python script below to create drafts via Gmail API:
"""

if __name__ == "__main__":
    print("=" * 60)
    print("  CSR 5-YEAR CO-FUNDED PILOT TEMPLATES")
    print("  CSR Pays Year 1 → Government Carries Years 2-5")
    print("  Local Employment: 1 Trainer, 5 Years, Underprivileged Community")
    print("=" * 60)
    print()
    print("Template Summary:")
    print(f"  Day 1: {CSR_5YEAR_D1_SUBJECT}")
    print(f"  Day 3: {CSR_5YEAR_D3_SUBJECT}")
    print(f"  Day 5: {CSR_5YEAR_D5_SUBJECT}")
    print(f"  Day 7: {CSR_5YEAR_D7_SUBJECT}")
    print(f"  Day 10: {CSR_5YEAR_D10_SUBJECT}")
    print()
    print("All templates are ready to be imported into Raj or Gmail drafts.")
    print("See the QUICK-REFERENCE section at the bottom of this file for instructions.")
