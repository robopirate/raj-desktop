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

<p>In one, students were crowded around a robot they had built, testing it again and again. In another, the lesson had ended, but a few children stayed back to finish what they had started. The third school reminded me that every classroom has its own way of teaching.</p>

<p>The biggest difference wasn't the budget, the building, or even the students.</p>

<p>It was the kind of experiences they were getting inside the classroom.</p>

<p>That's why we built WE Smart Lab.</p>

<p>Not to add another subject to a school's timetable, but to create a space where students learn by building, experimenting and solving problems together.</p>

<p>Since then, we've had the opportunity to bring the same approach to schools across 6 states. Today, more than 65,000 students learn through 85+ WE Smart Labs. One school I often think back to is Veer Baji Prabhu Vidyalay in Pune, where our first WE Smart Lab has now completed a full academic year of classes, projects and assessments.</p>

<p>If you're interested, here's a short walkthrough of a working WE Smart Lab. I hope it gives you a feel for what students experience every week.</p>

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

<p>The answer is simpler than it is usually made to sound. NEP encourages experiential learning. It wants students to understand concepts by doing, not only by reading about them in a textbook.</p>

<p>That's exactly why we built WE Smart Lab. The lab sits inside your school and works alongside your regular teaching. It does not replace any class or teacher. It gives students a place to build, experiment and solve problems with their hands, while the concepts stay connected to what they learn in their classrooms.</p>

<p>After seeing how the lab works, schools usually ask a second question: how is student learning observed and documented?</p>

<p>We keep a structured record for every child in the lab, including attendance, project completion and assessment outcomes.</p>

<p>I've attached a specimen student assessment report so you can see the kind of learning records schools receive through WE Smart Lab.</p>

<p>If anything in the report raises a question, just reply to this email. I'll be happy to answer it.</p>

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

In one, students were crowded around a robot they had built, testing it again and again. In another, the lesson had ended, but a few children stayed back to finish what they had started. The third school reminded me that every classroom has its own way of teaching.

The biggest difference wasn't the budget, the building, or even the students.

It was the kind of experiences they were getting inside the classroom.

That's why we built WE Smart Lab.

Not to add another subject to a school's timetable, but to create a space where students learn by building, experimenting and solving problems together.

Since then, we've had the opportunity to bring the same approach to schools across 6 states. Today, more than 65,000 students learn through 85+ WE Smart Labs. One school I often think back to is Veer Baji Prabhu Vidyalay in Pune, where our first WE Smart Lab has now completed a full academic year of classes, projects and assessments.

If you're interested, here's a short walkthrough of a working WE Smart Lab. I hope it gives you a feel for what students experience every week.

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

The answer is simpler than it is usually made to sound. NEP encourages experiential learning. It wants students to understand concepts by doing, not only by reading about them in a textbook.

That's exactly why we built WE Smart Lab. The lab sits inside your school and works alongside your regular teaching. It does not replace any class or teacher. It gives students a place to build, experiment and solve problems with their hands, while the concepts stay connected to what they learn in their classrooms.

After seeing how the lab works, schools usually ask a second question: how is student learning observed and documented?

We keep a structured record for every child in the lab, including attendance, project completion and assessment outcomes.

I've attached a specimen student assessment report so you can see the kind of learning records schools receive through WE Smart Lab.

If anything in the report raises a question, just reply to this email. I'll be happy to answer it.

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

<p>Our goal was to create a space where students could build, experiment, and learn STEM through hands-on experiences inside their own school.</p>

<p>Over the course of the academic year, the lab became an active learning space where students explored robotics, coding, AI and STEM through hands-on activities.</p>

<p>By the end of the academic year, the project had achieved what we set out to do. Yet one question remained.</p>

<p>What happens after Year 1?</p>

<p>That question challenged many of our own assumptions and eventually changed the way we think about CSR-funded STEM education.</p>

<p>The answer to that question shaped every WE Smart Lab we've built since. Since 2020, it has grown into 85+ labs across 6 states, where more than 65,000 students now learn.</p>

<p>If you'd like to know more about Robo Pirate and understand how WE Smart Lab works, I'd invite you to explore the attached brochure.</p>

<p>Regards,<br>Baban Jadhav<br>Program Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<p style="font-size:13px;color:#7A8A8A;">P.S. 85+ labs, 65,000 students, 6 states — but it started with one classroom in Pune.</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<table cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 14px;">
<tr><td align="center" bgcolor="#FFD400" style="border-radius:6px;">
<a href="{a.get('brochure','#')}" target="_blank" style="display:inline-block;padding:13px 30px;font-size:15px;font-weight:bold;color:#9333EA;text-decoration:none;font-family:Arial,Helvetica,sans-serif;">📄 Explore the WE Smart Lab Brochure</a>
</td></tr>
</table>
</div>""",

        3: f"""<p>Dear CSR Head,</p>

<p>In my previous email, I shared the question that stayed with us after completing our first WE Smart Lab:</p>

<p>What happens after Year 1?</p>

<p>Before we could answer it, we found ourselves looking back at where it all began.</p>

<p>Our first WE Smart Lab wasn't just about installing equipment. It was about creating a learning space where students could explore, build, experiment and discover through hands-on STEM education.</p>

<p>Seeing students engage with it reminded us that meaningful impact isn't measured by installation alone. It is shaped by what happens inside the classroom every single day.</p>

<p>By the middle of the year, the lab had become part of the school's week. Students looked forward to their sessions, and teachers planned around them. That is exactly what made one question impossible to ignore: when something works this well, what happens when the year ends?</p>

<p style="margin:0 0 16px;padding:12px 16px;border-left:3px solid #FFD400;background-color:#F5F9F9;font-style:italic;">"[FILL: TEACHER QUOTE — 2 lines max]"<br><span style="font-style:normal;font-weight:bold;font-size:13px;">— [FILL: TEACHER NAME], [FILL: DESIGNATION], Veer Baji Prabhu Vidyalay, Pune</span></p>

<p>If you're curious to see that first WE Smart Lab in action, we've shared a short video below.</p>

<p>In my next email, I'll share the answer we arrived at, and why it changed the way every WE Smart Lab is designed today.</p>

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

<p>In my previous email, I shared a glimpse of our first WE Smart Lab.</p>

<p>Completing that first year taught us something we had not expected. The lab worked. Students were learning, teachers were engaged, and the school wanted more.</p>

<p>That is when the real lesson became clear: lasting impact requires lasting ownership.</p>

<p>A lab that runs entirely on one year of CSR support has an expiry date. So we redesigned the model. In every WE Smart Lab that followed, the CSR partner makes Year 1 possible — and the school's own elected corporator commits the next four years through ward development funds, written into the same agreement the CSR partner signs.</p>

<p>Same lab. Same students. But instead of a one-year project, it becomes a five-year programme with shared ownership.</p>

<p>For a CSR partner, that means every rupee of Year-1 support is matched four times over. Your funding doesn't buy a project — it unlocks a programme.</p>

<p>This insight transformed how we implement. And because we believe in showing our work, we documented the entire first year—the implementation, classroom activities, student learning and outcomes—in our Transparency Report.</p>

<p>We've also attached the complete story of that first WE Smart Lab.</p>

<p>Rather than telling you what we learned, we'd prefer to share the project exactly as it happened.</p>

<p>In my next email, I'll show you what this model made possible across other schools and communities.</p>

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

<p>In my previous email, I shared the lesson that reshaped our work: lasting impact needs lasting ownership.</p>

<p>That lesson became the foundation for every WE Smart Lab that followed.</p>

<p>So, does the model actually work at scale?</p>

<p>One example is our implementation in Sangli, run in association with the District Collector, Sangli and the Worship Earth Foundation, where the project expanded in phases to reach more students while adapting to local needs. What began as a pilot continued into Phase II, with 11 more institutions joining the programme.</p>

<p>We've also had the privilege of conducting STEM learning experiences with Divyang students, reinforcing our belief that hands-on learning should be accessible to every child.</p>

<p>The initiative was covered independently by local media organisations, which meant the story reached people beyond us.</p>

<p>We've attached the Sangli project report, along with a few short videos and independent media coverage that showcase these initiatives.</p>

<p>In my final email, I'll share how your organisation can be part of this model.</p>

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

<p>Over the past few emails, I've shared the journey of WE Smart Lab—from our first implementation to the lesson that reshaped it, and the communities now proving it at scale.</p>

<p>Every project has reinforced one belief:</p>

<p>Meaningful STEM education isn't created by installing equipment alone.</p>

<p>It grows through consistent engagement, hands-on learning, teacher support, and a model designed to keep running long after the first year ends.</p>

<p>If your organisation is exploring CSR initiatives in education, we'd be delighted to explore how this model can be adapted to your goals and the communities you serve.</p>

<p>A complete first year — lab setup, a dedicated trained instructor, grade-wise curriculum, assessments and reporting — is a ₹12 lakh CSR commitment per school, fully itemised in the attached partnership proposal.</p>

<p>And it is built on the model you've read about: your organisation funds one year. The model carries it for five.</p>

<p>If the proposal aligns with your CSR objectives, just reply to this email — or reach me directly on +91 91368 99925.</p>

<p>And if you're in or around Pune, I'd rather show you than tell you. Reply and I'll arrange a 30-minute visit to a running WE Smart Lab this month.</p>

<p>Thank you for taking the time to follow our journey.</p>

<p>We hope it has offered a clear picture of what WE Smart Lab stands for and the impact we aspire to create with every partnership.</p>

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

Our goal was to create a space where students could build, experiment, and learn STEM through hands-on experiences inside their own school.

Over the course of the academic year, the lab became an active learning space where students explored robotics, coding, AI and STEM through hands-on activities.

By the end of the academic year, the project had achieved what we set out to do. Yet one question remained.

What happens after Year 1?

That question challenged many of our own assumptions and eventually changed the way we think about CSR-funded STEM education.

The answer to that question shaped every WE Smart Lab we've built since. Since 2020, it has grown into 85+ labs across 6 states, where more than 65,000 students now learn.

If you'd like to know more about Robo Pirate and understand how WE Smart Lab works, I'd invite you to explore the attached brochure.

Regards,
Baban Jadhav
Program Director – WE Smart Lab
Robo Pirate
https://robopirate.in

P.S. 85+ labs, 65,000 students, 6 states — but it started with one classroom in Pune.

Explore the WE Smart Lab Brochure: {a.get('brochure', 'Available on request')}
""",

        3: f"""Dear CSR Head,

In my previous email, I shared the question that stayed with us after completing our first WE Smart Lab:

What happens after Year 1?

Before we could answer it, we found ourselves looking back at where it all began.

Our first WE Smart Lab wasn't just about installing equipment. It was about creating a learning space where students could explore, build, experiment and discover through hands-on STEM education.

Seeing students engage with it reminded us that meaningful impact isn't measured by installation alone. It is shaped by what happens inside the classroom every single day.

By the middle of the year, the lab had become part of the school's week. Students looked forward to their sessions, and teachers planned around them. That is exactly what made one question impossible to ignore: when something works this well, what happens when the year ends?

"[FILL: TEACHER QUOTE — 2 lines max]"
— [FILL: TEACHER NAME], [FILL: DESIGNATION], Veer Baji Prabhu Vidyalay, Pune

If you're curious to see that first WE Smart Lab in action, we've shared a short video below.

In my next email, I'll share the answer we arrived at, and why it changed the way every WE Smart Lab is designed today.

Regards,
Baban Jadhav
Program Director – WE Smart Lab
Robo Pirate
https://robopirate.in

Watch Our First WE Smart Lab in Action: {a.get('video_wsl', 'Available on request')}

Trouble opening the link? Reply to this email and I'll send the video directly.
""",

        5: f"""Dear CSR Head,

In my previous email, I shared a glimpse of our first WE Smart Lab.

Completing that first year taught us something we had not expected. The lab worked. Students were learning, teachers were engaged, and the school wanted more.

That is when the real lesson became clear: lasting impact requires lasting ownership.

A lab that runs entirely on one year of CSR support has an expiry date. So we redesigned the model. In every WE Smart Lab that followed, the CSR partner makes Year 1 possible — and the school's own elected corporator commits the next four years through ward development funds, written into the same agreement the CSR partner signs.

Same lab. Same students. But instead of a one-year project, it becomes a five-year programme with shared ownership.

For a CSR partner, that means every rupee of Year-1 support is matched four times over. Your funding doesn't buy a project — it unlocks a programme.

This insight transformed how we implement. And because we believe in showing our work, we documented the entire first year—the implementation, classroom activities, student learning and outcomes—in our Transparency Report.

We've also attached the complete story of that first WE Smart Lab.

Rather than telling you what we learned, we'd prefer to share the project exactly as it happened.

In my next email, I'll show you what this model made possible across other schools and communities.

Regards,
Baban Jadhav
Program Director – WE Smart Lab
Robo Pirate
https://robopirate.in

Read the First WE Smart Lab Story: {a.get('report_1st_wsl', 'Available on request')}
View the Transparency Report: {a.get('report_vbv', 'Available on request')}
""",

        7: f"""Dear CSR Head,

In my previous email, I shared the lesson that reshaped our work: lasting impact needs lasting ownership.

That lesson became the foundation for every WE Smart Lab that followed.

So, does the model actually work at scale?

One example is our implementation in Sangli, run in association with the District Collector, Sangli and the Worship Earth Foundation, where the project expanded in phases to reach more students while adapting to local needs. What began as a pilot continued into Phase II, with 11 more institutions joining the programme.

We've also had the privilege of conducting STEM learning experiences with Divyang students, reinforcing our belief that hands-on learning should be accessible to every child.

The initiative was covered independently by local media organisations, which meant the story reached people beyond us.

We've attached the Sangli project report, along with a few short videos and independent media coverage that showcase these initiatives.

In my final email, I'll share how your organisation can be part of this model.

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

Over the past few emails, I've shared the journey of WE Smart Lab—from our first implementation to the lesson that reshaped it, and the communities now proving it at scale.

Every project has reinforced one belief:

Meaningful STEM education isn't created by installing equipment alone.

It grows through consistent engagement, hands-on learning, teacher support, and a model designed to keep running long after the first year ends.

If your organisation is exploring CSR initiatives in education, we'd be delighted to explore how this model can be adapted to your goals and the communities you serve.

A complete first year — lab setup, a dedicated trained instructor, grade-wise curriculum, assessments and reporting — is a ₹12 lakh CSR commitment per school, fully itemised in the attached partnership proposal.

And it is built on the model you've read about: your organisation funds one year. The model carries it for five.

If the proposal aligns with your CSR objectives, just reply to this email — or reach me directly on +91 91368 99925.

And if you're in or around Pune, I'd rather show you than tell you. Reply and I'll arrange a 30-minute visit to a running WE Smart Lab this month.

Thank you for taking the time to follow our journey.

We hope it has offered a clear picture of what WE Smart Lab stands for and the impact we aspire to create with every partnership.

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
        5: "CSR supports Year 1. The school's corporator commits four more — in writing.",
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
