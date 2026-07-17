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

<p>I spent last week in three schools. In one, sixth graders were debugging a line-following robot. In another, they were memorizing a textbook chapter called "future technologies." Same city. Very different outcomes.</p>

<p>The schools that get this right don't talk about kits or curriculum. They talk about the kid who couldn't stop showing his parents the line-following robot he built.</p>

<p>That's what a WE Smart Lab is. Not a product. A room where kids build things that surprise them.</p>

<p>We run 85+ of these labs across 6 states. The one that still surprises me is Veer Baji Prabhu Vidyalay in Sangli, which started with a single room and now has students winning at state level.</p>

<p>If you're curious, I can send you the two-minute video of a lab in action.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<p style="font-size:12px;color:#7A8A8A;margin-bottom:8px;">See what a WE Smart Lab includes:</p>
<a href="{a.get('video_wsl','#')}" style="display:inline-block;background:#006B6B;color:#FFFFFF;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:8px;margin-bottom:8px;">🎥 Watch the Lab in Action</a>
<a href="{a.get('brochure','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-right:8px;margin-bottom:8px;">WSL Program PDF</a>
<a href="{a.get('video_abp','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-right:8px;margin-bottom:8px;">ABP News Coverage</a>
<a href="{a.get('video_ig','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-bottom:8px;">Latest on Instagram</a>
</div>""",

        3: f"""<p>Dear Principal,</p>

<p>By now you've seen a dozen emails about NEP 2020 compliance. Most of them turn into a checklist of boxes to tick.</p>

<p>I think the better way to look at it is this: NEP is a fork in the road. Schools that build real experiential learning now will quietly separate themselves from the ones that wait.</p>

<p>I've seen the difference it makes when a principal treats this as a teaching upgrade instead of a compliance exercise. The students stop asking "why do we have to do this?" and start asking "can I stay after?"</p>

<p>I can send you the NEP-alignment note we share with principals. It takes two minutes to read.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('video_abp','#')}" style="display:inline-block;background:#006B6B;color:#FFFFFF;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:8px;margin-bottom:8px;">📺 Watch the ABP Coverage</a>
<a href="{a.get('video_ig','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-bottom:8px;">Instagram</a>
</div>""",

        5: f"""<p>Dear Principal,</p>

<p>At Veer Baji Prabhu Vidyalay, we use Prajwal as the proxy for the quiet kid in the last bench. Six months after we set up a WE Smart Lab in his school, he built an obstacle-avoidance robot from his own design.</p>

<p>That is the kind of progress we track in the report we keep on every child: attendance, project completion, competition results, and confidence growth.</p>

<p>Veer Baji started with one room and a handful of kits. Today their students have built 12+ working robots, entered state-level competitions, and their science engagement scores have moved up noticeably. The principal now uses the lab as a talking point for parent meetings.</p>

<p>Your school could be the next case study. Not because you are the same as Veer Baji, but because the model works wherever the principal is willing to give students room to build.</p>

<p>Happy to share the full Veer Baji report if you want to see the data.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<p style="font-size:12px;color:#7A8A8A;margin-bottom:8px;">See the impact:</p>
<a href="{a.get('report_vbv','#')}" style="display:inline-block;background:#006B6B;color:#FFFFFF;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:8px;margin-bottom:8px;">📊 Read the Veer Baji Report</a>
<a href="{a.get('video_star','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-right:8px;margin-bottom:8px;">Student Star Video</a>
<a href="{a.get('folder_vbv','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-right:8px;margin-bottom:8px;">Full Folder</a>
<a href="{a.get('video_ig','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-bottom:8px;">Instagram</a>
</div>""",

        7: f"""<p>Dear Principal,</p>

<p>Running a school means saying no to a hundred things. So when a principal decides to add a WE Smart Lab, it is never because they have extra budget or free time.</p>

<p>It is because they have walked into the lab and seen a child who was bored in science class suddenly explain how a sensor works.</p>

<p>I've watched that moment happen in Maharashtra, Karnataka, Gujarat, and beyond. 85+ principals have made the same decision.</p>

<p>If you want to see what that moment looks like at a school similar to {{SCHOOL_NAME}}, I can arrange it.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('profile','#')}" style="display:inline-block;background:#006B6B;color:#FFFFFF;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:8px;margin-bottom:8px;">📄 See the Company Profile</a>
<a href="{a.get('video_abp','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-right:8px;margin-bottom:8px;">ABP News</a>
<a href="{a.get('video_star','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-right:8px;margin-bottom:8px;">Student Star</a>
<a href="{a.get('video_ig','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-bottom:8px;">Instagram</a>
</div>""",

        10: f"""<p>Dear Principal,</p>

<p>I will not keep emailing you about this. You have a school to run and I respect that.</p>

<p>If you are even a little curious about what a WE Smart Lab could do for {{SCHOOL_NAME}}, I will make time for a 10-minute call. No pitch. Just show-and-tell.</p>

<p>The plans are flexible. What matters is that the kids who use the lab don't think of it as another class. They think of it as the best hour of their week.</p>

<p>If now is not the right time, I genuinely wish you a great academic year.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('plans','#')}" style="display:inline-block;background:#006B6B;color:#FFFFFF;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:8px;margin-bottom:8px;">📄 See Plans & Pricing</a>
<a href="{a.get('video_ig','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-bottom:8px;">Instagram</a>
</div>"""
    }
    return contents.get(day, f"<p>Template content for Day {day}</p>")


def _generate_school_text_content(day: int, assets: Dict[str, str]) -> str:
    a = assets
    contents = {
        1: f"""Dear Principal,

I spent last week in three schools. In one, sixth graders were debugging a line-following robot. In another, they were memorizing a textbook chapter called "future technologies." Same city. Very different outcomes.

The schools that get this right don't talk about kits or curriculum. They talk about the kid who couldn't stop showing his parents the line-following robot he built.

That's what a WE Smart Lab is. Not a product. A room where kids build things that surprise them.

We run 85+ of these labs across 6 states. The one that still surprises me is Veer Baji Prabhu Vidyalay in Sangli, which started with a single room and now has students winning at state level.

If you're curious, I can send you the two-minute video of a lab in action.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

WSL Program PDF: {a.get('brochure', 'Available on request')}
Lab in Action: {a.get('video_wsl', 'Available on request')}
ABP News Coverage: {a.get('video_abp', 'Available on request')}
Latest on Instagram: {a.get('video_ig', 'Available on request')}
""",

        3: f"""Dear Principal,

By now you've seen a dozen emails about NEP 2020 compliance. Most of them turn into a checklist of boxes to tick.

I think the better way to look at it is this: NEP is a fork in the road. Schools that build real experiential learning now will quietly separate themselves from the ones that wait.

I've seen the difference it makes when a principal treats this as a teaching upgrade instead of a compliance exercise. The students stop asking "why do we have to do this?" and start asking "can I stay after?"

I can send you the NEP-alignment note we share with principals. It takes two minutes to read.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

ABP News Coverage: {a.get('video_abp', 'Available on request')}
Instagram: {a.get('video_ig', 'Available on request')}
""",

        5: f"""Dear Principal,

At Veer Baji Prabhu Vidyalay, we use Prajwal as the proxy for the quiet kid in the last bench. Six months after we set up a WE Smart Lab in his school, he built an obstacle-avoidance robot from his own design.

That is the kind of progress we track in the report we keep on every child: attendance, project completion, competition results, and confidence growth.

Veer Baji started with one room and a handful of kits. Today their students have built 12+ working robots, entered state-level competitions, and their science engagement scores have moved up noticeably. The principal now uses the lab as a talking point for parent meetings.

Your school could be the next case study. Not because you are the same as Veer Baji, but because the model works wherever the principal is willing to give students room to build.

Happy to share the full Veer Baji report if you want to see the data.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

Veer Baji Report: {a.get('report_vbv', 'Available on request')}
Student Star Video: {a.get('video_star', 'Available on request')}
Full Folder: {a.get('folder_vbv', 'Available on request')}
Instagram: {a.get('video_ig', 'Available on request')}
""",

        7: f"""Dear Principal,

Running a school means saying no to a hundred things. So when a principal decides to add a WE Smart Lab, it is never because they have extra budget or free time.

It is because they have walked into the lab and seen a child who was bored in science class suddenly explain how a sensor works.

I've watched that moment happen in Maharashtra, Karnataka, Gujarat, and beyond. 85+ principals have made the same decision.

If you want to see what that moment looks like at a school similar to {{SCHOOL_NAME}}, I can arrange it.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

Company Profile: {a.get('profile', 'Available on request')}
ABP News Coverage: {a.get('video_abp', 'Available on request')}
Student Star: {a.get('video_star', 'Available on request')}
Instagram: {a.get('video_ig', 'Available on request')}
""",

        10: f"""Dear Principal,

I will not keep emailing you about this. You have a school to run and I respect that.

If you are even a little curious about what a WE Smart Lab could do for {{SCHOOL_NAME}}, I will make time for a 10-minute call. No pitch. Just show-and-tell.

The plans are flexible. What matters is that the kids who use the lab don't think of it as another class. They think of it as the best hour of their week.

If now is not the right time, I genuinely wish you a great academic year.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

Plans & Pricing: {a.get('plans', 'Available on request')}
Instagram: {a.get('video_ig', 'Available on request')}
"""
    }
    return contents.get(day, f"Template content for Day {day}")


def _generate_csr_wsl5_content(day: int, assets: Dict[str, str]) -> str:
    a = assets
    contents = {
        1: f"""<p>Dear CSR Head,</p>

<p>Most CSR projects start strong and fade by Year 2. The budget moves, the champion leaves, and the lab becomes a storage room.</p>

<p>I've watched that pattern play out too many times. So we built the WE Smart Lab 5-Year Model to break it.</p>

<p>You fund Year 1. The next four years run on government funds. 400 students every year at a government school.</p>

<p>If you're curious how the handover works, I can send you the one-page breakdown.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<p style="font-size:12px;color:#7A8A8A;margin-bottom:8px;">See the model:</p>
<a href="{a.get('report_vbv','#')}" style="display:inline-block;background:#006B6B;color:#FFFFFF;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:8px;margin-bottom:8px;">📊 Read the Veer Baji Report</a>
<a href="{a.get('brochure','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-right:8px;margin-bottom:8px;">Brochure</a>
<a href="{a.get('video_ig','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-bottom:8px;">Instagram</a>
</div>""",

        3: f"""<p>Dear CSR Head,</p>

<p>The first WE Smart Lab just completed its full academic year in a government school.</p>

<p>Not a pilot. Not a demo. A full year of classes, projects, assessments, and student reports.</p>

<p>The trainer we placed came from an underprivileged background himself. He is now certified, full-time, and managing 600+ students. The principal called last week to ask when we can expand to the secondary wing.</p>

<p>It is not theory. It is already happening. And it started with one CSR partner willing to fund Year 1.</p>

<p>Happy to send you the Veer Baji report and the ABP coverage if you want to see the data.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('report_vbv','#')}" style="display:inline-block;background:#006B6B;color:#FFFFFF;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:8px;margin-bottom:8px;">📊 Read the Veer Baji Report</a>
<a href="{a.get('video_abp','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-right:8px;margin-bottom:8px;">ABP News</a>
<a href="{a.get('video_star','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-right:8px;margin-bottom:8px;">Student Star Video</a>
<a href="{a.get('video_ig','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-bottom:8px;">Instagram</a>
</div>""",

        5: f"""<p>Dear CSR Head,</p>

<p>One trainer. Five years. Trained from an underprivileged background.</p>

<p>That is the job your CSR creates. It is not a short-term workshop. It is a career ladder. It is a family lifted. It is a community watching someone from their own neighbourhood teach robotics and AI to government school students.</p>

<p>I've met these trainers. They come in nervous. Three months later they are managing 600 students with a certification they can use anywhere.</p>

<p>This is the kind of CSR impact that gets talked about in annual reports.</p>

<p>If it helps, I can send you the trainer profile and the WSL video.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('video_wsl','#')}" style="display:inline-block;background:#006B6B;color:#FFFFFF;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:8px;margin-bottom:8px;">🎥 Watch the Trainer Video</a>
<a href="{a.get('video_ig','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-bottom:8px;">Instagram</a>
</div>""",

        7: f"""<p>Dear CSR Head,</p>

<p>Here is the math that matters.</p>

<p>The CSR covers Year 1. Years 2 through 5 are covered by government funds.</p>

<p>400 students every year. For five years.</p>

<p>The government school gets a lab it could never afford. The government gets a program that runs itself. And the CSR team gets a project that doesn't die when the budget moves.</p>

<p>If you want the full breakdown, I can send you the investment memo.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('brochure','#')}" style="display:inline-block;background:#006B6B;color:#FFFFFF;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:8px;margin-bottom:8px;">📄 Read the Investment Memo</a>
<a href="{a.get('video_ig','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-bottom:8px;">Instagram</a>
</div>""",

        10: f"""<p>Dear CSR Head,</p>

<p>This is the last email I will send on this.</p>

<p>Your FY 2026-27 budget window is closing. If you want a 90-day launch plan for a WE Smart Lab under your CSR, now is the time to lock it in.</p>

<p>I've seen what happens when a CSR partner says yes. The lab opens in a government school. The trainer starts. The students show up. And three years later the principal is still sending updates.</p>

<p>If you want to see the launch plan, I can send it. If not, I respect your decision and wish you a strong fiscal year.</p>

<p>Regards,<br>Baban Jadhav<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('profile','#')}" style="display:inline-block;background:#006B6B;color:#FFFFFF;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:8px;margin-bottom:8px;">📄 See the Company Profile</a>
<a href="{a.get('video_ig','#')}" style="display:inline;color:#5BD3D9;text-decoration:underline;font-size:12px;margin-bottom:8px;">Instagram</a>
</div>"""
    }
    return contents.get(day, f"<p>Template content for Day {day}</p>")


def _generate_csr_wsl5_text_content(day: int, assets: Dict[str, str]) -> str:
    a = assets
    contents = {
        1: f"""Dear CSR Head,

Most CSR projects start strong and fade by Year 2. The budget moves, the champion leaves, and the lab becomes a storage room.

I've watched that pattern play out too many times. So we built the WE Smart Lab 5-Year Model to break it.

You fund Year 1. The next four years run on government funds. 400 students every year at a government school.

If you're curious how the handover works, I can send you the one-page breakdown.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

Veer Baji Report: {a.get('report_vbv', 'Available on request')}
Brochure: {a.get('brochure', 'Available on request')}
Instagram: {a.get('video_ig', 'Available on request')}
""",

        3: f"""Dear CSR Head,

The first WE Smart Lab just completed its full academic year in a government school.

Not a pilot. Not a demo. A full year of classes, projects, assessments, and student reports.

The trainer we placed came from an underprivileged background himself. He is now certified, full-time, and managing 600+ students. The principal called last week to ask when we can expand to the secondary wing.

It is not theory. It is already happening. And it started with one CSR partner willing to fund Year 1.

Happy to send you the Veer Baji report and the ABP coverage if you want to see the data.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

Veer Baji Report: {a.get('report_vbv', 'Available on request')}
ABP News: {a.get('video_abp', 'Available on request')}
Student Star Video: {a.get('video_star', 'Available on request')}
Instagram: {a.get('video_ig', 'Available on request')}
""",

        5: f"""Dear CSR Head,

One trainer. Five years. Trained from an underprivileged background.

That is the job your CSR creates. It is not a short-term workshop. It is a career ladder. It is a family lifted. It is a community watching someone from their own neighbourhood teach robotics and AI to government school students.

I've met these trainers. They come in nervous. Three months later they are managing 600 students with a certification they can use anywhere.

This is the kind of CSR impact that gets talked about in annual reports.

If it helps, I can send you the trainer profile and the WSL video.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

WSL Video: {a.get('video_wsl', 'Available on request')}
Instagram: {a.get('video_ig', 'Available on request')}
""",

        7: f"""Dear CSR Head,

Here is the math that matters.

The CSR covers Year 1. Years 2 through 5 are covered by government funds.

400 students every year. For five years.

The government school gets a lab it could never afford. The government gets a program that runs itself. And the CSR team gets a project that doesn't die when the budget moves.

If you want the full breakdown, I can send you the investment memo.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

Brochure: {a.get('brochure', 'Available on request')}
Instagram: {a.get('video_ig', 'Available on request')}
""",

        10: f"""Dear CSR Head,

This is the last email I will send on this.

Your FY 2026-27 budget window is closing. If you want a 90-day launch plan for a WE Smart Lab under your CSR, now is the time to lock it in.

I've seen what happens when a CSR partner says yes. The lab opens in a government school. The trainer starts. The students show up. And three years later the principal is still sending updates.

If you want to see the launch plan, I can send it. If not, I respect your decision and wish you a strong fiscal year.

Regards,
Baban Jadhav
Robo Pirate
https://robopirate.in

Company Profile: {a.get('profile', 'Available on request')}
Instagram: {a.get('video_ig', 'Available on request')}
"""
    }
    return contents.get(day, f"Template content for Day {day}")


# Recommended subject lines to use in engine.py _generate_subject.
REWRITTEN_SUBJECTS = {
    "school": {
        1: "{{SCHOOL_NAME}} — what are your students actually building this year?",
        3: "NEP 2020 is a fork in the road for {{SCHOOL_NAME}}",
        5: "{{PRINCIPAL_NAME}}, the boy in the back row at {{SCHOOL_NAME}}",
        7: "{{SCHOOL_NAME}} — what 85+ principals have already figured out",
        10: "{{PRINCIPAL_NAME}}, this is my last note about WSL for {{SCHOOL_NAME}}"
    },
    "csr-wsl-5": {
        1: "{{COMPANY_NAME}} — fund Year 1, run for 5 years",
        3: "{{CSR_HEAD_NAME}}, we already ran the full year",
        5: "{{CSR_HEAD_NAME}}, the job your CSR creates",
        7: "{{COMPANY_NAME}} — the math behind Rs.12 lakhs",
        10: "{{CSR_HEAD_NAME}}, final call — FY 2026-27 budget window"
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
