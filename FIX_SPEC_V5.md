# Raj Web UI — Fix Specification
## Version: v5.0-fixes | Date: 2026-06-14
## Owner: Omkar (RoboPirate)

---

## 1. Research Summary: HTML vs Plain Text Emails

### Key Findings (2024-2026 B2B Cold Email Benchmarks)

| Metric | HTML Email | Plain Text | Winner |
|--------|-----------|------------|--------|
| Reply Rate | Baseline | **+18% higher** | Plain Text |
| Open Rate | ~27.7% avg | Similar or better | Tie |
| Spam Filter Risk | Higher (images, links) | Lower | Plain Text |
| Mobile Readability | Poor (formatting breaks) | Excellent | Plain Text |
| Perceived Authenticity | Marketing/promotional | Personal/1-to-1 | Plain Text |
| Link Tracking | Yes (pixel + wrapped URLs) | Yes (wrapped URLs only) | HTML |
| Branding | Strong (logo, colors) | Minimal | HTML |

**Bottom Line for RoboPirate:**
- **Cold outreach (Day 1, Day 3):** Use **plain text** — higher reply rates, feels personal
- **Follow-ups with proof (Day 5, Day 7, Day 10):** Use **HTML** — showcase reports, videos, impact data
- **Best practice:** Send multipart emails (both HTML + plain text) so recipient's client chooses

**Industry data sources:**
- Lemlist 2025: Plain text = +18% reply rate vs HTML
- Woodpecker 2026: 50-125 words optimal, 3-5 sentences, 1 clear CTA
- GMass: 6-8 sentences = 42.67% open rate, 6.9% reply rate
- HubSpot: Average reading time = 11 seconds — anything beyond that window won't be read

---

## 2. Template System Fixes

### 2.1 Engine.py — `_generate_content()` methods

**Problem:** `_generate_content()` only generates HTML. Plain text is generated separately in `_generate_text_content()` but the HTML versions are weak — no links, no asset embedding, generic copy.

**Fix:** Rewrite all 3 sequences' HTML content to:
1. Embed Drive links as styled CTA buttons
2. Embed YouTube/Instagram links as clickable thumbnails
3. Include the "diplomatic tone" Omkar wants (not pushy, story-driven)
4. Keep HTML under 125 words of actual text (rest is visual/links)
5. Generate matching plain text that mirrors the HTML message but in conversational format

**Tone guidelines (per Omkar's feedback):**
- ❌ No: "First branded photo: Within 10 weeks of payment" (sounds like a beggar)
- ✅ Yes: "First branded photo: Within 10 weeks of program launch" (focus on delivery)
- ❌ No: "Transform Your School" (generic marketing)
- ✅ Yes: Story-driven, specific examples, real schools
- ❌ No: Big logo at top (keep small, no issue)
- ✅ Yes: "We deliver and we always deliver. We don't let people down."
- ❌ No: Asking for money directly
- ✅ Yes: Diplomatic, sweet tongue, logical, genuine — "if you say 4, you give 4"
- Sign off as "Omkar" not "Vikram" or generic "RoboPirate Team"
- Don't mention MOU not signed, don't name specific people
- Mention Prajwal as specimen character (not real) — the kind of report we develop over children
- Tag specimen report in Day 3 email
- In last email: leave an imprint, tell a story, changes we're making, 2nd stage of Sangli
- Reference Balgruh Instagram: https://www.instagram.com/p/DSSIy7nglXc/
- Reference Veer Baji 2nd workshop: https://www.instagram.com/p/DTDBcsdk9FI/
- Reference 1st workshop Sangli divyang: https://www.instagram.com/p/DMhEDutOrl-/

### 2.2 Asset Links (CONFIRMED — use these exactly)

**Email 1 (Day 1) assets:**
- WSL PDF: https://drive.google.com/file/d/1qiWBhOiklPpwU5NaVkqnfjA6v9q3YumS/view
- ABP News: https://youtu.be/FJ2_W53WjmA
- WSL Video: https://drive.google.com/file/d/1KPrC2IpdooxazGJiyVe79JgyWlJbOxzu/view
- Instagram: https://www.instagram.com/reel/DMe2HzqofAk/

**Email 2 (Day 3) assets:**
- Sangli Report 1: https://drive.google.com/file/d/1HpNdnamA2k3H0xkKr58STEKMNu5RgHPx/view
- Brochure: https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view
- Instagram: https://www.instagram.com/reel/DMe2HzqofAk/

**Email 3 (Day 5) assets:**
- Sangli Report 2: https://drive.google.com/file/d/1pKSm1WPlPk-we4aC-uhqxEy8w-BYygSN/view
- Veer Baji Report: https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view
- Student Star Video: https://youtube.com/watch?v=iziKPBSfGKU
- Sangli Folder: https://drive.google.com/drive/folders/15sc5iOIKTBZyenb2rCpGVAK1lExcG5BC
- Instagram: https://www.instagram.com/reel/DMe2HzqofAk/
- Balgruh IG: https://www.instagram.com/p/DSSIy7nglXc/
- Veer Baji 2nd: https://www.instagram.com/p/DTDBcsdk9FI/
- Sangli Divyang 1st: https://www.instagram.com/p/DMhEDutOrl-/

**Email 4 (Day 7) assets:**
- Plans & Pricing: https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view
- WSL Video: https://drive.google.com/file/d/1KPrC2IpdooxazGJiyVe79JgyWlJbOxzu/view
- ABP News: https://youtu.be/FJ2_W53WjmA
- Sangli Video: https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view
- Instagram: https://www.instagram.com/reel/DMe2HzqofAk/
- PMC Proposal PDF: https://drive.google.com/file/d/15-EuEcwci8olOSnm0V50laK3gVKCUCe-/view

**Email 5 (Day 10) assets:**
- Company Profile: https://drive.google.com/file/d/1g9JJ4_VO_28QKYD7iVVDJZcv9l4uRbZu/view
- Sample Kits: https://drive.google.com/file/d/1cvi4p8IHgx1MekanVRHN3Fo4Lk9vbubX/view
- Instagram: https://www.instagram.com/reel/DMe2HzqofAk/
- Subscription/Clear Insight: https://drive.google.com/file/d/1p2CyHVZK_giZj0KNDGTTs_-s7HxVnQ_C/view
- Veer Baji Report: https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view

### 2.3 db.py — Template Schema

**Current:** `templates` table has `html_body`, `text_body`, `subject_b`, `ab_test`, `ab_split`

**Status:** ✅ Already supports both formats. No schema changes needed.

**Verify:** `template_get()` and `template_put()` already handle `text_body` column.

### 2.4 web/app.py — Template Endpoints

**Current:**
- `GET /api/templates/<seq>/<int:day>` → returns `{subject, subject_b, html_body, text_body, ...}` ✅
- `PUT /api/templates/<seq>/<int:day>` → accepts `{subject, html_body, text_body}` ✅
- `POST /api/templates/<seq>/<int:day>/generate` → calls `engine.save_generated_template()`

**Problem:** `generate_template()` in engine.py generates HTML content but the HTML is weak. The `save_generated_template()` saves to DB but the HTML content needs to be richer.

**Fix:** Update `_generate_school_content()`, `_generate_csr_content()`, `_generate_csr_wsl5_content()` to produce rich HTML with embedded links, styled CTAs, and proper formatting.

### 2.5 web/static/js/templates.js — UI Fixes

**Current Problems:**
1. When switching from HTML to Plain Text, it shows `tmpl.text_body || ''` but if text_body is empty, it shows nothing
2. When saving in Plain Text mode, it saves `text_body` but may lose `html_body` if not cached
3. The preview pane doesn't show plain text properly — it wraps in `<pre>` but should show as rendered text
4. No indication of which format will be sent (multipart sends both, but UI should clarify)

**Fixes needed:**
1. Load both `html_body` AND `text_body` from API, cache both separately
2. When switching format, preserve the other format in cache
3. Show a badge: "Multipart email — both HTML and Plain Text will be sent"
4. Add "Convert to Plain Text" button that auto-generates plain text from HTML using engine's `html_to_text()`
5. Add "Convert to HTML" button that wraps plain text in basic HTML template

---

## 3. Import Page Fixes

### 3.1 Missing Sequence Selector

**Problem:** Import page has no way to select which sequence (school, csr, csr-wsl-5) to import leads into. Leads default to "leads" sequence and must be manually reassigned.

**Fix:** Add sequence dropdown to both File Upload and Paste sections:
- Options: "Leads (unassigned)", "School", "CSR", "CSR-WSL-5"
- When selected, leads get `sequence_id` set accordingly
- Also add sub-pool input field (text) for tagging (e.g., "sangli-batch-1", "pune-corporates")

### 3.2 Sub-pool Filter on Batches Page

**Problem:** Batches page shows sub-pool selector but it's not populated with actual sub-pools from the database.

**Fix:** When sequence is selected, call `/api/pools?sequence_id=<seq>` to populate sub-pool dropdown with actual available sub-pools.

---

## 4. Replies Page Fixes

### 4.1 Current State

**What works:**
- ✅ Fetch replies from Gmail
- ✅ Display reply list with status badges
- ✅ Mark as handled

**What's missing:**
- ❌ AI-generated draft reply display (draft_html from DB)
- ❌ Send draft reply button
- ❌ Edit draft reply before sending
- ❌ Blacklist from reply button
- ❌ Sentiment analysis display (sentiment column exists but not shown well)
- ❌ Summary of reply content

### 4.2 Fixes Needed

1. **Expandable reply card:** Click to expand and see full reply body, AI summary, and draft reply
2. **Draft reply section:** Show AI-generated draft HTML with "Edit" and "Send" buttons
3. **Actions row:** Mark handled | Send draft | Edit draft | Blacklist sender | View thread
4. **Sentiment display:** Color-coded badge (positive=green, neutral=blue, hostile=red, unsubscribe=gray)

---

## 5. Blacklist Page Fixes

### 5.1 Current State

**What works:**
- ✅ Display blacklisted emails
- ✅ Add emails manually
- ✅ Remove individual emails
- ✅ Import CSV

**What's missing:**
- ❌ Search/filter blacklisted emails
- ❌ Bulk remove (checkboxes + "Remove selected")
- ❌ Show reason for blacklisting prominently
- ❌ Pagination (if list grows large)

### 5.2 Fixes Needed

1. **Search bar:** Filter by email or reason
2. **Bulk actions:** Checkboxes on each row + "Remove selected" button
3. **Reason badge:** Color-coded (bounce=red, manual=gray, sentiment=orange)
4. **Date sorting:** Sort by added date (newest first)

---

## 6. Dashboard Fixes

### 6.1 Template Health Widget

**Add to dashboard:** A small widget showing template status:
- Green: All 15 templates (3 sequences × 5 days) are populated
- Yellow: Some templates missing/empty
- Red: Critical templates missing (Day 1 of any sequence)
- Click to jump to Templates page

### 6.2 Sequence Selector for Pipeline

**Add:** Dropdown to filter pipeline table by sequence (School / CSR / CSR-WSL-5 / All)

---

## 7. Email Content Improvements (All 3 Sequences)

### 7.1 School Sequence (Day 1-5)

**Day 1 — Hook (Plain Text preferred):**
```
Subject: {{SCHOOL_NAME}} — A question about your STEM labs

Dear {{PRINCIPAL_NAME}},

Quick question: Are your students getting hands-on time with robotics, drones, and AI this year?

We've set up 85+ WE Smart Labs across 6 states. Schools like Veer Baji Prabhu Vidyalay (Sangli) started with a single room and now have students winning state-level competitions.

Everything's included — lab setup, 120+ kits, trained teacher, NEP curriculum, LMS. You just open the door.

Worth a 15-minute call to explore?

Warmly,
Omkar
RoboPirate

---
📄 WSL Program PDF: [link]
🎥 See a lab in action: [link]
📺 ABP News coverage: [link]
📱 Latest on Instagram: [link]
```

**Day 3 — NEP Compliance (HTML):**
- Visual timeline of NEP 2020 mandates
- "Is your school ready?" checklist graphic
- Link to brochure

**Day 5 — Story/Veer Baji (HTML):**
- Before/after photos (if available)
- Student project showcase
- Link to Veer Baji report
- Tag specimen report

**Day 7 — Social Proof (HTML):**
- Map of 85+ schools
- Testimonial quotes
- Link to company profile

**Day 10 — Soft Close (Plain Text preferred):**
```
Subject: {{PRINCIPAL_NAME}}, one last thing

I won't keep emailing you about this. You've got a school to run and I respect that.

But if you're even a little curious about what a WE Smart Lab could do for {{SCHOOL_NAME}}, I'll make time for a 10-minute call. No pitch, just show-and-tell.

If not, I genuinely wish you a great academic year.

Warmly,
Omkar
RoboPirate

P.S. — If you want to see what we offer in detail: [subscription link]
```

### 7.2 CSR Sequence (Day 1-5)

**Day 1 — Impact Hook (Plain Text preferred):**
```
Subject: {{COMPANY_NAME}} — 65,000 students and counting

Dear {{CSR_HEAD_NAME}},

Your CSR budget has the power to change thousands of young lives. The question is: where will it create the most lasting impact?

We've reached 65,000+ students across 6 states through WE Smart Labs — fully managed STEM/AI labs inside schools. CSR funds Year 1, government takes over Years 2-5. Sustainable by design.

Worth a 15-minute call to see how this works?

Best regards,
Omkar
RoboPirate

---
📊 Sangli Impact Report: [link]
📺 ABP News coverage: [link]
🎥 Sangli program video: [link]
📱 Instagram updates: [link]
```

**Day 3 — Schedule VII (HTML):**
- Visual alignment chart: Schedule VII items → WSL outcomes
- Link to brochure

**Day 5 — Sangli Story (HTML):**
- Infographic: 15 schools, 4,500 students, 87% satisfaction
- Link to Sangli reports
- Tag specimen report
- Instagram embeds for Balgruh, Veer Baji 2nd workshop, Sangli divyang

**Day 7 — ROI Math (HTML):**
- Cost breakdown visual
- "Rs.20 per student per year" highlight
- Link to plans & pricing + PMC proposal

**Day 10 — Legacy Close (Plain Text preferred):**
```
Subject: The story I want to leave you with

Dear {{CSR_HEAD_NAME}},

This is my last email for FY 2026-27 planning. I respect your time, so I'll keep this short.

There was a boy named Prajwal in one of our government schools. Quiet, always in the back row. The kind of child teachers forget to call on. We set up a WE Smart Lab in his school — not a big one, just the basics. A few kits, a trainer who cared, and drone access.

Six months later, Prajwal built a working obstacle-avoidance robot. From his own design, not a kit manual. His teachers showed us the report we develop over children like him. Attendance up. Science scores up. But more than that — he asked questions now. He stood in the front row.

That's the imprint I want to leave. Not a sales pitch. Just this: your CSR budget can create Prajwals. One at a time, or a hundred at a time.

If this resonates, you know where to find me. If not, I genuinely wish you and your team the very best this fiscal year.

Warmly,
Omkar
RoboPirate

---
📄 Company Profile: [link]
📦 Sample Kits: [link]
📱 Instagram: [link]
```

### 7.3 CSR-WSL-5 Sequence (Day 1-5)

**Day 1 — The 5-Year Model (Plain Text preferred):**
```
Subject: {{COMPANY_NAME}} — Fund Year 1, impact 5 years

Dear {{CSR_HEAD_NAME}},

What if your CSR budget could fund a 5-year STEM lab — and you only pay for Year 1?

That's the WE Smart Lab 5-Year Model:
• Year 1: CSR funds setup + operations (Rs.12L)
• Years 2-5: Government/Municipal funds take over through our PMC proposal
• Result: 400 students × 5 years = 2,000 lives changed

We handle everything — setup, trainer, curriculum, reporting. You fund Year 1, we make it self-sustaining.

Worth a 15-minute call?

Best regards,
Omkar
RoboPirate

---
📊 Veer Baji Report: [link]
📄 Brochure: [link]
📱 Instagram: [link]
```

**Day 3 — Proof (HTML):**
- "We already did this" — photos from first WE Smart Lab
- Trainer story (from underprivileged background, now certified)
- Link to Veer Baji report + ABP News

**Day 5 — Employment Impact (HTML):**
- "1 Trainer. 5 Years. Trained from underprivileged background."
- Career ladder visual
- Link to WSL video

**Day 7 — The Math (HTML):**
- "Rs.12L CSR + Rs.28L Government = 400 Students × 5 Years"
- Visual equation
- "Partial adoption works too — 3 schools, 4 schools, 10 schools"
- Link to brochure

**Day 10 — Final Call (Plain Text preferred):**
```
Subject: FY 2026-27 budget window + 90-day launch plan

Dear {{CSR_HEAD_NAME}},

Budgets are being locked. I won't send another follow-up.

We've shared the numbers, the stories, the math. Now I just want to leave you with this:

We deliver. We always deliver. We don't let people down.

85+ labs. 65,000+ students. 6 states. Every single one delivered. Every single one running.

If you want to see what we offer in detail: [subscription link]

If this resonates, you know where to find me. If not, I genuinely wish you the very best this fiscal year.

Warmly,
Omkar
RoboPirate

---
📄 Company Profile: [link]
📱 Instagram: [link]
```

---

## 8. Implementation Priority

### Phase A: Critical (Do First)
1. ✅ Fix engine.py `_generate_content()` methods — rich HTML with embedded links
2. ✅ Fix engine.py `_generate_text_content()` methods — diplomatic tone, proper links
3. ✅ Fix templates.js — proper HTML/Plain Text toggle, cache both formats
4. ✅ Update asset links in SEQUENCES dict to match Omkar's confirmed links

### Phase B: Important (Do Next)
5. Add sequence selector to Import page
6. Add sub-pool filter to Import page
7. Fix Replies page — draft reply display, send/edit actions
8. Fix Blacklist page — search, bulk actions

### Phase C: Polish (Do Last)
9. Dashboard template health widget
10. Sequence filter for pipeline table
11. Test all 15 templates (3 sequences × 5 days) with trial send
12. Verify all Drive links are accessible

---

## 9. Testing Checklist

- [ ] Day 1 School template renders with all links
- [ ] Day 1 CSR template renders with all links
- [ ] Day 1 CSR-WSL-5 template renders with all links
- [ ] Plain text version is generated for all 15 templates
- [ ] HTML version has styled CTA buttons for Drive links
- [ ] Templates page loads both HTML and Plain Text without losing data
- [ ] Switching format preserves the other format
- [ ] Trial send works for all 3 sequences
- [ ] Import page has sequence selector
- [ ] Import page has sub-pool input
- [ ] Replies page shows AI draft replies
- [ ] Replies page can send draft replies
- [ ] Blacklist page has search and bulk remove
- [ ] All 15 templates pass tone check (diplomatic, not pushy)
- [ ] All links are correct and accessible
- [ ] Sign-off is "Omkar" not "RoboPirate Team"
- [ ] No "branded photo within 10 weeks of payment" language
- [ ] No big logo at top
- [ ] "We deliver and we always deliver" included where appropriate
- [ ] Prajwal story in Day 10 CSR email
- [ ] Specimen report tagged in Day 3 and Day 5
- [ ] Instagram links for Balgruh, Veer Baji, Sangli divyang included
- [ ] PMC proposal PDF linked in Day 7
- [ ] Subscription/clear insight link in Day 10

---

## 10. Notes for Kimi Code Implementation

**When implementing this spec:**
1. Read `engine.py` lines 1000-1550 for template generation methods
2. Read `db.py` lines 640-680 for template_put/template_get
3. Read `web/static/js/templates.js` for current UI logic
4. Read `web/templates/index.html` for page structure
5. The SEQUENCES dict at top of engine.py (lines 44-148) defines asset links per day
6. HTML_TEMPLATE (lines 160-189) wraps all HTML content — don't break it
7. `html_to_text()` method (lines 287-323) can auto-convert HTML → plain text
8. All Drive links must be `/view` format (not `/edit` or preview)
9. Test with `python test_raj.py` after each change
10. Run `python web_start.py` and verify UI loads correctly

**Key files to modify:**
- `engine.py` — template content generation (lines 1061-1530)
- `web/static/js/templates.js` — UI format toggle and caching
- `web/templates/index.html` — Import page sequence selector
- `web/static/js/import.js` — Import logic
- `web/static/js/replies.js` — Draft reply actions
- `web/static/js/blacklist.js` — Search and bulk actions

---

*End of Fix Specification v5.0*
