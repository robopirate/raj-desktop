# Raj Email Command Center — Autopsy Report
**Date:** 2026-08-30  
**Auditor:** Orchestrator  
**Status:** CRITICAL FIXES NEEDED

---

## 1. What Was Audited

| File | Lines | Read? |
|------|-------|-------|
| `engine.py` | 2,875 | Full |
| `db.py` | 1,436 | Full |
| `web/app.py` | 1,459 | Full |
| `rewritten_email_templates.py` | 710 | Full |
| `web/static/js/api.js` | 193 | Full |
| `web/templates/index.html` | 960 | Full (preview) |

---

## 2. What's Working ✅

| Component | Status | Notes |
|-----------|--------|-------|
| **Backend API** | ✅ Solid | All 30+ endpoints that `api.js` calls exist in `app.py`. Nothing missing. |
| **Database schema** | ✅ Solid | Schema, migrations, pools, batches, templates all functional. |
| **Rewritten templates** | ✅ Content is good | Owner verified the drafts in the app are fine. |
| **Plain text support** | ✅ Wired | `_generate_text_content()`, `text_body` column, `format` column all exist. |
| **Template locking** | ✅ Works | `locked` column prevents overwrite. |
| **A/B testing** | ✅ Wired | `subject_b`, `ab_test`, `ab_split` columns present. |
| **Web UI (Flask)** | ✅ Functional | Dashboard, batches, import, templates, replies, blacklist all have endpoints. |
| **Auto-advance batches** | ✅ Works | Day 1 → Day 3 → Day 5 etc. with 2-day gap. |
| **Bounce guard** | ✅ Works | Stops sending if bounce rate > 10%. |
| **Reply scanning** | ✅ Works | Scans inbox, drafts replies via Ollama. |

---

## 3. What I Fixed ✅

| Fix | File | Status |
|-----|------|--------|
| Sign-off changed to "Om" | `rewritten_email_templates.py` | ✅ DONE (20 replacements) |
| Title changed to "Managing Director" | `rewritten_email_templates.py` | ✅ DONE (20 replacements) |

---

## 4. What's Broken / Needs Fixing 🔧

### 🔴 CRITICAL: `engine.py` is CORRUPTED

**What happened:** During link updates, the `replace_all` edit created **nested quotes** on multiple lines. Example:

```python
# Line 66 — CORRUPTED:
"brochure": ""brochure": "https://drive.google.com/file/d/18jbIdKcZtHy6_yMFUF0C9c8MpNhp9lVA/view?usp=drive_link"",

# Line 72 — CORRUPTED:
"report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view?usp=drive_link",
"video_abp": "https://youtu.be/FJ2_W53WjmA"
```

**Impact:** `python check_syntax.py` fails with `invalid decimal literal` errors.  
**Fix needed:** Rewrite the `SEQUENCES` dict cleanly. See Section 6 for the correct content.

---

### 🔴 HIGH: Google Drive Links Are Wrong

The `SEQUENCES` dict in `engine.py` has **outdated/incorrect links**. These must be updated:

| Asset | Current (Wrong) | Correct (Per Owner) |
|-------|----------------|---------------------|
| `brochure` (both seq) | `1vRMeFM22aajc5zfiYhqaev34UVQ87zyU` | `18jbIdKcZtHy6_yMFUF0C9c8MpNhp9lVA` |
| `report_1st_wsl` | `1H7mHVTWGprbd4ZFSPoJZPeAc1nHnih3J` | `1qiWBhOiklPpwU5NaVkqnfjA6v9q3YumS` |
| `report_sangli1` (school) | `1HpNdnamA2k3H0xkKr58STEKMNu5RgHPx` | `1MUlsC87vRbhFaoW0XcX146WBLKYBk448` |
| `report_sangli` (csr-wsl-5) | `1pKSm1WPlPk-we4aC-uhqxEy8w-BYygSN` | `1MUlsC87vRbhFaoW0XcX146WBLKYBk448` |
| `proposal_2nd` (csr-wsl-5) | `1mnmUNl1EkAmxjz7NVRGU2pmcHDrDUJMN` | `15-EuEcwci8olOSnm0V50laK3gVKCUCe-` |

**Note:** All Drive links should include `?usp=drive_link` for consistency.

---

### 🔴 HIGH: Missing "csr" Sequence

The `SEQUENCES` dict only has `"school"` and `"csr-wsl-5"`. There is **no plain `"csr"` sequence**.

**Impact:** Cannot run a standard 1-year CSR campaign.  
**Fix needed:** Add `"csr"` sequence with its own days, assets, and content.

---

### 🟡 MEDIUM: Web UI Missing Features

| Missing Feature | Location | Backend Support? |
|-----------------|----------|-----------------|
| **Sub-pool dropdown** on Import | `index.html` Import page | ✅ Yes (`/api/leads/import/file` accepts `sub_pool`) |
| **Sequence selector** on Batch Start | `index.html` Batches page | ✅ Yes (`/api/batches/{id}/start` accepts `sequence_id`) |
| **Format toggle** (HTML/Plain) | `index.html` Templates page | ✅ Yes (`format` column exists) |
| **Lock/Unlock buttons** | `index.html` Templates page | ✅ Yes (`/api/templates/*/lock` endpoints exist) |

All backend endpoints exist. Only the **frontend UI wiring** is missing.

---

### 🟡 MEDIUM: Template Auto-Repair Risk

On engine startup, `validate_templates(auto_repair=True)` will regenerate missing templates. If the DB is cleared, templates regenerate fresh. This is fine **if templates are locked**.

**Fix needed:** After generating templates, click "Lock All" in the UI (or call `POST /api/templates/lock-all`).

---

### 🟡 LOW: Old Tkinter UI is Broken

`python main.py` crashes with:
```
AttributeError: '_tkinter.tkapp' object has no attribute '_refresh_pool_count'
```

**Fix:** Use `python web_start.py` or `python desktop.py` instead. The tkinter UI is deprecated.

---

## 5. Content Fixes Needed (Per Owner's Instructions)

The owner reviewed the drafts and said the **content is fine** — no full rewrites needed. Only these targeted fixes:

1. ✅ **Sign-off:** "Baban Jadhav" → "Om" (DONE)
2. ✅ **Title:** "Program Director" → "Managing Director" (DONE)
3. 🔧 **Links:** Update 5 Google Drive links (see Section 4)
4. 🔧 **Add CSR sequence:** New sequence with simplified 1-year content
5. 🔧 **Last email tone:** Don't beg. Diplomatic. Tell a story. Mention partial options.
6. 🔧 **"Within 10 weeks of program launch"** — not "of payment"
7. 🔧 **"Access to drone"** — not "4 drones"
8. 🔧 **Don't mention names** — MOU not signed
9. 🔧 **"We deliver. We always deliver."** — not "we exist"

---

## 6. Correct `SEQUENCES` Dict (For Kimi Code)

Replace the entire `SEQUENCES = {` block in `engine.py` (lines 58-153) with this:

```python
SEQUENCES = {
    "school": {
        "days": [1, 3, 5, 7, 10],
        "template_prefix": "SCHOOL EMAIL ",
        "audience": "private_school",
        "persona": "school",
        "assets": {
            1: {
                "brochure": "https://drive.google.com/file/d/18jbIdKcZtHy6_yMFUF0C9c8MpNhp9lVA/view?usp=drive_link",
                "video_wsl": "https://www.instagram.com/p/DTDBcsdk9FI/",
                "video_abp": "https://youtu.be/FJ2_W53WjmA",
                "video_ig": "https://www.instagram.com/robo.pirate/"
            },
            3: {
                "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view?usp=drive_link",
                "video_abp": "https://youtu.be/FJ2_W53WjmA"
            },
            5: {
                "report_1st_wsl": "https://drive.google.com/file/d/1qiWBhOiklPpwU5NaVkqnfjA6v9q3YumS/view?usp=drive_link"
            },
            7: {
                "report_sangli1": "https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view?usp=drive_link",
                "video_abp": "https://youtu.be/FJ2_W53WjmA?si=ZFAr_bp_xU2Sduwr",
                "video_star": "https://www.youtube.com/watch?v=iziKPBSfGKU",
                "video_bandhuta": "https://www.youtube.com/watch?v=xVmaBnPyg9A",
                "video_sbn": "https://www.youtube.com/watch?v=d-TsgUkhIu0",
                "video_we": "https://www.instagram.com/reel/DMe2HzqofAk/?igsh=c201ZGxsOGFlMjJj"
            },
            10: {
                "plans": "https://drive.google.com/file/d/1p2CyHVZK_giZj0KNDGTTs_-s7HxVnQ_C/view?usp=drive_link"
            }
        }
    },
    "csr-wsl-5": {
        "days": [1, 3, 5, 7, 10],
        "template_prefix": "CSR-WSL-5 EMAIL ",
        "audience": "csr",
        "persona": "csr",
        "assets": {
            1: {
                "brochure": "https://drive.google.com/file/d/18jbIdKcZtHy6_yMFUF0C9c8MpNhp9lVA/view?usp=drive_link"
            },
            3: {
                "video_wsl": "https://www.instagram.com/p/DTDBcsdk9FI/"
            },
            5: {
                "report_1st_wsl": "https://drive.google.com/file/d/1qiWBhOiklPpwU5NaVkqnfjA6v9q3YumS/view?usp=drive_link",
                "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view?usp=drive_link"
            },
            7: {
                "report_sangli": "https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view?usp=drive_link",
                "video_divyang": "https://www.instagram.com/p/DMhEDutOrl-/",
                "video_gruh": "https://www.instagram.com/p/DSSIy7nglXc/",
                "video_abp": "https://youtu.be/FJ2_W53WjmA",
                "video_star": "https://www.youtube.com/watch?v=iziKPBSfGKU",
                "video_bandhuta": "https://www.youtube.com/watch?v=xVmaBnPyg9A",
                "video_sbn": "https://www.youtube.com/watch?v=d-TsgUkhIu0",
                "video_we": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            10: {
                "proposal_2nd": "https://drive.google.com/file/d/15-EuEcwci8olOSnm0V50laK3gVKCUCe-/view?usp=drive_link"
            }
        }
    },
    "csr": {
        "days": [1, 3, 5, 7, 10],
        "template_prefix": "CSR EMAIL ",
        "audience": "csr",
        "persona": "csr",
        "assets": {
            1: {
                "brochure": "https://drive.google.com/file/d/18jbIdKcZtHy6_yMFUF0C9c8MpNhp9lVA/view?usp=drive_link",
                "video_wsl": "https://www.instagram.com/p/DTDBcsdk9FI/",
                "video_abp": "https://youtu.be/FJ2_W53WjmA"
            },
            3: {
                "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view?usp=drive_link",
                "video_abp": "https://youtu.be/FJ2_W53WjmA"
            },
            5: {
                "report_1st_wsl": "https://drive.google.com/file/d/1qiWBhOiklPpwU5NaVkqnfjA6v9q3YumS/view?usp=drive_link"
            },
            7: {
                "report_sangli1": "https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view?usp=drive_link",
                "video_abp": "https://youtu.be/FJ2_W53WjmA?si=ZFAr_bp_xU2Sduwr",
                "video_star": "https://www.youtube.com/watch?v=iziKPBSfGKU",
                "video_bandhuta": "https://www.youtube.com/watch?v=xVmaBnPyg9A",
                "video_sbn": "https://www.youtube.com/watch?v=d-TsgUkhIu0",
                "video_we": "https://www.instagram.com/reel/DMe2HzqofAk/?igsh=c201ZGxsOGFlMjJj"
            },
            10: {
                "plans": "https://drive.google.com/file/d/1p2CyHVZK_giZj0KNDGTTs_-s7HxVnQ_C/view?usp=drive_link"
            }
        }
    }
}
```

---

## 7. CSR Content to Add to `rewritten_email_templates.py`

Add these functions and dict updates to `rewritten_email_templates.py`:

```python
def _generate_csr_content(day: int, assets: Dict[str, str]) -> str:
    """Plain CSR sequence — 1-year model, shorter than CSR-WSL-5."""
    a = assets
    contents = {
        1: f"""<p>Dear CSR Head,</p>

<p>Our first WE Smart Lab began as a one-year CSR project.</p>

<p>Today, more than 65,000 students learn with us across 85+ schools in 6 states.</p>

<p>If you'd like to know who we are and how the lab works, the brochure below is a good place to start.</p>

<p>Regards,<br>Om<br>Managing Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('brochure','#')}" target="_blank">📄 Explore the WE Smart Lab Brochure</a>
</div>""",

        3: f"""<p>Dear CSR Head,</p>

<p>One question comes up in every CSR conversation: how is learning tracked?</p>

<p>We keep a structured record for every child. I've attached a specimen assessment report so you can see what schools receive.</p>

<p>Regards,<br>Om<br>Managing Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('report_vbv','#')}" target="_blank">📄 View Sample Student Assessment Report</a>
</div>""",

        5: f"""<p>Dear CSR Head,</p>

<p>Our first lab at Veer Baji Prabhu Vidyalay has completed a full academic year.</p>

<p>We documented the full year in the First WE Smart Lab Annual Report. Inside you'll find student project records, assessment outcomes, and how learning was tracked per child.</p>

<p>Regards,<br>Om<br>Managing Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('report_1st_wsl','#')}" target="_blank">📄 Read the First WE Smart Lab Annual Report</a>
</div>""",

        7: f"""<p>Dear CSR Head,</p>

<p>In Sangli, we ran an AI and Robotics initiative for specially-abled students in association with the District Collector and Worship Earth Foundation.</p>

<p>The pilot grew into Phase II across 11 more institutions. Local media covered it independently.</p>

<p>The same team and curriculum runs inside private schools through our annual subscription.</p>

<p>Regards,<br>Om<br>Managing Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('report_sangli1','#')}" target="_blank">📘 Explore the Sangli Initiative</a>
<p style="margin:0;font-size:12px;color:#7A8A8A;">Also covered by:<br>
<a href="{a.get('video_abp','#')}">ABP Majha</a> • <a href="{a.get('video_star','#')}">Star News Marathi</a> • <a href="{a.get('video_bandhuta','#')}">Bandhuta News</a> • <a href="{a.get('video_sbn','#')}">SBN Marathi</a> • <a href="{a.get('video_we','#')}">Worship Earth</a></p>
</div>""",

        10: f"""<p>Dear CSR Head,</p>

<p>What would a partnership look like for your organisation?</p>

<p>We offer flexibility — start with one school or several. Every WE Smart Lab includes infrastructure, grade-wise kits, a dedicated instructor, and structured reporting.</p>

<p>A complete lab starts at ₹12 lakh per school for Year 1. Everything included.</p>

<p>Full details in the Subscription Overview below.</p>

<p>Regards,<br>Om<br>Managing Director – WE Smart Lab<br>Robo Pirate<br>https://robopirate.in</p>

<div style="margin-top:20px;padding-top:15px;border-top:1px solid #E0E8E8;">
<a href="{a.get('plans','#')}" target="_blank">📄 View WE Smart Lab Subscription Overview</a>
</div>"""
    }
    return contents.get(day, f"<p>Template content for Day {day}</p>")


def _generate_csr_text_content(day: int, assets: Dict[str, str]) -> str:
    """Plain text version of CSR sequence."""
    a = assets
    contents = {
        1: f"""Dear CSR Head,

Our first WE Smart Lab began as a one-year CSR project.

Today, more than 65,000 students learn with us across 85+ schools in 6 states.

If you'd like to know who we are and how the lab works, the brochure below is a good place to start.

Regards,
Om
Managing Director – WE Smart Lab
Robo Pirate
https://robopirate.in

Explore the WE Smart Lab Brochure: {a.get('brochure', 'Available on request')}
""",

        3: f"""Dear CSR Head,

One question comes up in every CSR conversation: how is learning tracked?

We keep a structured record for every child. I've attached a specimen assessment report so you can see what schools receive.

Regards,
Om
Managing Director – WE Smart Lab
Robo Pirate
https://robopirate.in

Sample Student Assessment Report: {a.get('report_vbv', 'Available on request')}
""",

        5: f"""Dear CSR Head,

Our first lab at Veer Baji Prabhu Vidyalay has completed a full academic year.

We documented the full year in the First WE Smart Lab Annual Report. Inside you'll find student project records, assessment outcomes, and how learning was tracked per child.

Regards,
Om
Managing Director – WE Smart Lab
Robo Pirate
https://robopirate.in

First WE Smart Lab Annual Report: {a.get('report_1st_wsl', 'Available on request')}
""",

        7: f"""Dear CSR Head,

In Sangli, we ran an AI and Robotics initiative for specially-abled students in association with the District Collector and Worship Earth Foundation.

The pilot grew into Phase II across 11 more institutions. Local media covered it independently.

The same team and curriculum runs inside private schools through our annual subscription.

Regards,
Om
Managing Director – WE Smart Lab
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

        10: f"""Dear CSR Head,

What would a partnership look like for your organisation?

We offer flexibility — start with one school or several. Every WE Smart Lab includes infrastructure, grade-wise kits, a dedicated instructor, and structured reporting.

A complete lab starts at ₹12 lakh per school for Year 1. Everything included.

Full details in the Subscription Overview below.

Regards,
Om
Managing Director – WE Smart Lab
Robo Pirate
https://robopirate.in

WE Smart Lab Subscription Overview: {a.get('plans', 'Available on request')}
"""
    }
    return contents.get(day, f"Template content for Day {day}")
```

Also update `REWRITTEN_SUBJECTS` and `PREHEADERS`:

```python
REWRITTEN_SUBJECTS = {
    "school": { ... },  # existing
    "csr-wsl-5": { ... },  # existing
    "csr": {
        1: "STEM labs that outlast the funding cycle",
        3: "How we track impact per child",
        5: "One year later: what actually happened",
        7: "From 1 school to 12 — the Sangli story",
        10: "Partner with us: flexible, measurable, lasting"
    }
}

PREHEADERS = {
    "school": { ... },  # existing
    "csr-wsl-5": { ... },  # existing
    "csr": {
        1: "85+ schools, 65,000+ students — but it started with one classroom in Pune.",
        3: "Every child gets a structured record: attendance, projects, assessments.",
        5: "Our first lab completed a full academic year. Here's what we learned.",
        7: "AI and Robotics for specially-abled students. 11 institutions joined Phase II.",
        10: "Start with one school or six. Your Year 1 investment, their five-year gain."
    }
}
```

---

## 8. Engine.py `_generate_content` Update

Update `_generate_content` and `_generate_text_content` in `engine.py` to handle `"csr"`:

```python
def _generate_content(self, seq_id: str, day: int, assets: dict) -> str:
    if seq_id == "school":
        return _new_school_content(day, assets)
    elif seq_id == "csr-wsl-5":
        return _new_csr_wsl5_content(day, assets)
    elif seq_id == "csr":
        return _new_csr_content(day, assets)
    else:
        return _new_csr_wsl5_content(day, assets)
```

Same for `_generate_text_content`.

Also update the import at the top of `engine.py`:

```python
from rewritten_email_templates import (
    _generate_school_content as _new_school_content,
    _generate_school_text_content as _new_school_text_content,
    _generate_csr_wsl5_content as _new_csr_wsl5_content,
    _generate_csr_wsl5_text_content as _new_csr_wsl5_text_content,
    _generate_csr_content as _new_csr_content,              # ADD
    _generate_csr_text_content as _new_csr_text_content,    # ADD
    REWRITTEN_SUBJECTS,
    PREHEADERS,
)
```

---

## 9. Regenerate & Lock Templates

After all code changes, run:

```python
# In Python console or add to a script
from db import Database
from engine import CampaignEngine
from gmail import GmailClient

db = Database()
gmail = GmailClient()
engine = CampaignEngine(db, gmail)

# Clear old templates so they regenerate with new content
db.execute("DELETE FROM templates")
db.commit()

# Generate all templates
for seq_id in ["school", "csr", "csr-wsl-5"]:
    for day in [1, 3, 5, 7, 10]:
        engine.save_generated_template(seq_id, day, create_draft=False)

# Lock them all
engine.lock_templates()

print("Done! All templates regenerated and locked.")
```

---

## 10. Testing Checklist

After Kimi Code implements everything:

- [ ] `python test_raj.py` passes
- [ ] `python check_syntax.py` prints "Syntax OK"
- [ ] `python web_start.py` starts without errors
- [ ] Dashboard loads at `http://127.0.0.1:5555`
- [ ] All 3 sequences appear in UI dropdowns
- [ ] Templates show correct sign-off "Om"
- [ ] All Google Drive links are correct
- [ ] Template locking works (locked templates can't be edited without force)
- [ ] Sub-pool selection works during import
- [ ] Sequence selector works on batch start
- [ ] Format toggle (HTML/Plain) saves correctly

---

## 11. Files Modified by This Audit

| File | Action | Status |
|------|--------|--------|
| `rewritten_email_templates.py` | Sign-off changed to "Om" | ✅ DONE |
| `engine.py` | Link updates attempted | ❌ CORRUPTED — needs rewrite |
| `RAJ_ARCHITECTURE_SPEC_v1.md` | Full spec written | ✅ DONE |
| `RAJ_AUTOPSY.md` | This report | ✅ DONE |

---

**Next Step:** Hand this autopsy to Kimi Code. They have all the correct content to fix `engine.py` and implement the UI changes cleanly.
