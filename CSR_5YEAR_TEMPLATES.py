"""
CSR_5YEAR_TEMPLATES.py — Raj CSR Email Templates: "Pay for 1 Year, Run for 5 Years"
===================================================================================
These are the 5-day email templates for the PCMC-style Co-Funded Pilot Model.
Story arc: CSR pays Year 1 → Municipality sees results → Continues Years 2-5.
Zero risk for the municipality. Proven track record. 51% cost savings.

HOW TO USE:
1. Save these as Gmail drafts with subjects: "CSR EMAIL 1", "CSR EMAIL 2", etc.
   (Raj syncs drafts using regex matching these subjects)
2. OR: Copy each html_body into the Raj template DB directly via the Templates tab
3. The templates use the same placeholders as standard CSR: {{CSR_HEAD_NAME}}, {{COMPANY_NAME}}

Templates:
- Day 1 (Email 1): The Hook — "What if CSR pays Year 1, you run it for 5?"
- Day 3 (Email 2): The Proof — Veer Baji + Sangli case studies
- Day 5 (Email 3): The Numbers — ₹12L + ₹28L = 400 students, ₹1,000/student/year
- Day 7 (Email 4): The Structure — How it works, 90-day launch, exit clause
- Day 10 (Email 5): The Close — Final call, schedule review, references

"""

from engine import HTML_TEMPLATE

# ═══════════════════════════════════════════════════════════════════════════════
# DAY 1 — THE HOOK: "What if a CSR partner pays for Year 1, and you run it for 5?"
# Tone: Bold, visionary, challenging the status quo
# ═══════════════════════════════════════════════════════════════════════════════
CSR_5YEAR_D1_SUBJECT = "{{COMPANY_NAME}} — A 5-Year STEM Pilot Where You Pay Nothing in Year 1"

CSR_5YEAR_D1_BODY = """
<p>Dear {{CSR_HEAD_NAME}},</p>

<p>Most CSR education programs follow the same pattern: <strong>one workshop, one photo-op, one report.</strong> The students forget everything in a month. The school goes back to the old way. And your CSR budget becomes a line item with no lasting legacy.</p>

<p>We built something different.</p>

<p><strong>What if a corporate CSR partner paid for the entire first year — lab setup, full-time teacher, curriculum, kits, everything — and your municipality only started paying from Year 2, <em>after</em> you saw measurable student outcomes?</strong></p>

<p>That's not theory. That's the <strong>WE Smart Lab Co-Funded Pilot</strong> we designed for PCMC — and it's designed for any municipality or municipal corporation that wants future-ready students without taking a financial risk on an unproven vendor.</p>

<p><strong>Here's the structure:</strong></p>
<ul>
<li><strong>Year 1:</strong> Fully funded by a corporate CSR partner (₹12 Lakhs). Complete lab build + full-time teacher + curriculum + quarterly impact reports.</li>
<li><strong>Years 2-5:</strong> Funded by the municipality's education budget (₹7 Lakhs/year). Same scope, same teacher, same outcomes.</li>
<li><strong>Total:</strong> 5 years of continuous STEAM/AI education for under ₹1,000 per student per year.</li>
</ul>

<p><strong>And the exit clause?</strong> If Year 1 outcomes don't meet agreed benchmarks, the municipality can exit with 90 days' notice — no penalty, no claim on installed hardware. The hardware stays with the school for continued use.</p>

<p>This is the lowest-risk entry point for a multi-year STEM program in India. We have already done this. We have the proof. And we have the case studies.</p>

<p>Would you be open to a 20-minute call to see how this model could work for {{COMPANY_NAME}}?</p>

<p>Best regards,</p>
<p><strong>RoboPirate CSR Team</strong><br>
WE Smart Lab Initiative</p>
"""

CSR_5YEAR_D1_HTML = HTML_TEMPLATE.format(body=CSR_5YEAR_D1_BODY)


# ═══════════════════════════════════════════════════════════════════════════════
# DAY 3 — THE PROOF: Veer Baji + Sangli. Real schools, real outcomes, real media.
# Tone: Evidence-backed, credibility-building, "we've already done this"
# ═══════════════════════════════════════════════════════════════════════════════
CSR_5YEAR_D3_SUBJECT = "{{CSR_HEAD_NAME}}, This Model Already Worked — Twice. Here's the Evidence"

CSR_5YEAR_D3_BODY = """
<p>Dear {{CSR_HEAD_NAME}},</p>

<p>In my last email, I shared the <strong>Co-Funded Pilot</strong> concept: CSR pays Year 1, municipality commits from Year 2 after seeing results. I know this sounds bold. So let me show you where it already happened — in government schools, with real students, under real scrutiny.</p>

<p><strong>Case Study 1: Veer Baji Prabhu Vidyalaya, Pune</strong></p>
<p>A government school with limited access to structured STEM learning. No permanent technical teacher. Minimal exposure to future-ready skills. The CSR partner (Cummins) wanted <strong>verifiable impact</strong> — not a one-day workshop photo-op.</p>

<p><strong>What we delivered:</strong></p>
<ul>
<li>Full Academic Year 2024-25, Grades 1-7</li>
<li>1 locally hired instructor, trained and certified in-house by RoboPirate</li>
<li>Consistent weekly participation tracked September to March</li>
<li>Students moved from guided activities to <strong>independent builds</strong> — basic electronic and robotic systems successfully tested</li>
<li>Local employment creation — instructor from an underprivileged background, earning a full year's wage</li>
</ul>

<p>The CSR partner got an audit-ready, outcome-linked report. The school got a working lab. The community got a job. This is the exact template we propose for any municipality.</p>

<p><strong>Case Study 2: Sangli District Collector's Pilot</strong></p>
<p>Initiated and publicly endorsed by <strong>Shri Ashok Kakade IAS</strong>, District Collector, Sangli. Two schools — including K.R.V. Mook-Badhir School for hearing-impaired students. If the model works in the most challenging setting, it works anywhere.</p>

<p><strong>Outcomes:</strong></p>
<ul>
<li>15-day intensive training delivered by in-house certified trainers</li>
<li>AI basics book personally inaugurated by the District Collector</li>
<li>11 different sensors taught via Masterboard platform</li>
<li>3D printing fundamentals — students built and printed physical prototypes</li>
<li>12 student projects completed and presented publicly</li>
<li>Public exhibition organized by the Collector's office — students sold their creations</li>
<li>Media coverage: ABP Majha, Star News Marathi, Bandhuta News, SBN Marathi</li>
</ul>

<p><strong>Phase 2 replicated in a second school (Baal Gruh), validating scale-up.</strong></p>

<p><strong>Why this matters for {{COMPANY_NAME}}:</strong></p>
<p>CSR-underwritten Smart Labs are <strong>executable, auditable, and repeatable.</strong> The local instructor model works — it reduces cost and builds community employment. Student attendance and engagement hold across a full academic year. Grade-wise progression is viable in government-school conditions. And the program is NEP + NCF aligned with measurable outcomes.</p>

<p>We have 85+ CSR labs across 6 states. 55,000+ students. 1.5 lakh+ projects. This is not a first attempt.</p>

<p>Can I send you the full Veer Baji and Sangli impact reports?</p>

<p>Best regards,</p>
<p><strong>RoboPirate CSR Team</strong><br>
WE Smart Lab Initiative</p>
"""

CSR_5YEAR_D3_HTML = HTML_TEMPLATE.format(body=CSR_5YEAR_D3_BODY)


# ═══════════════════════════════════════════════════════════════════════════════
# DAY 5 — THE NUMBERS: The math that makes this a no-brainer for any municipality
# Tone: Finance-focused, sharp, makes the CFO smile
# ═══════════════════════════════════════════════════════════════════════════════
CSR_5YEAR_D5_SUBJECT = "{{COMPANY_NAME}} — The Math: ₹12L CSR + ₹28L You = 400 Students × 5 Years"

CSR_5YEAR_D5_BODY = """
<p>Dear {{CSR_HEAD_NAME}},</p>

<p>Let me cut to the numbers. Because every CSR head I speak to has the same question: <strong>"What does this actually cost, and what do we get?"</strong></p>

<p><strong>The 5-Year PCMC Pilot Structure:</strong></p>
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
<td style="border:1px solid #2a2a4e; padding:8px;">Complete lab build + Year 1 operations + teacher + curriculum</td>
</tr>
<tr>
<td style="border:1px solid #2a2a4e; padding:8px;">Year 2 (2027-28)</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Municipality</td>
<td style="border:1px solid #2a2a4e; padding:8px;">₹7,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Annual subscription (teacher + curriculum + kit refresh)</td>
</tr>
<tr>
<td style="border:1px solid #2a2a4e; padding:8px;">Year 3 (2028-29)</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Municipality</td>
<td style="border:1px solid #2a2a4e; padding:8px;">₹7,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Annual subscription</td>
</tr>
<tr>
<td style="border:1px solid #2a2a4e; padding:8px;">Year 4 (2029-30)</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Municipality</td>
<td style="border:1px solid #2a2a4e; padding:8px;">₹7,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Annual subscription</td>
</tr>
<tr>
<td style="border:1px solid #2a2a4e; padding:8px;">Year 5 (2030-31)</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Municipality</td>
<td style="border:1px solid #2a2a4e; padding:8px;">₹7,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px;">Annual subscription + impact study + case report</td>
</tr>
<tr style="background:#59ced9; color:#0A1628;">
<td style="border:1px solid #2a2a4e; padding:8px; font-weight:bold;">5-Year Total</td>
<td style="border:1px solid #2a2a4e; padding:8px; font-weight:bold;">CSR + Municipality</td>
<td style="border:1px solid #2a2a4e; padding:8px; font-weight:bold;">₹40,00,000</td>
<td style="border:1px solid #2a2a4e; padding:8px; font-weight:bold;">5 years of continuous STEAM/AI for 400 students</td>
</tr>
</table>

<p><strong>The Per-Student Math:</strong></p>
<ul>
<li>₹40,00,000 ÷ 400 students ÷ 5 years = <strong>₹1,000 per student per year</strong></li>
<li>Standalone private rate = ₹2,050 per student per year</li>
<li><strong>This model delivers a 51% saving</strong> over market alternatives</li>
</ul>

<p><strong>What the municipality provides:</strong> A classroom (approx. 250 sq.ft.) + electricity + connectivity.</p>
<p><strong>What RoboPirate provides:</strong> Everything else — 198 items installed, 90 grade kits, 17 workshop kits, 4 drones, 3D printer, laptop, projector, safety gear, full-time trainer, curriculum, LMS, quarterly reports.</p>

<p><strong>The exit protection:</strong> At the end of each year, the municipality has a formal review checkpoint. If outcomes or delivery quality don't meet agreed benchmarks, the municipality may exit with 90 days' notice — no penalty, no claim on installed hardware. The hardware remains with the school for continued use.</p>

<p><strong>This is not a donation. This is a structured, outcome-linked, 5-year partnership.</strong> The CSR partner gets Schedule VII compliance, tax deductibility, and quarterly impact reports. The municipality gets a running, measurable lab at zero Year 1 risk. The students get 5 years of continuous STEM progression from Grade 5 to Grade 9.</p>

<p>Can we schedule a 30-minute review where I walk through the full financial model and the 90-day launch timeline?</p>

<p>Best regards,</p>
<p><strong>RoboPirate CSR Team</strong><br>
WE Smart Lab Initiative</p>
"""

CSR_5YEAR_D5_HTML = HTML_TEMPLATE.format(body=CSR_5YEAR_D5_BODY)


# ═══════════════════════════════════════════════════════════════════════════════
# DAY 7 — THE STRUCTURE: How it works, 90-day launch, and what "managed" means
# Tone: Operational, detailed, removes the "how do we execute?" objection
# ═══════════════════════════════════════════════════════════════════════════════
CSR_5YEAR_D7_SUBJECT = "{{CSR_HEAD_NAME}}, The 90-Day Launch Plan — From MoU to First Class"

CSR_5YEAR_D7_BODY = """
<p>Dear {{CSR_HEAD_NAME}},</p>

<p>By now you understand the concept: CSR pays Year 1, municipality commits from Year 2 after seeing results. You've seen the case studies. You've seen the numbers.</p>

<p>Now let me show you <strong>exactly how we get from signature to first student project.</strong> No vague promises. A week-by-week timeline.</p>

<p><strong>90-Day Launch Timeline — Year 1:</strong></p>

<p><strong>Week 1-2: MoU Signing & School Selection</strong></p>
<ul>
<li>Tripartite MoU drafted (PCMC + CSR Partner + RoboPirate)</li>
<li>PCMC identifies pilot school (Grade 5-9, 300-400 students)</li>
<li>Room handover confirmed (~250 sq.ft. + electricity + connectivity)</li>
<li>CSR partner finalized by RoboPirate from our network: Cummins, Bajaj, Tata Motors, Forbes Marshall, Thermax, Tech Mahindra Foundation, Persistent Systems</li>
</ul>

<p><strong>Week 3-5: Lab Build</strong></p>
<ul>
<li>Electrical, paint, wall theme, furniture install, wiring, posters</li>
<li>All 198 items delivered, installed, and audited</li>
<li>Photo record submitted to municipality</li>
</ul>

<p><strong>Week 6-8: Trainer Onboarding & LMS Setup</strong></p>
<ul>
<li>Locally hired trainer trained at RoboPirate HQ</li>
<li>LMS portal configured for the school</li>
<li>Student accounts created, grade-wise curriculum loaded</li>
</ul>

<p><strong>Week 9-10: Soft Launch</strong></p>
<ul>
<li>Demo classes for Grade 5-6 students</li>
<li>PCMC + CSR partner inauguration event</li>
<li>Free 90-minute hands-on session for students before any paperwork</li>
</ul>

<p><strong>Week 11-12: Full Operations</strong></p>
<ul>
<li>Regular 2-period-per-week schedule running</li>
<li>All 5 grades active simultaneously</li>
<li>Monthly attendance + syllabus progress auto-delivered via LMS</li>
</ul>

<p><strong>Week 13+: Continuous Operations</strong></p>
<ul>
<li>Quarterly impact reports with student-level outcomes, project showcase, photo/video evidence</li>
<li>Annual comprehensive report: pre/post assessments, parent feedback, teacher review, financial utilization statement</li>
<li>Open inspection access — PCMC officials can audit the lab unannounced anytime</li>
<li>Annual public exhibition — students present projects to PCMC, parents, and media (Sangli model)</li>
</ul>

<p><strong>What "Fully Managed" Actually Means:</strong></p>
<table style="width:100%; border-collapse:collapse; margin:15px 0; font-size:13px;">
<tr style="background:#111D2E;">
<th style="border:1px solid #2a2a4e; padding:8px; text-align:left;">Component</th>
<th style="border:1px solid #2a2a4e; padding:8px; text-align:left;">Who Provides</th>
</tr>
<tr><td style="border:1px solid #2a2a4e; padding:8px;">Lab infrastructure (furniture, wiring, paint, posters, interiors)</td><td style="border:1px solid #2a2a4e; padding:8px;">RoboPirate</td></tr>
<tr><td style="border:1px solid #2a2a4e; padding:8px;">120+ DIY kits (robotics, AI, IoT, 3D printing, coding)</td><td style="border:1px solid #2a2a4e; padding:8px;">RoboPirate</td></tr>
<tr><td style="border:1px solid #2a2a4e; padding:8px;">Full-time on-site trained teacher (locally hired)</td><td style="border:1px solid #2a2a4e; padding:8px;">RoboPirate</td></tr>
<tr><td style="border:1px solid #2a2a4e; padding:8px;">Grade-wise NEP + NCF-aligned curriculum</td><td style="border:1px solid #2a2a4e; padding:8px;">RoboPirate</td></tr>
<tr><td style="border:1px solid #2a2a4e; padding:8px;">LMS portal, assessments, student journals, quarterly reports</td><td style="border:1px solid #2a2a4e; padding:8px;">RoboPirate</td></tr>
<tr><td style="border:1px solid #2a2a4e; padding:8px;">Classroom space + electricity + connectivity</td><td style="border:1px solid #2a2a4e; padding:8px;">School / Municipality</td></tr>
</table>

<p><strong>The school simply opens the door. We handle everything else.</strong></p>

<p>Most STEAM initiatives fail because responsibilities are split — one vendor sends kits, another sends a teacher, a third owns curriculum. Accountability vanishes. RoboPirate solves this by owning the entire delivery.</p>

<p>Would you like me to send the full 90-day Gantt chart and the MoU draft template?</p>

<p>Best regards,</p>
<p><strong>RoboPirate CSR Team</strong><br>
WE Smart Lab Initiative</p>
"""

CSR_5YEAR_D7_HTML = HTML_TEMPLATE.format(body=CSR_5YEAR_D7_BODY)


# ═══════════════════════════════════════════════════════════════════════════════
# DAY 10 — THE CLOSE: Final call, urgency without pressure, references available
# Tone: Respectful, decisive, leaves the door open but creates urgency
# ═══════════════════════════════════════════════════════════════════════════════
CSR_5YEAR_D10_SUBJECT = "{{CSR_HEAD_NAME}}, Final Call — FY 2026-27 Budget Window Closes Soon"

CSR_5YEAR_D10_BODY = """
<p>Dear {{CSR_HEAD_NAME}},</p>

<p>This is my final email on the <strong>5-Year Co-Funded Pilot</strong> for FY 2026-27.</p>

<p>I know your inbox is crowded. So let me be direct about why this quarter matters:</p>

<p><strong>April 2026 is the start of the new financial year for both corporate CSR (FY 2026-27) and municipal budgets.</strong> A decision now lets us:</p>
<ul>
<li>Lock a CSR partner for Year 1 before their CSR allocations are committed elsewhere</li>
<li>Complete lab setup by monsoon</li>
<li>Begin classes in the July 2026 academic session</li>
<li>Deliver the first quarterly impact report by October 2026</li>
</ul>

<p><strong>What we have ready for you:</strong></p>
<ul>
<li>✓ Veer Baji Prabhu Vidyalaya (Pune) — full AY 2024-25 impact report available</li>
<li>✓ Sangli District Collector's Office — pilot with Shri Ashok Kakade IAS, 2 schools, Phase 1 + Phase 2 reports</li>
<li>✓ Media coverage — ABP Majha, Star News Marathi, Bandhuta News, SBN Marathi features</li>
<li>✓ Private school contracts — 7 active multi-year contracts across Kalyan and Varanasi</li>
<li>✓ Real student progress reports — chapter-by-chapter assessment samples from AY 2024-25</li>
<li>✓ 85+ labs operational across 6 states, 55,000+ students served</li>
</ul>

<p><strong>The model is simple:</strong> CSR pays ₹12 Lakhs for Year 1. You see everything. If it works, you continue for 4 more years at ₹7 Lakhs each. If it doesn't, you exit with 90 days' notice, hardware stays with the school. Zero risk. Full transparency. Measurable outcomes.</p>

<p>We are not asking for a leap of faith. We are asking for a pilot — with an exit door built in.</p>

<p>I am available for a 30-minute presentation at your office or via video call. No pitch, just facts, the financial model, and a live demo of the LMS and student reports.</p>

<p>If now isn't the right time, I respect that. But if you're even slightly curious, let's not let another quarter pass. The students entering Grade 5 this July won't get this year back.</p>

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
    print("  Pay for 1 Year → Run for 5 Years")
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
