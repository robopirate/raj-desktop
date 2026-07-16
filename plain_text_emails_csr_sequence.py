"""
plain_text_emails_csr_sequence.py — RoboPirate Raj Plain Text Email Templates for CSR Sequence
================================================================================================

This module provides:
1. Plain text versions of all 5 CSR sequence emails (Days 1, 3, 5, 7, 10)
2. A plain_text_body column migration for the templates table
3. HTML-to-plain-text conversion utilities
4. Integration hooks into the CampaignEngine render() and send pipeline

USAGE:
    from plain_text_emails_csr_sequence import (
        CSR_PLAIN_TEXT_TEMPLATES,
        html_to_plain_text,
        inject_plain_text_into_engine,
        migrate_plain_text_column
    )

    # One-time DB migration
    migrate_plain_text_column(db)

    # Inject into engine instance
    inject_plain_text_into_engine(engine)

    # Or access templates directly
    day1 = CSR_PLAIN_TEXT_TEMPLATES["csr"][1]  # {subject, body}

TONE: Diplomatic, genuine, not pushy. Omkar's voice. Sugar-coated, never begging.
Signed off as "Omkar" — not "Vikram" or "RoboPirate CSR Team".
"""

import re
import html
from typing import Dict, Tuple, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# ASSET LINKS (shared across all CSR plain text emails)
# ═══════════════════════════════════════════════════════════════════════════════

ASSETS_CSR = {
    1: {
        "report_sangli1": "https://drive.google.com/file/d/1HpNdnamA2k3H0xkKr58STEKMNu5RgHPx/view",
        "video_abp": "https://youtu.be/FJ2_W53WjmA",
        "video_sangli": "https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view",
        "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/",
    },
    3: {
        "report_sangli1": "https://drive.google.com/file/d/1HpNdnamA2k3H0xkKr58STEKMNu5RgHPx/view",
        "brochure": "https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view",
        "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/",
    },
    5: {
        "report_sangli2": "https://drive.google.com/file/d/1pKSm1WPlPk-we4aC-uhqxEy8w-BYygSN/view",
        "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view",
        "video_star": "https://youtube.com/watch?v=iziKPBSfGKU",
        "folder_sangli": "https://drive.google.com/drive/folders/15sc5iOIKTBZyenb2rCpGVAK1lExcG5BC",
        "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/",
    },
    7: {
        "plans": "https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view",
        "video_wsl": "https://drive.google.com/file/d/1KPrC2IpdooxazGJiyVe79JgyWlJbOxzu/view",
        "video_abp": "https://youtu.be/FJ2_W53WjmA",
        "video_sangli": "https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view",
        "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/",
    },
    10: {
        "profile": "https://drive.google.com/file/d/1g9JJ4_VO_28QKYD7iVVDJZcv9l4uRbZu/view",
        "kits": "https://drive.google.com/file/d/1cvi4p8IHgx1MekanVRHN3Fo4Lk9vbubX/view",
        "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/",
    },
}

SOCIAL_LINKS = {
    "instagram_baalgruh": "https://www.instagram.com/p/DSSIy7nglXc/",
    "instagram_veer_baji_2nd": "https://www.instagram.com/p/DTDBcsdk9FI/",
    "instagram_sangli_divyang": "https://www.instagram.com/p/DMhEDutOrl-/",
}

PDF_LINKS = {
    "pmc_proposal": "https://drive.google.com/file/d/15-EuEcwci8olOSnm0V50laK3gVKCUCe-/view",
    "wsl": "https://drive.google.com/file/d/1qiWBhOiklPpwU5NaVkqnfjA6v9q3YumS/view",
    "sangli_report": "https://drive.google.com/file/d/1H7mHVTWGprbd4ZFSPoJZPeAc1nHnih3J/view",
    "subscription": "https://drive.google.com/file/d/1p2CyHVZK_giZj0KNDGTTs_-s7HxVnQ_C/view",
}

# ═══════════════════════════════════════════════════════════════════════════════
# PLAIN TEXT CSR EMAIL TEMPLATES
# Each entry: { "subject": str, "body": str }
# ═══════════════════════════════════════════════════════════════════════════════

CSR_PLAIN_TEXT_TEMPLATES = {
    "csr": {},
    "csr-wsl-5": {},
}

# ───────────────────────────────────────────────────────────────────────────────
# DAY 1 — The Introduction: Soft, warm, sets the stage without asking for anything
# ───────────────────────────────────────────────────────────────────────────────

CSR_PLAIN_TEXT_TEMPLATES["csr"][1] = {
    "subject": "{{COMPANY_NAME}} — Something quietly changing in government schools",
    "body": """Dear {{CSR_HEAD_NAME}},

I hope this finds you well. I wanted to share something that has been unfolding quietly but meaningfully over the past few years — and I believe it might resonate with the work {{COMPANY_NAME}} is already doing in the community.

In government schools across Maharashtra, children are experiencing hands-on STEM education for the first time. Not through one-off workshops, but through full academic year programs where they build robots, write code, fly drones, and present their own projects to district officials and the media.

We call it the WE Smart Lab. It is a fully equipped, fully managed STEM lab that runs inside a government school for the entire academic year — with a dedicated trainer, structured curriculum, and quarterly impact reports that actually show what the children learned.

A few things I thought you might find interesting:

  • Sangli District Collector's Office — a 15-school pilot initiated by Shri Ashok Kakade IAS, including a school for hearing-impaired children. The students built and sold their creations at a public exhibition. Media coverage followed: ABP Majha, Star News Marathi, Bandhuta News, SBN Marathi.
    Report: {report_sangli1}
    Video (Sangli): {video_sangli}
    Video (ABP Majha): {video_abp}

  • Veer Baji Prabhu Vidyalaya, Pune — a full academic year program (2024-25) where students progressed from guided activities to independent builds. The trainer was locally hired from an underprivileged background — so the program created employment alongside education.

We have 85+ labs running across 6 states now. Over 55,000 students. More than 1.5 lakh projects completed.

I am not writing to ask for a commitment today. I simply wanted you to know this exists — and that if {{COMPANY_NAME}} ever explores STEM education as part of its CSR journey, there is a model here that has already been tested, measured, and replicated.

Here is a short clip from one of our recent sessions:
  {video_ig}

If you would ever like to see the Sangli impact report or simply have a conversation about what this could look like for your organisation, I would be genuinely happy to connect.

Warmly,
Omkar
RoboPirate
www.robopirate.in | info@robopirate.in

P.S. — We also develop detailed child-level progress reports over the academic year. Prajwal, one of our students from the Sangli program, has a report that tracks his journey from not knowing what a sensor was to building a working obstacle-avoidance robot. I would be glad to share it if you are curious.""".format(
        report_sangli1=ASSETS_CSR[1]["report_sangli1"],
        video_sangli=ASSETS_CSR[1]["video_sangli"],
        video_abp=ASSETS_CSR[1]["video_abp"],
        video_ig=ASSETS_CSR[1]["video_ig"],
    )
}

# ───────────────────────────────────────────────────────────────────────────────
# DAY 3 — The Proof: Show, don't tell. Let the work speak.
# ───────────────────────────────────────────────────────────────────────────────

CSR_PLAIN_TEXT_TEMPLATES["csr"][3] = {
    "subject": "{{CSR_HEAD_NAME}}, what 15 schools in Sangli looked like after one year",
    "body": """Dear {{CSR_HEAD_NAME}},

A quick follow-up to my last note. I mentioned the Sangli pilot — I wanted to share a little more about what actually happened there, because I think the details matter more than the pitch ever could.

Shri Ashok Kakade IAS, the District Collector of Sangli, initiated this pilot because he wanted something that would outlast his tenure. Not a photo opportunity. Something the schools could keep running.

Here is what the first phase delivered:

  • 15 government schools equipped with fully managed STEAM/AI labs
  • 15-day intensive training delivered by our in-house certified trainers
  • 11 different sensors taught through the Masterboard platform
  • 3D printing fundamentals — students designed and printed physical prototypes
  • 12 student projects completed and presented publicly
  • A public exhibition organised by the Collector's office where students sold their work
  • Media coverage across four Marathi news channels

And then Phase 2 happened at Baal Gruh, validating that the model could scale.
  Instagram: """ + SOCIAL_LINKS["instagram_baalgruh"] + """

The reason I share this is simple: we deliver, and we always deliver. We do not let people down. When a district collector puts his name behind a program, and when children from underprivileged backgrounds stand in front of cameras explaining how they built a robot — that is not marketing. That is proof.

The Sangli Phase 1 report is here if you would like to see the numbers:
  """ + ASSETS_CSR[3]["report_sangli1"] + """

And here is a broader overview of what a WE Smart Lab includes:
  """ + ASSETS_CSR[3]["brochure"] + """

A short clip from our latest session:
  """ + ASSETS_CSR[3]["video_ig"] + """

No pressure at all — I just believe good work deserves to be seen.

Warmly,
Omkar
RoboPirate
www.robopirate.in | info@robopirate.in

P.S. — If {{COMPANY_NAME}} is only able to support a partial adoption — say 3 or 4 schools instead of a full district — that is absolutely possible. We have built this to be modular."""
}

# ───────────────────────────────────────────────────────────────────────────────
# DAY 5 — The Depth: Prajwal's report, the human story, the quiet impact
# ───────────────────────────────────────────────────────────────────────────────

CSR_PLAIN_TEXT_TEMPLATES["csr"][5] = {
    "subject": "{{CSR_HEAD_NAME}}, the report we develop over children like Prajwal",
    "body": """Dear {{CSR_HEAD_NAME}},

I want to tell you about Prajwal.

Prajwal is a student from one of our government school programs. When he started, he had never touched a circuit board. By the end of the academic year, he had built a working line-following robot, coded a simple AI model to recognise hand gestures, and presented his project to a visiting district official.

But here is what matters more than any of that: we have a report on Prajwal. A real, detailed, child-level progress report that tracks every module he completed, every skill he gained, every project he built. It is not a certificate. It is evidence.

This is what we mean when we say "impact, not activity." Every child in our program gets this level of attention. Every school gets quarterly reports. Every CSR partner gets audit-ready documentation that stands up to scrutiny.

Here are the Sangli reports if you would like to see the depth:
  Phase 1: """ + ASSETS_CSR[3]["report_sangli1"] + """
  Phase 2: """ + ASSETS_CSR[5]["report_sangli2"] + """

And the Veer Baji report:
  """ + ASSETS_CSR[5]["report_vbv"] + """

A short feature that aired on Star News Marathi:
  """ + ASSETS_CSR[5]["video_star"] + """

The full Sangli folder with photos, videos, and media coverage:
  """ + ASSETS_CSR[5]["folder_sangli"] + """

Latest session clip:
  """ + ASSETS_CSR[5]["video_ig"] + """

We deliver, and we always deliver. We do not let people down. When a CSR partner commits to us, they are not buying a workshop. They are investing in a year-long relationship where every rupee is accounted for and every child is tracked.

If you would like to see Prajwal's actual report — or any of our other student portfolios — just reply to this email. I would be happy to share.

Warmly,
Omkar
RoboPirate
www.robopirate.in | info@robopirate.in

P.S. — The per-student cost works out to under Rs.1,000 per year when spread across a 5-year program. That includes the lab, the trainer, the curriculum, the kits, the LMS, and the reports. I can share the full financial model if helpful."""
}

# ───────────────────────────────────────────────────────────────────────────────
# DAY 7 — The Invitation: Open the door, let them walk through
# ───────────────────────────────────────────────────────────────────────────────

CSR_PLAIN_TEXT_TEMPLATES["csr"][7] = {
    "subject": "{{COMPANY_NAME}} — A conversation, whenever you are ready",
    "body": """Dear {{CSR_HEAD_NAME}},

I have shared a lot over the past few emails — the Sangli story, the numbers, Prajwal's report, the media coverage. I hope it has given you a clear sense of who we are and what we do.

Now I want to step back and simply say: whenever you are ready, I would love to have a conversation. No presentation deck. No pressure. Just two people talking about whether there is a fit between what {{COMPANY_NAME}} wants to achieve and what we have already built.

Here is everything in one place, in case you would like to review or share internally:

  WE Smart Lab Overview & Plans:
    """ + ASSETS_CSR[7]["plans"] + """

  ABP Majha Feature:
    """ + ASSETS_CSR[7]["video_abp"] + """

  WSL Program Video:
    """ + ASSETS_CSR[7]["video_wsl"] + """

  Sangli District Video:
    """ + ASSETS_CSR[7]["video_sangli"] + """

  PMC Proposal PDF:
    """ + PDF_LINKS["pmc_proposal"] + """

  WSL Program PDF:
    """ + PDF_LINKS["wsl"] + """

  Subscription Details:
    """ + PDF_LINKS["subscription"] + """

  Latest session clip:
    """ + ASSETS_CSR[7]["video_ig"] + """

A few things worth knowing:

  • We are NEP 2020 and NCF-aligned. The curriculum maps directly to government standards.
  • We are Schedule VII compliant. Full tax deductibility under the Companies Act 2013.
  • We handle everything end-to-end: lab setup, trainer hiring, curriculum delivery, LMS, quarterly reports, and annual audits.
  • The school only needs to provide a classroom (~250 sq.ft.) with electricity. We do the rest.
  • Partial adoption is absolutely fine. Three schools, four schools, one school — we scale to what works for you.

We deliver, and we always deliver. We do not let people down. That is not a slogan. It is the reason we have 85+ labs running and partners who renew year after year.

If there is someone else at {{COMPANY_NAME}} who should see this — a colleague in sustainability, a foundation lead, a board member — please feel free to forward this along. I am happy to adapt the conversation to whoever is making the decision.

Warmly,
Omkar
RoboPirate
www.robopirate.in | info@robopirate.in | +91-9136899925

P.S. — I am based in Pune and happy to travel to your office for a 30-minute conversation whenever it is convenient. No pitch, just a walkthrough of what already exists."""
}

# ───────────────────────────────────────────────────────────────────────────────
# DAY 10 — The Story: Leave an imprint. Diplomat style. No persuasion, just presence.
# ───────────────────────────────────────────────────────────────────────────────

CSR_PLAIN_TEXT_TEMPLATES["csr"][10] = {
    "subject": "{{CSR_HEAD_NAME}}, a story I wanted to leave with you",
    "body": """Dear {{CSR_HEAD_NAME}},

This is my last email in this series. I promised myself I would not make it a sales pitch, so I will not.

Instead, I want to tell you a story.

Last year, I visited one of our government school labs in Sangli unannounced. I do that sometimes — just show up, sit in the back, and watch. The trainer was running a session on sensors. The children were maybe 10 or 11 years old. One boy, thin, quiet, sitting in the corner, was struggling with a circuit. The trainer walked over, knelt beside him, and they worked on it together for ten minutes. Then the boy connected the last wire, the LED blinked, and he looked up — not at the trainer, not at me — at the ceiling, with this expression of pure, quiet surprise.

I have seen that look before. In Pune. In Kalyan. In Varanasi. It is the look of a child who just realised they can build something that works. That they are not just recipients of education — they are makers.

That is why we do this. Not for the reports, though we write them. Not for the media coverage, though it comes. We do it for that look. Because once a child has it, they do not un-have it. It stays with them. It changes how they see themselves.

{{COMPANY_NAME}} has the resources to create that moment for hundreds of children. Maybe thousands. And if you choose to, I would be honoured to help make it happen. If you choose not to, I completely understand. This work will continue either way. We have 85+ labs running. We will have more next year.

But I wanted you to know what is possible. And I wanted you to know that if you ever decide to step into this, there is a team here that delivers — always — and never lets people down.

Here is our company profile, in case you would like to keep it on file:
  """ + ASSETS_CSR[10]["profile"] + """

And a look at the kits and equipment we install:
  """ + ASSETS_CSR[10]["kits"] + """

Latest session clip:
  """ + ASSETS_CSR[10]["video_ig"] + """

Thank you for reading these emails. Thank you for the work you do at {{COMPANY_NAME}}. And thank you for considering us, even if only for a moment.

With respect and warmth,
Omkar
RoboPirate
www.robopirate.in | info@robopirate.in | +91-9136899925

P.S. — If you ever want to visit one of our labs — Pune, Sangli, Kalyan, anywhere — just let me know. I will arrange it personally. No agenda. Just come and see."""
}


# ═══════════════════════════════════════════════════════════════════════════════
# CSR-WSL-5 SEQUENCE — Plain Text Templates (Co-Funded Pilot: Pay Year 1, Run 5)
# ═══════════════════════════════════════════════════════════════════════════════

ASSETS_CSR_WSL5 = {
    1: {
        "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view",
        "brochure": "https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view",
        "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/",
    },
    3: {
        "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view",
        "video_abp": "https://youtu.be/FJ2_W53WjmA",
        "video_star": "https://youtube.com/watch?v=iziKPBSfGKU",
        "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/",
    },
    5: {
        "video_wsl": "https://drive.google.com/file/d/1KPrC2IpdooxazGJiyVe79JgyWlJbOxzu/view",
        "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/",
    },
    7: {
        "brochure": "https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view",
        "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/",
    },
    10: {
        "profile": "https://drive.google.com/file/d/1g9JJ4_VO_28QKYD7iVVDJZcv9l4uRbZu/view",
        "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/",
    },
}

# ───────────────────────────────────────────────────────────────────────────────
# CSR-WSL-5 DAY 1 — The Hook: What if you only paid for Year 1?
# ───────────────────────────────────────────────────────────────────────────────

CSR_PLAIN_TEXT_TEMPLATES["csr-wsl-5"][1] = {
    "subject": "{{COMPANY_NAME}} — A 5-year STEM pilot where you fund only Year 1",
    "body": """Dear {{CSR_HEAD_NAME}},

I wanted to share an idea that has been working well for municipalities and CSR partners alike — and I think it might interest {{COMPANY_NAME}}.

What if your CSR budget covered only the first year of a STEM lab — the full setup, the trainer, the curriculum, everything — and the municipality took over from Year 2, after seeing measurable results?

That is the WE Smart Lab Co-Funded Pilot. It is designed so that the CSR partner carries zero long-term obligation, and the municipality commits only after they have seen the program work with their own students.

Here is how it looks:

  Year 1 (2026-27): Fully funded by CSR partner — Rs.12 Lakhs
    Complete lab build, full-time trainer, curriculum, LMS, quarterly reports

  Years 2-5 (2027-31): Funded by municipality — Rs.7 Lakhs per year
    Same scope, same trainer, same outcomes

  Total 5-year cost: Rs.40 Lakhs for 400 students
    That works out to under Rs.1,000 per student per year

  Exit clause: If Year 1 outcomes do not meet agreed benchmarks, the municipality can exit with 90 days' notice. No penalty. The hardware stays with the school.

The Veer Baji report from our Pune pilot shows what Year 1 looks like in practice:
  """ + ASSETS_CSR_WSL5[1]["report_vbv"] + """

And here is the full program overview:
  """ + ASSETS_CSR_WSL5[1]["brochure"] + """

Latest session clip:
  """ + ASSETS_CSR_WSL5[1]["video_ig"] + """

I am not asking for a commitment. I am simply sharing a model that has already been executed successfully — and that removes almost all the risk for both sides.

If you would like to see the financial model or the 90-day launch timeline, just reply to this email.

Warmly,
Omkar
RoboPirate
www.robopirate.in | info@robopirate.in

P.S. — We have done this before. We deliver, and we always deliver. We do not let people down."""
}

# ───────────────────────────────────────────────────────────────────────────────
# CSR-WSL-5 DAY 3 — The Proof: We already did this. Here is the evidence.
# ───────────────────────────────────────────────────────────────────────────────

CSR_PLAIN_TEXT_TEMPLATES["csr-wsl-5"][3] = {
    "subject": "{{CSR_HEAD_NAME}}, this model already worked — twice. Here is the evidence.",
    "body": """Dear {{CSR_HEAD_NAME}},

In my last email, I shared the Co-Funded Pilot concept. I know it sounds bold — CSR pays Year 1, municipality commits from Year 2 only after seeing results. So let me show you where it already happened.

Veer Baji Prabhu Vidyalaya, Pune:
  A government school with no prior STEM exposure. Cummins India funded Year 1 through their CSR. We delivered a full academic year program (2024-25), Grades 1-7, with a locally hired trainer who was trained and certified in-house by our team.

  The students moved from guided activities to independent builds. The CSR partner got an audit-ready, outcome-linked report. The school got a working lab. The community got a job.

  Report: """ + ASSETS_CSR_WSL5[3]["report_vbv"] + """

Sangli District Collector's Pilot:
  Initiated by Shri Ashok Kakade IAS. Two schools, including K.R.V. Mook-Badhir School for hearing-impaired students. If the model works there, it works anywhere.

  15-day intensive training. 11 sensors taught. 3D printing. 12 student projects. Public exhibition. Media coverage: ABP Majha, Star News Marathi.

  Video (ABP Majha): """ + ASSETS_CSR_WSL5[3]["video_abp"] + """
  Video (Star News): """ + ASSETS_CSR_WSL5[3]["video_star"] + """

We have 85+ CSR labs across 6 states. 55,000+ students. 1.5 lakh+ projects. This is not a first attempt.

Latest session clip:
  """ + ASSETS_CSR_WSL5[3]["video_ig"] + """

We deliver, and we always deliver. We do not let people down. When a district collector and a Fortune 500 company both put their names behind the same program, that is not luck. That is execution.

If you would like the full Veer Baji or Sangli reports, just let me know.

Warmly,
Omkar
RoboPirate
www.robopirate.in | info@robopirate.in

P.S. — Partial adoption is possible. Three schools, four schools, one school — we adapt to what works for your CSR budget and timeline."""
}

# ───────────────────────────────────────────────────────────────────────────────
# CSR-WSL-5 DAY 5 — The Job: What this CSR actually creates
# ───────────────────────────────────────────────────────────────────────────────

CSR_PLAIN_TEXT_TEMPLATES["csr-wsl-5"][5] = {
    "subject": "{{CSR_HEAD_NAME}}, the job your CSR creates — and the child it changes",
    "body": """Dear {{CSR_HEAD_NAME}},

I want to talk about something that does not always make it into the proposal deck: the job.

When {{COMPANY_NAME}} funds a WE Smart Lab, you are not just buying equipment and curriculum. You are creating a full-time job for a young person from an underprivileged background — someone who is trained by us, certified by us, and placed as a dedicated STEM trainer in a government school.

That trainer earns a full year's wage. They gain professional skills in robotics, AI, IoT, and 3D printing. They become a role model in their community. And they stay with the school for the entire academic year — not a visiting volunteer, but a permanent presence.

Over 5 years, that is 5 jobs created. Five families supported. Five young people who entered the workforce through STEM education instead of leaving it.

And then there are the children. Prajwal, whom I mentioned earlier, has a full child-level progress report tracking his journey from zero to building working robots. Every child in the program gets this. Every CSR partner gets the aggregated data.

Here is the WSL program video:
  """ + ASSETS_CSR_WSL5[5]["video_wsl"] + """

Latest session clip:
  """ + ASSETS_CSR_WSL5[5]["video_ig"] + """

We deliver, and we always deliver. We do not let people down. The trainer we place is not outsourced. They are ours. We train them, we manage them, we replace them if needed. The school never has to worry about staffing.

If you would like to see a sample trainer profile or a child progress report, just reply to this email.

Warmly,
Omkar
RoboPirate
www.robopirate.in | info@robopirate.in

P.S. — The Rs.12 Lakhs Year 1 cost includes everything: lab build, all kits and equipment, trainer salary and training, curriculum, LMS, quarterly reports, and annual audit. There are no hidden costs."""
}

# ───────────────────────────────────────────────────────────────────────────────
# CSR-WSL-5 DAY 7 — The Math: Rs.12L + Rs.28L = 400 students x 5 years
# ───────────────────────────────────────────────────────────────────────────────

CSR_PLAIN_TEXT_TEMPLATES["csr-wsl-5"][7] = {
    "subject": "{{COMPANY_NAME}} — The math: Rs.12L CSR + Rs.28L Government = 400 students x 5 years",
    "body": """Dear {{CSR_HEAD_NAME}},

Let me cut to the numbers, because every CSR head I speak to eventually asks the same question: what does this actually cost, and what do we get?

Here is the full 5-year structure:

  Year 1 (2026-27): CSR Partner — Rs.12,00,000
    Complete lab build + Year 1 operations + trainer + curriculum + reports

  Year 2 (2027-28): Municipality — Rs.7,00,000
    Annual subscription (trainer + curriculum + kit refresh)

  Year 3 (2028-29): Municipality — Rs.7,00,000
    Annual subscription

  Year 4 (2029-30): Municipality — Rs.7,00,000
    Annual subscription

  Year 5 (2030-31): Municipality — Rs.7,00,000
    Annual subscription + impact study + case report

  -------------------------------------------------
  5-Year Total: Rs.40,00,000 for 400 students
  Per student per year: Under Rs.1,000
  Standalone private rate: Rs.2,050 per student per year
  Savings vs. market: 51%
  -------------------------------------------------

What the municipality provides: A classroom (~250 sq.ft.) + electricity + connectivity.
What RoboPirate provides: Everything else — 198 items installed, 90 grade kits, 17 workshop kits, drone access, 3D printer, laptop, projector, safety gear, full-time trainer, curriculum, LMS, quarterly reports.

The exit protection: At the end of each year, a formal review checkpoint. If outcomes do not meet benchmarks, the municipality exits with 90 days' notice. No penalty. Hardware stays with the school.

Full program overview:
  """ + ASSETS_CSR_WSL5[7]["brochure"] + """

Latest session clip:
  """ + ASSETS_CSR_WSL5[7]["video_ig"] + """

This is not a donation. This is a structured, outcome-linked, 5-year partnership. The CSR partner gets Schedule VII compliance, tax deductibility, and quarterly impact reports. The municipality gets a running, measurable lab at zero Year 1 risk. The students get 5 years of continuous STEM progression.

We deliver, and we always deliver. We do not let people down.

If you would like a 30-minute walkthrough of this model — financials, timeline, and a live demo of the LMS — just reply with a time that works.

Warmly,
Omkar
RoboPirate
www.robopirate.in | info@robopirate.in | +91-9136899925

P.S. — The FY 2026-27 budget window is open now. A decision in the next few weeks lets us complete lab setup by monsoon and begin classes in the July academic session."""
}

# ───────────────────────────────────────────────────────────────────────────────
# CSR-WSL-5 DAY 10 — The Story: Leave an imprint. Diplomat style.
# ───────────────────────────────────────────────────────────────────────────────

CSR_PLAIN_TEXT_TEMPLATES["csr-wsl-5"][10] = {
    "subject": "{{CSR_HEAD_NAME}}, a story I wanted to leave with you",
    "body": """Dear {{CSR_HEAD_NAME}},

This is my last email. I promised myself it would not be a pitch, so I will keep that promise.

Instead, a story.

Last year I visited one of our labs unannounced. A government school in Sangli. The trainer was teaching sensors to a class of ten-year-olds. In the corner, a quiet boy was struggling with a circuit. The trainer knelt beside him. Ten minutes later, the boy connected the last wire. The LED blinked. He looked up at the ceiling with this expression of pure, quiet surprise — not at anyone, just at the fact that he had made something work.

I have seen that look in Pune. In Kalyan. In Varanasi. It is the look of a child who realises they are not just a student — they are a maker. And once they have that, they do not un-have it.

{{COMPANY_NAME}} has the resources to create that moment for hundreds of children. Maybe thousands. If you choose to, I would be honoured to help. If you choose not to, I understand completely. This work continues either way. We have 85+ labs. We will have more next year.

But I wanted you to know what is possible. And I wanted you to know that if you ever step into this, there is a team here that delivers — always — and never lets people down.

Here is our company profile:
  """ + ASSETS_CSR_WSL5[10]["profile"] + """

Latest session clip:
  """ + ASSETS_CSR_WSL5[10]["video_ig"] + """

Thank you for reading these emails. Thank you for the work you do. And thank you for considering us, even if only for a moment.

With respect and warmth,
Omkar
RoboPirate
www.robopirate.in | info@robopirate.in | +91-9136899925

P.S. — If you ever want to visit a lab — Pune, Sangli, anywhere — just let me know. I will arrange it personally. No agenda. Just come and see."""
}


# ═══════════════════════════════════════════════════════════════════════════════
# HTML-TO-PLAIN-TEXT CONVERSION UTILITY
# Converts existing HTML templates to plain text for fallback / mixed-mode sending
# ═══════════════════════════════════════════════════════════════════════════════

def html_to_plain_text(html_body: str) -> str:
    """
    Convert HTML email body to clean plain text.
    Handles: tags, entities, links, lists, tables, line breaks.
    """
    if not html_body:
        return ""

    text = html_body

    # Replace <br>, <br/>, <br /> with newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

    # Replace <p> with double newlines, </p> with single
    text = re.sub(r'<p\b[^>]*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '', text, flags=re.IGNORECASE)

    # Replace <li> with bullet
    text = re.sub(r'<li\b[^>]*>', '\n  • ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '', text, flags=re.IGNORECASE)

    # Replace <ul>, <ol> with nothing (bullets handle it)
    text = re.sub(r'</?ul\b[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?ol\b[^>]*>', '', text, flags=re.IGNORECASE)

    # Handle <a href="...">text</a> → text (URL)
    def link_replacer(m):
        href = m.group(1) or ""
        link_text = m.group(2) or ""
        # If link text is the URL or empty, just return the URL
        if not link_text.strip() or link_text.strip() == href.strip():
            return f"\n  {href}\n"
        return f"{link_text}\n  {href}\n"

    text = re.sub(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', link_replacer, text, flags=re.IGNORECASE | re.DOTALL)

    # Handle <strong>, <b>, <em>, <i> — strip tags but keep content
    text = re.sub(r'</?(strong|b|em|i|span|div|font)\b[^>]*>', '', text, flags=re.IGNORECASE)

    # Handle headings — add newlines
    text = re.sub(r'<h[1-6]\b[^>]*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</h[1-6]>', '\n', text, flags=re.IGNORECASE)

    # Handle table rows — simple conversion
    text = re.sub(r'<tr\b[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</tr>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<td\b[^>]*>', '  ', text, flags=re.IGNORECASE)
    text = re.sub(r'</td>', '  ', text, flags=re.IGNORECASE)
    text = re.sub(r'<th\b[^>]*>', '  ', text, flags=re.IGNORECASE)
    text = re.sub(r'</th>', '  ', text, flags=re.IGNORECASE)
    text = re.sub(r'</?table\b[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</?thead\b[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?tbody\b[^>]*>', '', text, flags=re.IGNORECASE)

    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities
    text = html.unescape(text)

    # Clean up excessive whitespace
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n[ \t]+', '\n', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE MIGRATION: Add plain_text_body column to templates table
# ═══════════════════════════════════════════════════════════════════════════════

def migrate_plain_text_column(db):
    """
    Add plain_text_body column to templates table if missing.
    Call this once during app startup.
    
    Args:
        db: Database instance (from db.py)
    """
    try:
        db.conn.execute("SELECT plain_text_body FROM templates LIMIT 1")
        print("[DB] plain_text_body column already exists")
    except Exception:
        print("[DB] Migrating: Adding plain_text_body to templates...")
        db.conn.execute("ALTER TABLE templates ADD COLUMN plain_text_body TEXT")
        db.conn.commit()
        print("[DB] Migration complete: plain_text_body added")

        # Auto-populate plain_text for existing CSR templates
        _backfill_plain_text(db)


def _backfill_plain_text(db):
    """Backfill plain_text_body for existing templates using html_to_plain_text."""
    from engine import SEQUENCES

    updated = 0
    for seq_id in ["csr", "csr-wsl-5"]:
        if seq_id not in SEQUENCES:
            continue
        for day in SEQUENCES[seq_id]["days"]:
            tmpl = db.template_get(seq_id, day)
            if tmpl and tmpl.get("html_body") and not tmpl.get("plain_text_body"):
                plain = html_to_plain_text(tmpl["html_body"])
                if plain:
                    db.conn.execute(
                        "UPDATE templates SET plain_text_body = ? WHERE sequence_id = ? AND day = ?",
                        (plain, seq_id, day)
                    )
                    updated += 1
    db.conn.commit()
    if updated:
        print(f"[DB] Backfilled plain_text_body for {updated} existing templates")


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE PUT WITH PLAIN TEXT — Wrapper for db.template_put
# ═══════════════════════════════════════════════════════════════════════════════

def template_put_with_plain_text(db, sequence_id, day, subject, html_body, source="synced",
                                   subject_b=None, ab_test=0, ab_split=0.5):
    """
    Save a template with both HTML and auto-generated plain text.
    Use this instead of db.template_put() when you want plain text support.
    """
    plain_text = html_to_plain_text(html_body)

    db.conn.execute("""
        INSERT INTO templates (sequence_id, day, subject, subject_b, html_body, plain_text_body, source, ab_test, ab_split)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(sequence_id, day) DO UPDATE SET
            subject=excluded.subject,
            subject_b=excluded.subject_b,
            html_body=excluded.html_body,
            plain_text_body=excluded.plain_text_body,
            source=excluded.source,
            ab_test=excluded.ab_test,
            ab_split=excluded.ab_split,
            cached_at=CURRENT_TIMESTAMP
    """, (sequence_id, day, subject, subject_b, html_body, plain_text, source, ab_test, ab_split))
    db.conn.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# ENGINE INTEGRATION: render_plain_text() method
# Adds plain text rendering capability to CampaignEngine
# ═══════════════════════════════════════════════════════════════════════════════

def render_plain_text(engine, seq_id: str, day: int, rec) -> tuple:
    """
    Render a plain text email for a recipient.
    Priority:
      1. Dedicated plain text template from CSR_PLAIN_TEXT_TEMPLATES
      2. plain_text_body column from DB
      3. Auto-convert from html_body
    
    Args:
        engine: CampaignEngine instance
        seq_id: Sequence ID ("csr", "csr-wsl-5", etc.)
        day: Day number (1, 3, 5, 7, 10)
        rec: Recipient dataclass instance
    
    Returns:
        (subject, plain_text_body, ab_variant) or (None, None, None)
    """
    import json

    # Priority 1: Dedicated plain text template
    if seq_id in CSR_PLAIN_TEXT_TEMPLATES and day in CSR_PLAIN_TEXT_TEMPLATES[seq_id]:
        tmpl = CSR_PLAIN_TEXT_TEMPLATES[seq_id][day]
        subj = tmpl["subject"]
        body = tmpl["body"]
        variant = None

        # Apply placeholders
        extra = json.loads(rec.extra_json or "{}")
        placeholders = {
            "{{PRINCIPAL_NAME}}": rec.name,
            "{{SCHOOL_NAME}}": rec.org,
            "{{CSR_HEAD_NAME}}": rec.name,
            "{{COMPANY_NAME}}": rec.org,
            "{{OPENING_LINE}}": extra.get("Opening Line", extra.get("opening_line", "")),
            "{{NAME}}": rec.name,
            "{{ORG}}": rec.org,
            "{{EMAIL}}": rec.email,
        }
        for ph, val in placeholders.items():
            subj = subj.replace(ph, str(val))
            body = body.replace(ph, str(val))

        return subj, body, variant

    # Priority 2: plain_text_body from DB
    tmpl = engine.db.template_get(seq_id, day)
    if not tmpl:
        return None, None, None

    subj = tmpl.get("subject") or ""
    variant = None
    if tmpl.get("ab_test"):
        variant = engine._ab_variant(rec.email, tmpl.get("ab_split", 0.5))
        subj = tmpl["subject"] if variant == "A" else (tmpl.get("subject_b") or tmpl["subject"])

    # Check for plain_text_body column
    try:
        row = engine.db.execute(
            "SELECT plain_text_body FROM templates WHERE sequence_id=? AND day=?",
            (seq_id, day)
        ).fetchone()
        plain_text = row[0] if row and row[0] else None
    except Exception:
        plain_text = None

    if plain_text:
        body = plain_text
    else:
        # Priority 3: Auto-convert from HTML
        body = html_to_plain_text(tmpl.get("html_body", ""))

    if not body or not body.strip():
        return None, None, None

    # Apply placeholders
    extra = json.loads(rec.extra_json or "{}")
    placeholders = {
        "{{PRINCIPAL_NAME}}": rec.name,
        "{{SCHOOL_NAME}}": rec.org,
        "{{CSR_HEAD_NAME}}": rec.name,
        "{{COMPANY_NAME}}": rec.org,
        "{{OPENING_LINE}}": extra.get("Opening Line", extra.get("opening_line", "")),
        "{{NAME}}": rec.name,
        "{{ORG}}": rec.org,
        "{{EMAIL}}": rec.email,
    }
    for ph, val in placeholders.items():
        subj = subj.replace(ph, str(val))
        body = body.replace(ph, str(val))

    return subj, body, variant


# ═══════════════════════════════════════════════════════════════════════════════
# GMAIL MULTIPART SEND — Send both HTML and plain text
# ═══════════════════════════════════════════════════════════════════════════════

def send_multipart_email(gmail_client, to: str, subject: str, html_body: str, plain_text_body: str,
                         thread_id=None):
    """
    Send a multipart email with both HTML and plain text parts.
    Falls back to HTML-only if plain text is empty.
    
    Args:
        gmail_client: GmailClient instance
        to: Recipient email address
        subject: Email subject
        html_body: HTML version of the email
        plain_text_body: Plain text version of the email
        thread_id: Optional Gmail thread ID for threading
    
    Returns:
        Gmail API send response dict
    """
    import base64
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    if not plain_text_body or not plain_text_body.strip():
        # Fallback to HTML-only
        return gmail_client.send_email(to, subject, html_body, thread_id)

    # Build multipart message
    msg = MIMEMultipart('alternative')
    msg['to'] = to
    msg['subject'] = subject
    if thread_id:
        msg['In-Reply-To'] = thread_id
        msg['References'] = thread_id

    # Attach plain text part first (recommended: text first, HTML second)
    part_text = MIMEText(plain_text_body, 'plain', 'utf-8')
    msg.attach(part_text)

    # Attach HTML part
    part_html = MIMEText(html_body, 'html', 'utf-8')
    msg.attach(part_html)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    body = {'raw': raw}
    if thread_id:
        body['threadId'] = thread_id

    return gmail_client.service.users().messages().send(userId='me', body=body).execute()


def draft_multipart_email(gmail_client, to: str, subject: str, html_body: str, plain_text_body: str):
    """
    Create a multipart Gmail draft with both HTML and plain text parts.
    """
    import base64
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    if not plain_text_body or not plain_text_body.strip():
        return gmail_client.draft_email(to, subject, html_body)

    msg = MIMEMultipart('alternative')
    msg['to'] = to
    msg['subject'] = subject

    part_text = MIMEText(plain_text_body, 'plain', 'utf-8')
    msg.attach(part_text)

    part_html = MIMEText(html_body, 'html', 'utf-8')
    msg.attach(part_html)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    return gmail_client.service.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()


def create_scheduled_multipart_draft(gmail_client, to: str, subject: str, html_body: str,
                                      plain_text_body: str, send_at_iso: str):
    """
    Create a scheduled multipart Gmail draft.
    Subject gets [RAJ-SCHEDULE:...] prefix for Apps Script processing.
    """
    import base64
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    scheduled_subject = f"[RAJ-SCHEDULE:{send_at_iso}] {subject}"

    msg = MIMEMultipart('alternative')
    msg['to'] = to
    msg['subject'] = scheduled_subject

    if plain_text_body and plain_text_body.strip():
        part_text = MIMEText(plain_text_body, 'plain', 'utf-8')
        msg.attach(part_text)

    part_html = MIMEText(html_body, 'html', 'utf-8')
    msg.attach(part_html)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    return gmail_client.service.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()


# ═══════════════════════════════════════════════════════════════════════════════
# ENGINE PATCH — Inject plain text methods into CampaignEngine
# ═══════════════════════════════════════════════════════════════════════════════

def inject_plain_text_into_engine(engine):
    """
    Inject plain text rendering and multipart sending into a CampaignEngine instance.
    Call this after creating the engine: inject_plain_text_into_engine(engine)
    
    This patches:
      - engine.render_plain_text(seq_id, day, rec)
      - engine.send_multipart(to, subject, html_body, plain_text_body, thread_id)
      - engine.draft_multipart(to, subject, html_body, plain_text_body)
      - engine.create_scheduled_multipart_draft(to, subject, html_body, plain_text_body, send_at_iso)
    """
    engine.render_plain_text = lambda seq_id, day, rec: render_plain_text(engine, seq_id, day, rec)
    engine.send_multipart = lambda to, subject, html_body, plain_text_body, thread_id=None: send_multipart_email(
        engine.gmail, to, subject, html_body, plain_text_body, thread_id
    )
    engine.draft_multipart = lambda to, subject, html_body, plain_text_body: draft_multipart_email(
        engine.gmail, to, subject, html_body, plain_text_body
    )
    engine.create_scheduled_multipart_draft = lambda to, subject, html_body, plain_text_body, send_at_iso: create_scheduled_multipart_draft(
        engine.gmail, to, subject, html_body, plain_text_body, send_at_iso
    )
    print("[PlainText] Injected plain text methods into CampaignEngine")


# ═══════════════════════════════════════════════════════════════════════════════
# SEED PLAIN TEXT TEMPLATES INTO DATABASE
# Call this once to populate the DB with dedicated plain text CSR templates
# ═══════════════════════════════════════════════════════════════════════════════

def seed_plain_text_templates(db):
    """
    Seed the database with dedicated plain text templates for CSR and CSR-WSL-5 sequences.
    This stores the plain text in the plain_text_body column.
    """
    migrate_plain_text_column(db)

    count = 0
    for seq_id in ["csr", "csr-wsl-5"]:
        if seq_id not in CSR_PLAIN_TEXT_TEMPLATES:
            continue
        for day, tmpl in CSR_PLAIN_TEXT_TEMPLATES[seq_id].items():
            # Get existing template to preserve HTML and other fields
            existing = db.template_get(seq_id, day)
            html_body = existing.get("html_body", "") if existing else ""
            subject = tmpl["subject"]
            plain_body = tmpl["body"]
            source = "plain_text_seeded"

            db.conn.execute("""
                INSERT INTO templates (sequence_id, day, subject, html_body, plain_text_body, source, ab_test, ab_split)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(sequence_id, day) DO UPDATE SET
                    plain_text_body=excluded.plain_text_body,
                    source=excluded.source,
                    cached_at=CURRENT_TIMESTAMP
            """, (seq_id, day, subject, html_body, plain_body, source, 0, 0.5))
            count += 1

    db.conn.commit()
    print(f"[PlainText] Seeded {count} plain text templates into database")
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK REFERENCE / TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  RoboPirate Raj — Plain Text CSR Email Templates")
    print("=" * 70)
    print()

    for seq_id in ["csr", "csr-wsl-5"]:
        print(f"\n{'='*70}")
        print(f"  Sequence: {seq_id.upper()}")
        print(f"{'='*70}")
        for day in [1, 3, 5, 7, 10]:
            tmpl = CSR_PLAIN_TEXT_TEMPLATES[seq_id].get(day)
            if tmpl:
                print(f"\n  Day {day}: {tmpl['subject']}")
                print(f"  Body length: {len(tmpl['body'])} chars")
                preview = tmpl['body'][:200].replace('\n', ' ')
                print(f"  Preview: {preview}...")
            else:
                print(f"\n  Day {day}: [MISSING]")

    print("\n" + "=" * 70)
    print("  HTML-to-Plain-Text Conversion Test")
    print("=" * 70)
    test_html = """
    <p>Dear <strong>{{CSR_HEAD_NAME}}</strong>,</p>
    <p>Here is a <a href="https://example.com">link</a> for you.</p>
    <ul>
        <li>Item one</li>
        <li>Item two</li>
    </ul>
    <p>Best,<br>Omkar</p>
    """
    converted = html_to_plain_text(test_html)
    print(f"\nInput HTML ({len(test_html)} chars):")
    print(test_html)
    print(f"\nOutput Plain Text ({len(converted)} chars):")
    print(converted)
    print("\n" + "=" * 70)
    print("  All systems ready. Import this module and call:")
    print("    migrate_plain_text_column(db)")
    print("    seed_plain_text_templates(db)")
    print("    inject_plain_text_into_engine(engine)")
    print("=" * 70)
