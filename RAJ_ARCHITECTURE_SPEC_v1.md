# Raj Email Command Center — Architecture & Implementation Spec v1.0

**Date:** 2026-08-30  
**Project:** Raj Desktop v5.0 — Web UI + Template Overhaul  
**Author:** Orchestrator  
**Target Implementer:** Kimi Code (VS Code)

---

## 1. Executive Summary

This spec covers a **complete template overhaul + UI polish** for the Raj Email Command Center. The backend (Flask API, DB, engine) is functional and stable. The focus is:

1. **Fix all 10 email templates** (sign-off, links, tone, copy, placeholders)
2. **Add a 3rd sequence** (plain CSR, not just CSR-WSL-5)
3. **Fix the web UI** (pool selection, format toggle, sequence assignment)
4. **Add Plain Text campaign mode** (higher reply rates for B2B outreach)
5. **Protect templates from auto-overwrite**

---

## 2. Phase 1: Template Content Overhaul (CRITICAL)

### 2.1 File: `rewritten_email_templates.py`

This file contains the **source of truth** for all email content. It defines:
- `_generate_school_content(day, assets)` — HTML version
- `_generate_school_text_content(day, assets)` — Plain text version
- `_generate_csr_wsl5_content(day, assets)` — HTML version
- `_generate_csr_wsl5_text_content(day, assets)` — Plain text version
- `REWRITTEN_SUBJECTS` — Subject lines
- `PREHEADERS` — Inbox preview text

### 2.2 Universal Changes (All Sequences)

#### A. Sign-off Change
**Every** email currently signs off as:
```
Regards,
Baban Jadhav
Program Director – WE Smart Lab
Robo Pirate
https://robopirate.in
```

**Replace with:**
```
Regards,
Om
Managing Director – WE Smart Lab
Robo Pirate
https://robopirate.in
```
```
Regards,
Om
Managing Director – WE Smart Lab
Robo Pirate
https://robopirate.in
```

This applies to **all 20 instances** (10 HTML + 10 plain text).

#### B. Tone Directive (Owner's Instructions)
The owner has specified these tone rules that must be reflected in the templates:

1. **Don't beg for money.** Be diplomatic, not persuasive. "Ask for money but show the cause."
2. **Don't use corporate buzzwords** like "branded photo." Use "program launch" instead of "payment."
3. **Don't talk about what "could exist"** — talk about what **we deliver**. "We deliver and we always deliver. We don't let people down."
4. **Be sugar-coated but logical and genuine.** "If you say 4, you give 4."
5. **Last email should tell a story,** not push for a sale. Leave an imprint.
6. **They can take partial** — 3 schools, 4 schools, etc. Mention flexibility.
7. **Don't mention names** (MOU not signed). Mention the project, not individuals.
8. **"Access to 4 drones" is vague.** Just say "drone access" or don't specify numbers.
9. **Small logo,** not big. (Handled in HTML_TEMPLATE in engine.py — already small)
10. **Sign off as "Omkar"** (done above).

#### C. Link Updates

The `SEQUENCES` dict in `engine.py` provides `assets` dict to these template functions. Update the following asset links in `engine.py`:

| Asset Key | Current Link | New Link |
|-----------|-------------|----------|
| `brochure` | `https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view` | `https://drive.google.com/file/d/18jbIdKcZtHy6_yMFUF0C9c8MpNhp9lVA/view?usp=drive_link` |
| `report_1st_wsl` | `https://drive.google.com/file/d/1H7mHVTWGprbd4ZFSPoJZPeAc1nHnih3J/view` | `https://drive.google.com/file/d/1qiWBhOiklPpwU5NaVkqnfjA6v9q3YumS/view?usp=drive_link` |
| `report_sangli1` (school) | `https://drive.google.com/file/d/1HpNdnamA2k3H0xkKr58STEKMNu5RgHPx/view` | `https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view?usp=drive_link` |
| `report_sangli` (csr-wsl-5) | `https://drive.google.com/file/d/1pKSm1WPlPk-we4aC-uhqxEy8w-BYygSN/view` | `https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view?usp=drive_link` |
| `proposal_2nd` | `https://drive.google.com/file/d/1mnmUNl1EkAmxjz7NVRGU2pmcHDrDUJMN/view` | `https://drive.google.com/file/d/15-EuEcwci8olOSnm0V50laK3gVKCUCe-/view?usp=drive_link` |
| `plans` | `https://drive.google.com/file/d/1p2CyHVZK_giZj0KNDGTTs_-s7HxVnQ_C/view` | `https://drive.google.com/file/d/1p2CyHVZK_giZj0KNDGTTs_-s7HxVnQ_C/view?usp=drive_link` |

**Note:** The `plans` link stays the same but add `?usp=drive_link` for consistency.

**New assets to add for CSR-WSL-5 Day 7:**
- `report_vbv` = `https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view?usp=drive_link` (specimen report — Prajwal)

#### D. Instagram Links (Verify These Are Correct)

Current links in `SEQUENCES` — **verify with owner before changing:**
- `video_wsl` = `https://www.instagram.com/p/DTDBcsdk9FI/` (Veer Baji 2nd workshop)
- `video_divyang` = `https://www.instagram.com/p/DMhEDutOrl-/` (Sangli Divyang 1st workshop)
- `video_gruh` = `https://www.instagram.com/p/DSSIy7nglXc/` (Baalgruh)
- `video_we` = `https://www.instagram.com/reel/DMe2HzqofAk/` (Worship Earth)

**Owner correction:** The Veer Baji link is the **first** WSL video, not 2nd workshop. But the current link `DTDBcsdk9FI` is what the owner provided for "veer baji 2nd workshop of sangli." Keep as-is unless owner confirms otherwise.

---

### 2.3 SCHOOL Sequence (5 emails: Day 1, 3, 5, 7, 10)

#### Day 1 — Introduction + Brochure
- **Subject:** `{{SCHOOL_NAME}} — a classroom I couldn't stop thinking about`
- **Current issues:** None major. Keep the opening story about visiting 3 schools.
- **CTA:** Watch WSL video + Brochure + ABP Coverage
- **Assets used:** `brochure`, `video_wsl`, `video_abp`, `video_ig`

#### Day 3 — NEP Fit + Assessment Report
- **Subject:** `So how does WE Smart Lab fit with NEP?`
- **Current issues:** None major.
- **CTA:** View Specimen Assessment Report (Prajwal)
- **Assets used:** `report_vbv`, `video_abp`
- **Note:** Mention that Prajwal is a specimen character — "this is the kind of report we develop for every child."

#### Day 5 — First WSL Annual Report
- **Subject:** `What a full academic year taught us`
- **Current issues:** None major.
- **CTA:** Read First WSL Annual Report
- **Assets used:** `report_1st_wsl`

#### Day 7 — Sangli Initiative + Media Coverage
- **Subject:** `When the work spoke for itself in Sangli`
- **Current issues:** 
  - Add the Sangli report PDF link
  - Add ALL news coverage links (ABP, Star, Bandhuta, SBN, Worship Earth)
- **Assets used:** `report_sangli1`, `video_abp`, `video_star`, `video_bandhuta`, `video_sbn`, `video_we`

#### Day 10 — Pricing + Subscription Overview
- **Subject:** `What bringing WE Smart Lab to {{SCHOOL_NAME}} would involve`
- **Current issues:**
  - Remove "branded photo" language. Use "program launch" instead of "payment."
  - Don't be pushy. Frame as "here's what it would take" not "buy now."
  - Mention flexibility: "We can start with a single wing or grade and expand."
- **Assets used:** `plans`

---

### 2.4 CSR-WSL-5 Sequence (5 emails: Day 1, 3, 5, 7, 10)

#### Day 1 — Introduction + Brochure
- **Subject:** `What happens after Year 1?`
- **Current issues:** None major.
- **CTA:** Explore WE Smart Lab Brochure
- **Assets used:** `brochure`

#### Day 3 — First Lab Video
- **Subject:** `Looking back at where it began`
- **Current issues:** None major.
- **CTA:** Watch First WSL Video
- **Assets used:** `video_wsl`

#### Day 5 — Year 1 Story + Transparency Report
- **Subject:** `What we discovered after Year 1`
- **Current issues:** 
  - Add both 1st WSL PDF and VBV/Transparency Report
- **Assets used:** `report_1st_wsl`, `report_vbv`

#### Day 7 — Sangli Scale + Divyang + Employment + Media
- **Subject:** `When the work grew beyond one school`
- **Current issues:**
  - Add Sangli report
  - Add ALL Instagram reels and news coverage
  - Mention employment creation (₹9-12 lakh per school)
  - **Tag the specimen report** (Prajwal) — "this is the kind of per-child tracking we do"
- **Assets used:** `report_sangli`, `video_divyang`, `video_gruh`, `video_abp`, `video_star`, `video_bandhuta`, `video_sbn`, `video_we`, `report_vbv`

#### Day 10 — Partnership Proposal
- **Subject:** `An invitation to partner`
- **Current issues:**
  - Don't be persuasive. Tell the story. Changes you're making.
  - Mention 2nd stage of Sangli expansion
  - Mention partial options ("start with 1 school or 6")
  - Add implementation partner details (Worship Earth Foundation)
  - Remove vague "4 drone access" — just say "drone access"
- **Assets used:** `proposal_2nd`

---

### 2.5 NEW: Plain CSR Sequence (5 emails: Day 1, 3, 5, 7, 10)

**Purpose:** For CSR heads who want a standard 1-year model (not the 5-year co-funded model).

**Persona:** `"csr"` (formal, impact-focused, shorter than WSL-5)

**Template prefix:** `"CSR EMAIL "`

**Assets:**
- Day 1: `brochure`, `video_wsl`, `video_abp`
- Day 3: `report_vbv`, `video_abp`
- Day 5: `report_1st_wsl`
- Day 7: `report_sangli1`, `video_abp`, `video_star`, `video_bandhuta`, `video_sbn`, `video_we`
- Day 10: `plans`

**Content strategy:** Similar to school sequence but addressed to CSR heads. Focus on:
- Day 1: Who we are + brochure
- Day 3: Impact tracking + specimen report
- Day 5: First WSL annual report
- Day 7: Sangli scale + media
- Day 10: Partnership options (1-year, flexible school count)

**Subject lines:**
```python
"csr": {
    1: "STEM labs that outlast the funding cycle",
    3: "How we track impact per child",
    5: "One year later: what actually happened",
    7: "From 1 school to 12 — the Sangli story",
    10: "Partner with us: flexible, measurable, lasting"
}
```

**Preheaders:**
```python
"csr": {
    1: "85+ schools, 65,000+ students — but it started with one classroom in Pune.",
    3: "Every child gets a structured record: attendance, projects, assessments.",
    5: "Our first lab completed a full academic year. Here's what we learned.",
    6: "AI and Robotics for specially-abled students. 11 institutions joined Phase II.",
    10: "Start with one school or six. Your Year 1 investment, their five-year gain."
}
```

---

## 3. Phase 2: Engine Fixes

### 3.1 File: `engine.py`

#### A. Add CSR Sequence to SEQUENCES Dict

After the existing `"csr-wsl-5"` entry, add:

```python
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
```

#### B. Update Existing Links (School and CSR-WSL-5)

Update these keys inside the existing `"school"` and `"csr-wsl-5"` asset dicts:

**In `"school"`:**
- `brochure` → new link
- `report_1st_wsl` → new link
- `report_sangli1` → new link

**In `"csr-wsl-5"`:**
- `brochure` → new link
- `report_1st_wsl` → new link
- `report_sangli` → new link
- `proposal_2nd` → new link

#### C. Update `_generate_content` and `_generate_text_content`

Add handling for `"csr"` sequence:

```python
def _generate_content(self, seq_id: str, day: int, assets: dict) -> str:
    if seq_id == "school":
        return _new_school_content(day, assets)
    elif seq_id == "csr-wsl-5":
        return _new_csr_wsl5_content(day, assets)
    elif seq_id == "csr":
        return _new_csr_content(day, assets)  # NEW function needed
    else:
        return _new_csr_wsl5_content(day, assets)
```

Same for `_generate_text_content`.

**Note:** `_new_csr_content` and `_new_csr_text_content` need to be added to `rewritten_email_templates.py`.

#### D. Update `_generate_subject` for CSR

Add CSR subjects:

```python
def _generate_subject(self, seq_id: str, day: int) -> str:
    if REWRITTEN_TEMPLATES_AVAILABLE and seq_id in REWRITTEN_SUBJECTS:
        return REWRITTEN_SUBJECTS[seq_id].get(day, f"RoboPirate {seq_id.upper()} - Day {day}")
    # ... existing fallback subjects ...
```

Also add `REWRITTEN_SUBJECTS["csr"]` and `PREHEADERS["csr"]` to `rewritten_email_templates.py`.

#### E. Template Auto-Repair Guard

In `engine.start()` (around line 358), the `validate_templates(auto_repair=True)` will regenerate templates if missing. After we update the templates, we must **lock them** so auto-repair doesn't overwrite.

**Add after template validation in `start()`:**

```python
# Lock all templates after first successful generation to prevent overwrite
self.lock_templates()
```

**OR** change the validation logic to respect the source:
- If a template has `source='rewritten'`, never auto-repair it.
- Only auto-repair templates with `source='generated'` or `source='unknown'`.

**Preferred approach:** Add a check in `validate_templates()`:

```python
if tmpl and tmpl.get("source") == "rewritten":
    details.append({"seq_id": sid, "day": day, "status": "ok-locked"})
    continue
```

And in `save_generated_template()`, set `source="rewritten"` when saving from rewritten templates.

---

## 4. Phase 3: Web UI Improvements

### 4.1 File: `web/templates/index.html`

#### A. Import Page — Add Sub-Pool Dropdown

In the Import page section, add a **Sub-Pool selector** dropdown:

```html
<select id="import-sub-pool" class="input">
    <option value="">(No tag — generic pool)</option>
    <option value="school">School Leads</option>
    <option value="csr">CSR Leads</option>
    <option value="csr-wsl-5">CSR-WSL-5 Leads</option>
</select>
```

This value gets sent as `sub_pool` in the `/api/leads/import/file` and `/api/leads/import/paste` requests.

#### B. Batches Page — Sequence Selector on Start

When clicking "Start" on a batch, show a **Sequence selector** if the batch has `sequence_id="unassigned"`:

```html
<select id="batch-sequence-select">
    <option value="school">SCHOOL — Private Schools</option>
    <option value="csr">CSR — Standard CSR (1-year)</option>
    <option value="csr-wsl-5">CSR-WSL-5 — Co-funded 5-year model</option>
</select>
```

This gets sent as `sequence_id` in the `/api/batches/{id}/start` POST body.

#### C. Templates Page — Format Toggle (HTML / Plain Text)

In the template editor, add a **Format selector**:

```html
<select id="template-format">
    <option value="html">HTML (rich formatting)</option>
    <option value="plain">Plain Text (simple, personal)</option>
</select>
```

When `format="plain"`:
- The HTML preview iframe is hidden
- A plain text preview `<pre>` block is shown
- The `text_body` field is the primary editor
- `html_body` is auto-generated from text via `html_to_text()` (or `_text_to_simple_html`)

When saving via PUT `/api/templates/{seq}/{day}`, include `format` in the body.

#### D. Templates Page — Lock/Unlock Buttons

Add buttons next to each template:
- **Lock** → POST `/api/templates/{seq}/{day}/lock`
- **Unlock** → DELETE `/api/templates/{seq}/{day}/lock`
- **Lock All** → POST `/api/templates/lock-all`

Show a 🔒 icon when locked. Disable editing on locked templates (or show a "Force Edit" checkbox).

### 4.2 File: `web/static/js/api.js`

Already has all the endpoints. No changes needed.

### 4.3 File: `web/static/js/app.js`, `batches.js`, `import.js`, `templates.js`

Update these to wire the new UI elements to the API calls.

---

## 5. Phase 4: Plain Text Campaign Mode

### 5.1 Background

Research shows:
- **Plain text emails** have higher reply rates for B2B outreach (feel personal, not marketing)
- **HTML emails** have higher click-through rates (buttons, images, tracking)
- Best practice: Offer both. Let the user choose per campaign.

### 5.2 Implementation

The backend already supports `format` (html/plain). What's missing is:

1. **Generate plain text for all templates** — `rewritten_email_templates.py` already has `_generate_*_text_content()` functions. Use them.

2. **UI toggle** — When creating a batch or starting a campaign, offer:
   - "HTML Campaign" (rich, branded, tracked)
   - "Plain Text Campaign" (personal, simple, higher reply rate)

3. **Store format preference** — Save `preferred_format` in batch or campaign settings.

4. **Render respects format** — `render()` already returns `fmt`. Ensure it reads from the template's `format` column.

### 5.3 Plain Text Template Style

When `format="plain"`:
- No HTML wrapper (no logo, no colored buttons)
- Links written as: `Label: https://...`
- Simple greeting: `Dear {First Name},`
- Paragraphs separated by blank lines
- Sign-off with `--` separator

Example:
```
Dear Rahul,

Last week I visited three schools...

Watch a WE Smart Lab in Action: https://instagram.com/...

--
Om
Managing Director – WE Smart Lab
Robo Pirate
https://robopirate.in
```

---

## 6. Files to Modify

| File | Changes |
|------|---------|
| `rewritten_email_templates.py` | Sign-off "Om", add CSR sequence content + subjects + preheaders, tone fixes per owner instructions |
| `engine.py` | Update SEQUENCES dict (links + add "csr"), update `_generate_content`/`_generate_text_content`, add source guard in `validate_templates` |
| `web/templates/index.html` | Add sub-pool dropdown, sequence selector, format toggle, lock buttons |
| `web/static/js/import.js` | Wire sub-pool dropdown to API |
| `web/static/js/batches.js` | Wire sequence selector to start batch API |
| `web/static/js/templates.js` | Wire format toggle, lock/unlock buttons |
| `web/static/css/main.css` | Style for new dropdowns and toggles |

---

## 7. Testing Checklist

After implementation, verify:

- [ ] All 15 templates (3 sequences × 5 days) render without error
- [ ] Sign-off says "Om" in all 30 versions (HTML + text)
- [ ] All Google Drive links open correctly
- [ ] `REWRITTEN_TEMPLATES_AVAILABLE` is `True` on startup
- [ ] Template locking prevents auto-overwrite
- [ ] Sub-pool selection during import tags leads correctly
- [ ] Batch start with sequence assignment works
- [ ] Format toggle (HTML/Plain) saves and renders correctly
- [ ] CSR sequence appears in UI dropdowns
- [ ] `python test_raj.py` passes all tests
- [ ] Flask server starts without errors
- [ ] Dashboard loads real data

---

## 8. Migration Notes

### For Existing Users (You)

1. **Back up your DB** before updating:
   ```bash
   python -c "import shutil; shutil.copy('campaign_data.db', 'campaign_data.db.backup')"
   ```

2. **Delete old templates from DB** so they regenerate with new content:
   ```sql
   DELETE FROM templates;
   ```
   Or use the "Unlock All → Generate Missing → Lock All" flow in the UI.

3. **Restart the engine** — templates will auto-generate on startup.

4. **Lock all templates** after verifying they're correct.

### For New Installs

No migration needed. Templates generate fresh on first startup.

---

## 9. Open Questions for Owner

1. **CSR sequence content:** Should the plain CSR emails be shorter/more direct than CSR-WSL-5? Or same structure with different emphasis?

2. **Plain text default:** Should new campaigns default to HTML or Plain Text? (Recommend: HTML for schools, Plain for CSR)

3. **Veer Baji video:** Confirm the Instagram link `DTDBcsdk9FI` is correct (owner said "VEER BAJI NOT 2ND WORKSHOP" but link seems to be the one he provided).

4. **PMC Proposal:** Is this for CSR-WSL-5 Day 10 only, or also for plain CSR Day 10?

---

## 10. Appendix: Owner's Original Corrections (Consolidated)

From the conversation history, these are the specific corrections the owner requested:

1. ✅ Sign off as "Omkar" not "Baban Jadhav"
2. ✅ Fix brochure link (Email 1)
3. ✅ Fix 1st WSL PDF link
4. ✅ Fix Sangli report link
5. ✅ Add PMC proposal PDF to CSR Day 10
6. ✅ Add subscription overview to last email
7. ✅ Tag specimen report (Prajwal) in Day 3 and Day 7 emails
8. ✅ Remove vague "4 drone" — just say "drone"
9. ✅ "Within 10 weeks of program launch" not "of payment"
10. ✅ Don't beg. Diplomatic tone. Show cause, be sugar-coated.
11. ✅ Don't mention names (MOU not signed)
12. ✅ Mention partial options (3/4 schools)
13. ✅ Last email: tell a story, changes you're making, 2nd stage of Sangli
14. ✅ Small logo
15. ✅ Mention Baalgruh, Veer Baji, Sangli Divyang Instagram links
16. ✅ Add news coverage links (ABP, Star, Bandhuta, SBN) to last emails
17. ✅ "We deliver, we always deliver. We don't let people down."

---

**END OF SPEC**
