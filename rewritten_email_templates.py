"""
rewritten_email_templates.py
Rewritten SCHOOL and CSR-WSL-5 email sequences for Raj Desktop v5.0.

These functions mirror the signatures used in engine.py so they can be dropped in
as replacements for _generate_school_content, _generate_school_text_content,
_generate_csr_wsl5_content, and _generate_csr_wsl5_text_content.

Rewrite goals:
- Founder-to-founder tone, not marketing copy.
- Each email adds new value; no repeated openers, closings, stats, or CTAs.
- All placeholders, links, reports, videos, and attachments preserved.
- Sign-off: Robo Pirate team / RoboPirate.
"""

from typing import Dict


def _generate_school_content(day: int, assets: Dict[str, str]) -> str:
    a = assets
    contents = {
        1: f"""<p>Dear Principal,</p>

<p>Last week I visited three schools.</p>

<p>In one, students crowded around a robot they had built. In another, a few children stayed back after the lesson to finish what they had started. The third reminded me that every classroom teaches differently.</p>

<p>The biggest difference wasn't the budget, the building, or even the students.</p>

<p>It was the kind of experiences they were getting inside the classroom.</p>

<p>That's why we built WE Smart Lab.</p>

<p>Not another subject on the timetable — a space where students learn by building and solving problems together.</p>

<p>Since then, we've brought the same approach to schools across 6 states. Today, more than 65,000 students learn with us across 85+ schools. One I often think back to is Veer Baji Prabhu Vidyalay in Pune, where our first lab completed a full academic year.</p>

<p>If you're interested, here's a short walkthrough of a working lab.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('video_wsl','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">▶ Watch a WE Smart Lab in Action</a>
</td></tr>
</table>
<p style="margin:0 0 6px;font-size:14px;"><strong><a href="{a.get('brochure','#')}" style="color:#9333EA;">WE Smart Lab Brochure</a></strong></p>
<p style="margin:0 0 6px;font-size:14px;"><strong><a href="{a.get('video_abp','#')}" style="color:#9333EA;">ABP Majha Coverage</a></strong></p>
<p style="margin:0 0 6px;font-size:14px;"><strong><a href="https://robopirate.in" style="color:#9333EA;">robopirate.in</a></strong></p>
</div>""",

        3: f"""<p>Dear Principal,</p>

<p>One question comes up in almost every conversation I have with principals: how does WE Smart Lab fit with NEP?</p>

<p>The answer is simpler than it sounds. NEP encourages experiential learning — concepts understood by doing, not only read in textbooks.</p>

<p>That's exactly why we built WE Smart Lab. It sits inside your school, works alongside regular teaching, and replaces no class or teacher. Students build and solve problems with their hands, tied to what they learn in class.</p>

<p>Schools then ask: how is learning documented?</p>

<p>We keep a structured record for every child: attendance, projects, assessment outcomes.</p>

<p>I've attached a specimen assessment report so you can see the records schools receive.</p>

<p>If it raises questions, just reply. I'm happy to answer.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('report_vbv','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">📄 View Sample Student Assessment Report</a>
</td></tr>
</table>
<p style="margin:0 0 6px;font-size:14px;"><strong><a href="{a.get('video_abp','#')}" style="color:#9333EA;">ABP Majha Coverage</a></strong></p>
<p style="margin:0 0 6px;font-size:14px;"><strong><a href="https://robopirate.in" style="color:#9333EA;">robopirate.in</a></strong></p>
</div>""",

        5: f"""<p>Dear Principal,</p>

<p>A year is long enough to know whether something truly belongs in a school.</p>

<p>The real test is what happens in month eight, when the novelty is gone and the timetable takes over.</p>

<p>Our first WE Smart Lab at Veer Baji Prabhu Vidyalay in Pune has now completed a full academic year. It became a regular part of the school's timetable, and students consistently participated in projects and assessments.</p>

<p>That consistency is what we were hoping for when we set up our first lab.</p>

<p>We documented the full year in the First WE Smart Lab Annual Report. We share it with schools that want to see how the lab works over time, not just how it starts.</p>

<p>Here it is.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('report_1st_wsl','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">📄 Read the First WE Smart Lab Annual Report</a>
</td></tr>
</table>
<p style="margin:0 0 6px;font-size:14px;"><strong><a href="https://robopirate.in/case-studies" style="color:#9333EA;">🌐 Explore More WE Smart Lab Case Studies</a></strong></p>
</div>""",

        7: f"""<p>Dear Principal,</p>

<p>When work matters, it has a way of getting noticed on its own.</p>

<p>In Sangli, we ran an AI and Robotics initiative for specially-abled students, in association with the District Collector, Sangli and the Worship Earth Foundation.</p>

<p>What began as a pilot did more than go well. It validated both student outcomes and the delivery model, and that is what allowed the programme to grow. Eleven more institutions have now joined in Phase II.</p>

<p>The initiative was also covered independently by local media organisations, which meant the story reached people beyond us.</p>

<p>If you would like to see what the initiative looked like in practice, the report is below.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('report_sangli1','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">📘 Explore the Sangli Initiative</a>
</td></tr>
</table>
<p style="margin:0;font-size:12px;color:#7A8A8A;">Also covered by:<br>
<a href="{a.get('video_abp','#')}" style="color:#9333EA;">ABP Majha</a> • <a href="{a.get('video_star','#')}" style="color:#9333EA;">Star News Marathi</a> • <a href="{a.get('video_bandhuta','#')}" style="color:#9333EA;">Bandhuta News</a> • <a href="{a.get('video_sbn','#')}" style="color:#9333EA;">SBN Marathi</a> • <a href="{a.get('video_we','#')}" style="color:#9333EA;">Worship Earth</a></p>
</div>""",

        10: f"""<p>Dear Principal,</p>

<p>Over these emails, I have shared why we built WE Smart Lab, how learning is documented, what a full year looks like, and how the work has been noticed beyond us.</p>

<p>If you're wondering what bringing WE Smart Lab to your school would involve, the Subscription Overview is a good place to start.</p>

<p>It outlines how implementation works, what your school receives, the support we provide through the year, and how the subscription is structured.</p>

<p>If you would like to discuss whether WE Smart Lab is a good fit for {{SCHOOL_NAME}}, I am happy to talk it through.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('plans','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">📄 View WE Smart Lab Subscription Overview</a>
</td></tr>
</table>
<p style="margin:0;font-size:13px;color:#7A8A8A;">Or simply reply to this email to schedule a discussion.</p>
</div>"""
    }
    return contents.get(day, f"<p>Template content for Day {day}</p>")


def _generate_school_text_content(day: int, assets: Dict[str, str]) -> str:
    a = assets
    contents = {
        1: f"""Dear Principal,

Last week I visited three schools.

In one, students crowded around a robot they had built. In another, a few children stayed back after the lesson to finish what they had started. The third reminded me that every classroom teaches differently.

The biggest difference wasn't the budget, the building, or even the students.

It was the kind of experiences they were getting inside the classroom.

That's why we built WE Smart Lab.

Not another subject on the timetable — a space where students learn by building and solving problems together.

Since then, we've brought the same approach to schools across 6 states. Today, more than 65,000 students learn with us across 85+ schools. One I often think back to is Veer Baji Prabhu Vidyalay in Pune, where our first lab completed a full academic year.

If you're interested, here's a short walkthrough of a working lab.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

Watch a WE Smart Lab in Action: {a.get('video_wsl', 'Available on request')}
WE Smart Lab Brochure: {a.get('brochure', 'Available on request')}
ABP Majha Coverage: {a.get('video_abp', 'Available on request')}
""",

        3: f"""Dear Principal,

One question comes up in almost every conversation I have with principals: how does WE Smart Lab fit with NEP?

The answer is simpler than it sounds. NEP encourages experiential learning — concepts understood by doing, not only read in textbooks.

That's exactly why we built WE Smart Lab. It sits inside your school, works alongside regular teaching, and replaces no class or teacher. Students build and solve problems with their hands, tied to what they learn in class.

Schools then ask: how is learning documented?

We keep a structured record for every child: attendance, projects, assessment outcomes.

I've attached a specimen assessment report so you can see the records schools receive.

If it raises questions, just reply. I'm happy to answer.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

Sample Student Assessment Report: {a.get('report_vbv', 'Available on request')}
ABP Majha Coverage: {a.get('video_abp', 'Available on request')}
""",

        5: f"""Dear Principal,

A year is long enough to know whether something truly belongs in a school.

The real test is what happens in month eight, when the novelty is gone and the timetable takes over.

Our first WE Smart Lab at Veer Baji Prabhu Vidyalay in Pune has now completed a full academic year. It became a regular part of the school's timetable, and students consistently participated in projects and assessments.

That consistency is what we were hoping for when we set up our first lab.

We documented the full year in the First WE Smart Lab Annual Report. We share it with schools that want to see how the lab works over time, not just how it starts.

Here it is.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

First WE Smart Lab Annual Report: {a.get('report_1st_wsl', 'Available on request')}
More WE Smart Lab Case Studies: https://robopirate.in/case-studies
""",

        7: f"""Dear Principal,

When work matters, it has a way of getting noticed on its own.

In Sangli, we ran an AI and Robotics initiative for specially-abled students, in association with the District Collector, Sangli and the Worship Earth Foundation.

What began as a pilot did more than go well. It validated both student outcomes and the delivery model, and that is what allowed the programme to grow. Eleven more institutions have now joined in Phase II.

The initiative was also covered independently by local media organisations, which meant the story reached people beyond us.

If you would like to see what the initiative looked like in practice, the report is below.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

Explore the Sangli Initiative: {a.get('report_sangli1', 'Available on request')}

Also featured by:
ABP Majha: {a.get('video_abp', 'Available on request')}
Star News Marathi: {a.get('video_star', 'Available on request')}
Bandhuta News: {a.get('video_bandhuta', 'Available on request')}
SBN Marathi: {a.get('video_sbn', 'Available on request')}
Worship Earth: {a.get('video_we', 'Available on request')}
""",

        10: f"""Dear Principal,

Over these emails, I have shared why we built WE Smart Lab, how learning is documented, what a full year looks like, and how the work has been noticed beyond us.

If you're wondering what bringing WE Smart Lab to your school would involve, the Subscription Overview is a good place to start.

It outlines how implementation works, what your school receives, the support we provide through the year, and how the subscription is structured.

If you would like to discuss whether WE Smart Lab is a good fit for {{SCHOOL_NAME}}, I am happy to talk it through.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

WE Smart Lab Subscription Overview: {a.get('plans', 'Available on request')}

Or simply reply to this email to schedule a discussion.
"""
    }
    return contents.get(day, f"Template content for Day {day}")


def _generate_csr_wsl5_content(day: int, assets: Dict[str, str]) -> str:
    a = assets
    contents = {
        1: f"""<p>Dear CSR Head,</p>

<p>Our first WE Smart Lab began as a one-year CSR project.</p>

<p>Our goal was a space where students could build, experiment and learn STEM hands-on inside their own school. Over the year, it became where students explored robotics, coding and AI.</p>

<p>By year-end, the project had achieved what we set out to do. Yet one question remained.</p>

<p>What happens after Year 1?</p>

<p>The answer to that question shaped everything we've built since. What started in a college robotics club in 2018 — through years of kits, curricula and classrooms — is today the WE Smart Lab model, working with 85+ schools across 6 states, where more than 65,000 students learn. The first of those labs ran its full academic year with CSR support from Cummins.</p>

<p>If you'd like to know who we are and how the lab works, the attached brochure is a good place to start.</p>

<p>Regards,<br>Baban Jadhav<br>Program Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<p style="font-size:13px;color:#7A8A8A;">P.S. 85+ schools, 65,000+ students, 6 states — but it started with one classroom in Pune.</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('brochure','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">📄 Explore the WE Smart Lab Brochure</a>
</td></tr>
</table>
</div>""",

        3: f"""<p>Dear CSR Head,</p>

<p>In my previous email, I shared the question that stayed with us after our first WE Smart Lab:</p>

<p>What happens after Year 1?</p>

<p>That lab was never just equipment. It was a space where students could explore, build and discover through hands-on STEM.</p>

<p>Impact, we learned, isn't measured on installation day. It is what happens in the classroom every day after.</p>

<p>By mid-year, the lab was part of the school's week. Students looked forward to sessions; teachers planned around them. Which made one question unavoidable: when something works this well, what happens when the year ends?</p>

<p>Here is a short video of that lab in action.</p>

<p>Next email: the answer we arrived at, and how it changed every lab we've designed since.</p>

<p>Regards,<br>Baban Jadhav<br>Program Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('video_wsl','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">🎥 Watch Our First WE Smart Lab in Action</a>
</td></tr>
</table>
<p style="margin:0 0 6px;font-size:13px;color:#7A8A8A;">Trouble opening the link? Reply to this email and I'll send the video directly.</p>
</div>""",

        5: f"""<p>Dear CSR Head,</p>

<p>My last email was a glimpse of our first lab.</p>

<p>That first year taught us something unexpected: the lab worked, and the school wanted more.</p>

<p>The lesson: lasting impact requires lasting ownership.</p>

<p>A lab running on one year of CSR support has an expiry date. So we redesigned it: the CSR partner makes Year 1 possible, and the local government body contractually commits the next four years — written into the same agreement the CSR partner signs.</p>

<p>Same lab, same students — but a five-year programme, not a one-year project.</p>

<p>For a CSR partner, the math is simple: your Year-1 commitment of ₹12 lakh unlocks a ₹40 lakh five-year programme. Every rupee you commit is more than tripled.</p>

<p>Attached: the full story of that first year, and the Transparency Report documenting it. We'd rather show than tell.</p>

<p>Next email: what that made possible across other schools and communities.</p>

<p>Regards,<br>Baban Jadhav<br>Program Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 10px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('report_1st_wsl','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">📄 Read the First WE Smart Lab Story</a>
</td></tr>
</table>
<table cellpadding="0" cellspacing="0" border="0" style="margin:0 0 14px;">
<tr><td align="center" bgcolor="#FFFFFF" style="border-radius:6px;border:1px solid #FF2E88;">
<a href="{a.get('report_vbv','#')}" target="_blank" style="display:inline-block;padding:12px 28px;font-size:14px;font-weight:bold;color:#FF2E88;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">📑 View the Transparency Report</a>
</td></tr>
</table>
</div>""",

        7: f"""<p>Dear CSR Head,</p>

<p>My last email shared the lesson: lasting impact needs lasting ownership.</p>

<p>It became every lab's foundation.</p>

<p>So, does the model actually work at scale?</p>

<p>One example: our Sangli initiative, run with the District Collector, Sangli and the Worship Earth Foundation. The pilot grew into a completed Phase II across 11 more institutions — and following those outcomes, the District Collector announced expansion to 12–13 Divyang schools across the district.</p>

<p>We also ran STEM sessions for Divyang students — hands-on learning should be reachable for every child.</p>

<p>Each lab also creates local employment: every WE Smart Lab hires and trains an instructor from the local community — often from underprivileged backgrounds — creating ₹9–12 lakh of dignified livelihood per school across the programme.</p>

<p>Local media covered it.</p>

<p>The Sangli report, short videos and media coverage are below.</p>

<p>Final email next: how your organisation can be part of this model.</p>

<p>Regards,<br>Baban Jadhav<br>Program Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<p style="font-size:13px;color:#7A8A8A;">P.S. The work we're proudest of in Sangli isn't in any report — it's the Divyang students who now build robots alongside everyone else.</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('report_sangli','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">📄 Read the Sangli Project Report</a>
</td></tr>
</table>
<a href="{a.get('video_divyang','#')}" target="_blank" style="display:inline-block;background:#FFFFFF;color:#FF2E88;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:12px;margin:0 8px 8px 0;border:1px solid #FF2E88;">🎥 Sangli Divyang Reel</a>
<a href="{a.get('video_gruh','#')}" target="_blank" style="display:inline-block;background:#FFFFFF;color:#FF2E88;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:12px;margin:0 8px 8px 0;border:1px solid #FF2E88;">🎥 Divyang Gruh Workshop Reel</a>
<a href="{a.get('video_abp','#')}" target="_blank" style="display:inline-block;background:#FFFFFF;color:#FF2E88;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:12px;margin:0 8px 8px 0;border:1px solid #FF2E88;">📰 ABP Coverage</a>
<a href="{a.get('video_star','#')}" target="_blank" style="display:inline-block;background:#FFFFFF;color:#FF2E88;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:12px;margin:0 8px 8px 0;border:1px solid #FF2E88;">📰 Star News Marathi</a>
<a href="{a.get('video_bandhuta','#')}" target="_blank" style="display:inline-block;background:#FFFFFF;color:#FF2E88;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:12px;margin:0 8px 8px 0;border:1px solid #FF2E88;">📰 Bandhuta Coverage</a>
<a href="{a.get('video_sbn','#')}" target="_blank" style="display:inline-block;background:#FFFFFF;color:#FF2E88;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:12px;margin:0 8px 8px 0;border:1px solid #FF2E88;">📰 SBN Marathi</a>
<a href="{a.get('video_we','#')}" target="_blank" style="display:inline-block;background:#FFFFFF;color:#FF2E88;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:12px;margin:0 8px 8px 0;border:1px solid #FF2E88;">📰 Worship Earth</a>
</div>""",

        10: f"""<p>Dear CSR Head,</p>

<p>Over these emails, I've shared our journey.</p>

<p>A complete first year — lab, instructor, curriculum, assessments, reporting — starts at a ₹12 lakh CSR commitment per school — whether for one school or a six-school district pilot — itemised in the proposal. Your organisation funds one year; the local government contractually funds four more. Your ₹12 lakh unlocks a ₹40 lakh programme.</p>

<p>The model is endorsed by PCMC's Samaj Vikas Vibhag; a 6-school pilot Letter of Intent is already in process.</p>

<p>If it aligns, reply — or call +91 91368 99925.</p>

<p>Near Pune? Reply and I'll arrange a 30-minute lab visit.</p>

<p>Somewhere in a government school in Maharashtra, a girl is in Grade 4 today. By the time a partnership like this is signed, she'll be in Grade 5. By 2030, she could graduate with a five-year STEM portfolio in her hand. Let's not make her wait another year.</p>

<p>Regards,<br>Baban Jadhav<br>Program Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<p style="font-size:13px;color:#7A8A8A;">P.S. If your team finalises CSR allocations this quarter, I can send a one-page budget note your committee can use.</p>

<p style="margin-top:16px;padding-top:12px;border-top:1px solid #E0E8E8;font-size:12px;color:#7A8A8A;line-height:1.5;">Implementation partner: Worship Earth Foundation · CSR-1 Registration [FILL: CSR-1 NUMBER] · 80G/12A certified<br>Aligned with Schedule VII (ii), Companies Act 2013 — promotion of education · SDG 4 (Quality Education)<br>Fund utilisation certificates, quarterly implementation reports and annual impact assessments provided.</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('proposal_2nd','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">📄 View the Partnership Proposal</a>
</td></tr>
</table>
</div>"""
    }
    return contents.get(day, f"<p>Template content for Day {day}</p>")


def _generate_csr_wsl5_text_content(day: int, assets: Dict[str, str]) -> str:
    a = assets
    contents = {
        1: f"""Dear CSR Head,

Our first WE Smart Lab began as a one-year CSR project.

Our goal was a space where students could build, experiment and learn STEM hands-on inside their own school. Over the year, it became where students explored robotics, coding and AI.

By year-end, the project had achieved what we set out to do. Yet one question remained.

What happens after Year 1?

The answer to that question shaped everything we've built since. What started in a college robotics club in 2018 — through years of kits, curricula and classrooms — is today the WE Smart Lab model, working with 85+ schools across 6 states, where more than 65,000 students learn. The first of those labs ran its full academic year with CSR support from Cummins.

If you'd like to know who we are and how the lab works, the attached brochure is a good place to start.

Regards,
Baban Jadhav
Program Director – WE Smart Lab
Robo Pirate
https://robopirate.in

P.S. 85+ schools, 65,000+ students, 6 states — but it started with one classroom in Pune.

Explore the WE Smart Lab Brochure: {a.get('brochure', 'Available on request')}
""",

        3: f"""Dear CSR Head,

In my previous email, I shared the question that stayed with us after our first WE Smart Lab:

What happens after Year 1?

That lab was never just equipment. It was a space where students could explore, build and discover through hands-on STEM.

Impact, we learned, isn't measured on installation day. It is what happens in the classroom every day after.

By mid-year, the lab was part of the school's week. Students looked forward to sessions; teachers planned around them. Which made one question unavoidable: when something works this well, what happens when the year ends?

Here is a short video of that lab in action.

Next email: the answer we arrived at, and how it changed every lab we've designed since.

Regards,
Baban Jadhav
Program Director – WE Smart Lab
Robo Pirate
https://robopirate.in

Watch Our First WE Smart Lab in Action: {a.get('video_wsl', 'Available on request')}

Trouble opening the link? Reply to this email and I'll send the video directly.
""",

        5: f"""Dear CSR Head,

My last email was a glimpse of our first lab.

That first year taught us something unexpected: the lab worked, and the school wanted more.

The lesson: lasting impact requires lasting ownership.

A lab running on one year of CSR support has an expiry date. So we redesigned it: the CSR partner makes Year 1 possible, and the local government body contractually commits the next four years — written into the same agreement the CSR partner signs.

Same lab, same students — but a five-year programme, not a one-year project.

For a CSR partner, the math is simple: your Year-1 commitment of ₹12 lakh unlocks a ₹40 lakh five-year programme. Every rupee you commit is more than tripled.

Attached: the full story of that first year, and the Transparency Report documenting it. We'd rather show than tell.

Next email: what that made possible across other schools and communities.

Regards,
Baban Jadhav
Program Director – WE Smart Lab
Robo Pirate
https://robopirate.in

Read the First WE Smart Lab Story: {a.get('report_1st_wsl', 'Available on request')}
View the Transparency Report: {a.get('report_vbv', 'Available on request')}
""",

        7: f"""Dear CSR Head,

My last email shared the lesson: lasting impact needs lasting ownership.

It became every lab's foundation.

So, does the model actually work at scale?

One example: our Sangli initiative, run with the District Collector, Sangli and the Worship Earth Foundation. The pilot grew into a completed Phase II across 11 more institutions — and following those outcomes, the District Collector announced expansion to 12–13 Divyang schools across the district.

We also ran STEM sessions for Divyang students — hands-on learning should be reachable for every child.

Each lab also creates local employment: every WE Smart Lab hires and trains an instructor from the local community — often from underprivileged backgrounds — creating ₹9–12 lakh of dignified livelihood per school across the programme.

Local media covered it.

The Sangli report, short videos and media coverage are below.

Final email next: how your organisation can be part of this model.

Regards,
Baban Jadhav
Program Director – WE Smart Lab
Robo Pirate
https://robopirate.in

P.S. The work we're proudest of in Sangli isn't in any report — it's the Divyang students who now build robots alongside everyone else.

Read the Sangli Project Report: {a.get('report_sangli', 'Available on request')}
Sangli Divyang Reel: {a.get('video_divyang', 'Available on request')}
Divyang Gruh Workshop Reel: {a.get('video_gruh', 'Available on request')}
ABP Coverage: {a.get('video_abp', 'Available on request')}
Star News Marathi: {a.get('video_star', 'Available on request')}
Bandhuta Coverage: {a.get('video_bandhuta', 'Available on request')}
SBN Marathi: {a.get('video_sbn', 'Available on request')}
Worship Earth: {a.get('video_we', 'Available on request')}
""",

        10: f"""Dear CSR Head,

Over these emails, I've shared our journey.

A complete first year — lab, instructor, curriculum, assessments, reporting — starts at a ₹12 lakh CSR commitment per school — whether for one school or a six-school district pilot — itemised in the proposal. Your organisation funds one year; the local government contractually funds four more. Your ₹12 lakh unlocks a ₹40 lakh programme.

The model is endorsed by PCMC's Samaj Vikas Vibhag; a 6-school pilot Letter of Intent is already in process.

If it aligns, reply — or call +91 91368 99925.

Near Pune? Reply and I'll arrange a 30-minute lab visit.

Somewhere in a government school in Maharashtra, a girl is in Grade 4 today. By the time a partnership like this is signed, she'll be in Grade 5. By 2030, she could graduate with a five-year STEM portfolio in her hand. Let's not make her wait another year.

Regards,
Baban Jadhav
Program Director – WE Smart Lab
Robo Pirate
https://robopirate.in

P.S. If your team finalises CSR allocations this quarter, I can send a one-page budget note your committee can use.

Implementation partner: Worship Earth Foundation · CSR-1 Registration [FILL: CSR-1 NUMBER] · 80G/12A certified
Aligned with Schedule VII (ii), Companies Act 2013 — promotion of education · SDG 4 (Quality Education)
Fund utilisation certificates, quarterly implementation reports and annual impact assessments provided.

View the Partnership Proposal: {a.get('proposal_2nd', 'Available on request')}
"""
    }
    return contents.get(day, f"Template content for Day {day}")


# Recommended subject lines to use in engine.py _generate_subject.
REWRITTEN_SUBJECTS = {
    "school": {
        1: "{{SCHOOL_NAME}} — a classroom I couldn't stop thinking about",
        3: "So how does WE Smart Lab fit with NEP?",
        5: "What a full academic year taught us",
        7: "When the work spoke for itself in Sangli",
        10: "What bringing WE Smart Lab to {{SCHOOL_NAME}} would involve"
    },
    "csr-wsl-5": {
        1: "What happens after Year 1?",
        3: "Looking back at where it began",
        5: "What we discovered after Year 1",
        7: "When the work grew beyond one school",
        10: "An invitation to partner"
    }
}

# Preview text (preheader) shown next to the subject in the inbox.
# Injected as hidden text at the top of the HTML body.
PREHEADERS = {
    "school": {
        1: "Last week I visited three schools. One difference stayed with me.",
        3: "It is the question principals ask most. The answer is simpler than it sounds.",
        5: "Our first lab at Veer Baji Prabhu Vidyalay just completed year one.",
        7: "An AI and Robotics initiative for specially-abled students in Sangli.",
        10: "The Subscription Overview, and an open door whenever you are ready."
    },
    "csr-wsl-5": {
        1: "It ran the full academic year. Then we faced a question we had not planned for.",
        3: "Our first WE Smart Lab wasn't just about installing equipment.",
        5: "CSR supports Year 1. The local government contractually commits four more.",
        7: "One example is our implementation in Sangli, expanded in phases.",
        10: "A complete first year of a WE Smart Lab is a ₹12 lakh CSR commitment — and it unlocks four more."
    }
}


if __name__ == "__main__":
    # Quick sanity check: verify all 10 emails return non-empty strings.
    school_assets = {
        "brochure": "https://example.com/brochure",
        "video_wsl": "https://example.com/wsl",
        "video_abp": "https://example.com/abp",
        "video_ig": "https://example.com/ig",
        "report_vbv": "https://example.com/vbv",
        "video_star": "https://example.com/star",
        "folder_vbv": "https://example.com/folder",
        "profile": "https://example.com/profile",
        "plans": "https://example.com/plans"
    }
    csr_assets = {
        "report_vbv": "https://example.com/vbv",
        "brochure": "https://example.com/brochure",
        "video_ig": "https://example.com/ig",
        "video_abp": "https://example.com/abp",
        "video_star": "https://example.com/star",
        "video_wsl": "https://example.com/wsl",
        "profile": "https://example.com/profile"
    }
    ok = True
    for day in (1, 3, 5, 7, 10):
        if not _generate_school_content(day, school_assets):
            ok = False
        if not _generate_school_text_content(day, school_assets):
            ok = False
        if not _generate_csr_wsl5_content(day, csr_assets):
            ok = False
        if not _generate_csr_wsl5_text_content(day, csr_assets):
            ok = False
    print("All templates generated:", "OK" if ok else "FAILED")
