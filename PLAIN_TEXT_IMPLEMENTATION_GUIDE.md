# Plain Text Email Feature — Implementation Guide
## Raj Email Command Center v4.3

---

## Overview

Add plain text email support alongside HTML emails. Every template now stores BOTH an HTML body and a plain text body. When sending, Gmail sends a **multipart email** with both versions — email clients that prefer plain text will show the clean text version, while HTML-capable clients show the styled version.

**Research-backed:** Plain text emails have 21-42% higher click-through rates and better inbox placement for cold outreach (HubSpot, WarmForge studies).

---

## Files to Modify

1. `db.py` — Add `text_body` column + migration
2. `gmail.py` — Add multipart email support
3. `engine.py` — Add text content generation, update render/send methods
4. `raj_chat.py` — Add UI toggle for plain vs HTML preference (optional v2)

---

## STEP 1: db.py Changes

### 1a. Add `text_body` to `_init_tables()` templates CREATE statement

Find this block (~line 89-102):
```python
            -- Templates
            CREATE TABLE IF NOT EXISTS templates (
                sequence_id TEXT,
                day INTEGER,
                subject TEXT,
                subject_b TEXT,
                html_body TEXT,
                source TEXT DEFAULT 'unknown',
                locked INTEGER DEFAULT 0,
                ab_test INTEGER DEFAULT 0,
                ab_split REAL DEFAULT 0.5,
                cached_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (sequence_id, day)
            );
```

Replace with:
```python
            -- Templates
            CREATE TABLE IF NOT EXISTS templates (
                sequence_id TEXT,
                day INTEGER,
                subject TEXT,
                subject_b TEXT,
                html_body TEXT,
                text_body TEXT,
                source TEXT DEFAULT 'unknown',
                locked INTEGER DEFAULT 0,
                ab_test INTEGER DEFAULT 0,
                ab_split REAL DEFAULT 0.5,
                cached_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (sequence_id, day)
            );
```

### 1b. Add migration in `_migrate_schema()`

Add this block at the END of `_migrate_schema()` (after the ab_variant migration, ~line 398):

```python
        # Add text_body to templates if missing
        try:
            self.conn.execute("SELECT text_body FROM templates LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Adding text_body to templates...")
            self.conn.execute("ALTER TABLE templates ADD COLUMN text_body TEXT")
            self.conn.commit()
            print("[DB] Migration complete: text_body added")
```

### 1c. Update `template_put()` method

Find (~line 636-647):
```python
    def template_put(self, sequence_id, day, subject, html_body, source="synced",
                      subject_b=None, ab_test=0, ab_split=0.5):
        self.execute("""
            INSERT INTO templates (sequence_id, day, subject, subject_b, html_body, source, ab_test, ab_split)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sequence_id, day) DO UPDATE SET
                subject=excluded.subject, subject_b=excluded.subject_b,
                html_body=excluded.html_body, source=excluded.source,
                ab_test=excluded.ab_test, ab_split=excluded.ab_split,
                cached_at=CURRENT_TIMESTAMP
        """, (sequence_id, day, subject, subject_b, html_body, source, ab_test, ab_split))
        self.commit()
```

Replace with:
```python
    def template_put(self, sequence_id, day, subject, html_body, source="synced",
                      subject_b=None, ab_test=0, ab_split=0.5, text_body=None):
        self.execute("""
            INSERT INTO templates (sequence_id, day, subject, subject_b, html_body, text_body, source, ab_test, ab_split)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sequence_id, day) DO UPDATE SET
                subject=excluded.subject, subject_b=excluded.subject_b,
                html_body=excluded.html_body, text_body=excluded.text_body,
                source=excluded.source,
                ab_test=excluded.ab_test, ab_split=excluded.ab_split,
                cached_at=CURRENT_TIMESTAMP
        """, (sequence_id, day, subject, subject_b, html_body, text_body, source, ab_test, ab_split))
        self.commit()
```

### 1d. Update `template_get()` method

Find (~line 649-660):
```python
    def template_get(self, sequence_id, day):
        row = self.execute("""
            SELECT subject, subject_b, html_body, source, locked, ab_test, ab_split
            FROM templates WHERE sequence_id=? AND day=?
        """, (sequence_id, day)).fetchone()
        if not row:
            return None
        return {
            "subject": row[0], "subject_b": row[1], "html_body": row[2],
            "source": row[3], "locked": bool(row[4]),
            "ab_test": bool(row[5]), "ab_split": row[6]
        }
```

Replace with:
```python
    def template_get(self, sequence_id, day):
        row = self.execute("""
            SELECT subject, subject_b, html_body, text_body, source, locked, ab_test, ab_split
            FROM templates WHERE sequence_id=? AND day=?
        """, (sequence_id, day)).fetchone()
        if not row:
            return None
        return {
            "subject": row[0], "subject_b": row[1], "html_body": row[2],
            "text_body": row[3], "source": row[4], "locked": bool(row[5]),
            "ab_test": bool(row[6]), "ab_split": row[7]
        }
```

---

## STEP 2: gmail.py Changes

### 2a. Add imports at the top

Add these imports after existing imports:
```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
```

### 2b. Update `send_email()` method

Find the existing `send_email()` method and replace with:

```python
    def send_email(self, to, subject, body_html, body_text=None, thread_id=None):
        """Send email. If body_text is provided, sends multipart HTML+Plain Text.
        If body_text is None, sends HTML-only (backward compatible)."""
        if body_text:
            # Multipart: both plain text and HTML
            message = MIMEMultipart('alternative')
            message['to'] = to
            message['subject'] = subject
            if thread_id:
                message['In-Reply-To'] = thread_id
                message['References'] = thread_id
            # Attach plain text part first (preferred by plain-text clients)
            message.attach(MIMEText(body_text, 'plain', 'utf-8'))
            # Attach HTML part
            message.attach(MIMEText(body_html, 'html', 'utf-8'))
        else:
            # HTML-only (backward compatible)
            message = MIMEText(body_html, 'html', 'utf-8')
            message['to'] = to
            message['subject'] = subject
            if thread_id:
                message['In-Reply-To'] = thread_id
                message['References'] = thread_id

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body = {'raw': raw}
        if thread_id:
            body['threadId'] = thread_id
        return self.service.users().messages().send(userId='me', body=body).execute()
```

### 2c. Update `draft_email()` method

Find and replace:
```python
    def draft_email(self, to, subject, body_html, body_text=None):
        """Create a Gmail draft. Supports optional plain text body for multipart."""
        if body_text:
            message = MIMEMultipart('alternative')
            message['to'] = to
            message['subject'] = subject
            message.attach(MIMEText(body_text, 'plain', 'utf-8'))
            message.attach(MIMEText(body_html, 'html', 'utf-8'))
        else:
            message = MIMEText(body_html, 'html', 'utf-8')
            message['to'] = to
            message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return self.service.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()
```

### 2d. Update `create_scheduled_draft()` method

Find and replace:
```python
    def create_scheduled_draft(self, to, subject, body_html, send_at_iso, body_text=None):
        """Create a Gmail draft with a schedule prefix in the subject.
        Supports optional plain text body for multipart emails.
        """
        scheduled_subject = f"[RAJ-SCHEDULE:{send_at_iso}] {subject}"
        if body_text:
            message = MIMEMultipart('alternative')
            message['to'] = to
            message['subject'] = scheduled_subject
            message.attach(MIMEText(body_text, 'plain', 'utf-8'))
            message.attach(MIMEText(body_html, 'html', 'utf-8'))
        else:
            message = MIMEText(body_html, 'html', 'utf-8')
            message['to'] = to
            message['subject'] = scheduled_subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return self.service.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()
```

---

## STEP 3: engine.py Changes

### 3a. Add `html` import at the top

After existing imports (~line 28), add:
```python
import html as html_module
```

### 3b. Add `html_to_text()` static method

Add this method to the `CampaignEngine` class (after `HTML_TEMPLATE`, around line 188):

```python
    @staticmethod
    def html_to_text(html_body: str) -> str:
        """Convert HTML email body to clean plain text for multipart sending.
        Preserves structure, links, and readability. Idempotent on plain text."""
        if not html_body:
            return ""
        # If already plain text (no HTML tags), return as-is
        if "<" not in html_body and ">" not in html_body:
            return html_body.strip()

        text = html_body
        # Replace <br> variants with newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        # Replace </p> with double newline
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
        # Replace </div> with newline
        text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
        # Replace </li> with newline + bullet marker
        text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
        # Replace <li> with bullet
        text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
        # Replace <h1>-<h6> with uppercase + newlines
        for i in range(6, 0, -1):
            text = re.sub(rf'<h{i}[^>]*>(.*?)</h{i}>', lambda m: f'\n\n{m.group(1).upper()}\n{"=" * len(m.group(1))}\n', text, flags=re.IGNORECASE | re.DOTALL)
        # Replace <strong>, <b> with **text**
        text = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'**\2**', text, flags=re.IGNORECASE | re.DOTALL)
        # Replace <em>, <i> with _text_
        text = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'_\2_', text, flags=re.IGNORECASE | re.DOTALL)
        # Replace <a href="...">text</a> with text (URL)
        text = re.sub(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', lambda m: f'{m.group(2)} ({m.group(1)})', text, flags=re.IGNORECASE | re.DOTALL)
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        text = html_module.unescape(text)
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
```

### 3c. Update `render()` method

Find the existing `render()` method (~line 1246) and replace:

```python
    def render(self, seq_id: str, day: int, rec: Recipient) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Render email for recipient. Returns (subject, body_html, body_text, ab_variant)."""
        tmpl = self.db.template_get(seq_id, day)
        if not tmpl:
            return None, None, None, None

        subj, body_html, body_text = tmpl["subject"] or "", tmpl["html_body"] or "", tmpl.get("text_body") or ""
        variant = None
        if tmpl.get("ab_test"):
            variant = self._ab_variant(rec.email, tmpl.get("ab_split", 0.5))
            subj = tmpl["subject"] if variant == "A" else (tmpl.get("subject_b") or tmpl["subject"])

        extra = json.loads(rec.extra_json or "{}")

        placeholders = {
            "{{PRINCIPAL_NAME}}": rec.name, "{{SCHOOL_NAME}}": rec.org,
            "{{CSR_HEAD_NAME}}": rec.name, "{{COMPANY_NAME}}": rec.org,
            "{{OPENING_LINE}}": extra.get("Opening Line", extra.get("opening_line", "")),
            "{{NAME}}": rec.name, "{{ORG}}": rec.org, "{{EMAIL}}": rec.email,
        }
        for ph, val in placeholders.items():
            subj = subj.replace(ph, str(val))
            body_html = body_html.replace(ph, str(val))
            body_text = body_text.replace(ph, str(val))
        return subj, body_html, body_text, variant
```

### 3d. Update `_send_with_retry()` method

Find (~line 1269) and replace:

```python
    def _send_with_retry(self, to: str, subject: str, body_html: str, body_text: str = None, thread_id=None, max_retries: int = 3):
        """Send via Gmail with exponential backoff for transient SSL/network errors.
        Supports optional plain text body for multipart emails."""
        if not self.gmail or not self.gmail.is_connected():
            raise Exception("Gmail not connected. Go to Settings > Google Connections.")
        last_err = None
        for attempt in range(max_retries):
            try:
                return self.gmail.send_email(to, subject, body_html, body_text, thread_id)
            except Exception as e:
                last_err = e
                err_text = str(e).lower()
                # Only retry on transient network/TLS errors
                if any(k in err_text for k in ["ssl", "wrong_version", "connection", "timeout", "temporary"]):
                    wait = 2 ** attempt
                    self._log(f"[GmailRetry] Attempt {attempt + 1}/{max_retries} failed ({e}); retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                raise
        raise last_err
```

### 3e. Update `_process_running_batches()` send section

Find this line (~line 511):
```python
                subj, body, ab_variant = self.render(seq_id, day_offset, rec)
```
Replace with:
```python
                subj, body_html, body_text, ab_variant = self.render(seq_id, day_offset, rec)
```

Then find the tracking injection section (~line 534) and update:
```python
                    # Inject tracking pixel and wrapped links with real send_id
                    if self.tracker and self.tracker.base_url and send_id:
                        body_html = self.tracker.inject_tracking(body_html, rec.id, batch_id, send_id)
```

Then find the draft creation (~line 538) and update:
```python
                    if use_draft:
                        draft = self.gmail.create_scheduled_draft(rec.email, subj, body_html, sched_str, body_text)
```

Then find the actual send (~line 561) and update:
```python
                        msg = self._send_with_retry(rec.email, subj, body_html, body_text)
```

### 3f. Update `send_batch()` method

Find (~line 1296):
```python
            subj, body, ab_variant = self.render(seq_id, day, rec)
```
Replace with:
```python
            subj, body_html, body_text, ab_variant = self.render(seq_id, day, rec)
```

Find the tracking injection (~line 1304) and update:
```python
                if self.tracker and self.tracker.base_url and send_id:
                    body_html = self.tracker.inject_tracking(body_html, rec.id, None, send_id)
```

Find the send call (~line 1306) and update:
```python
                msg = self.gmail.send_email(rec.email, subj, body_html, body_text)
```

Find the pending_resumes section (~line 1317) and update:
```python
                    for r in due[i:]:
                        rs, rb, rt, _ = self.render(seq_id, day, r)
```

### 3g. Update `trial_send()` method

Find (~line 1350):
```python
            subj, body, _ = self.render(seq_id, day, rec)
```
Replace with:
```python
            subj, body_html, body_text, _ = self.render(seq_id, day, rec)
```

Find the banner and send section (~line 1360) and replace:
```python
                # Add trial banner
                trial_banner_html = f"<div style='background:#fff3cd;border:1px solid #ffc107;padding:10px;margin-bottom:15px;border-radius:4px;font-family:Arial,sans-serif'><strong style='color:#856404'>🧪 TRIAL EMAIL — Day {day} of {len(days)} — Sequence: {seq_id.upper()}</strong></div>"
                trial_banner_text = f"🧪 TRIAL EMAIL — Day {day} of {len(days)} — Sequence: {seq_id.upper()}\n{'='*60}\n\n"
                self._send_with_retry(email, f"[TRIAL] {subj}", trial_banner_html + body_html, trial_banner_text + (body_text or ""))
```

### 3h. Update `test_send()` method

Find (~line 1400) and replace:
```python
            self._send_with_retry(email, f"[TEST] {tmpl['subject']}", tmpl["html_body"], tmpl.get("text_body"))
```

### 3i. Update `generate_template()` method

Find (~line 971) and replace:
```python
    def generate_template(self, seq_id: str, day: int) -> dict:
        cfg = SEQUENCES.get(seq_id)
        if not cfg:
            return {"error": "Invalid sequence"}

        assets = cfg.get("assets", {}).get(day, {})
        persona = cfg.get("persona", "school")

        content_html = self._generate_content(seq_id, day, assets)
        content_text = self._generate_text_content(seq_id, day, assets)
        subject = self._generate_subject(seq_id, day)

        html = HTML_TEMPLATE.format(body=content_html)

        return {
            "subject": subject,
            "html_body": html,
            "text_body": content_text,
            "seq_id": seq_id,
            "day": day,
            "assets_used": list(assets.keys())
        }
```

### 3j. Update `save_generated_template()` method

Find (~line 1139) and replace:
```python
    def save_generated_template(self, seq_id: str, day: int, create_draft: bool = True) -> bool:
        template = self.generate_template(seq_id, day)
        if "error" in template:
            self._log(f"Failed to generate {seq_id.upper()} Day {day}: {template['error']}")
            return False

        self.db.template_put(seq_id, day, template["subject"], template["html_body"], "generated",
                              text_body=template.get("text_body"))

        if not create_draft:
            self._log(f"Generated {seq_id.upper()} Day {day} template (DB only)")
            return True

        try:
            draft = self.gmail.draft_email(
                "om@robopirate.in",
                f"[TEMPLATE] {template['subject']}",
                template["html_body"],
                template.get("text_body")
            )
            self._log(f"Generated {seq_id.upper()} Day {day} template + Gmail draft created")
            return True
        except Exception as e:
            self._log(f"Saved to DB but Gmail draft failed for {seq_id.upper()} Day {day}: {e}")
            return True
```

### 3k. Update `sync_templates()` method

Find the template_put call (~line 862) and replace:
```python
            # Preserve existing A/B test settings and text_body when syncing
            existing = self.db.template_get(seq, day)
            self.db.template_put(
                seq, day, draft_subject, draft_body,
                subject_b=existing.get("subject_b") if existing else None,
                ab_test=existing.get("ab_test", 0) if existing else 0,
                ab_split=existing.get("ab_split", 0.5) if existing else 0.5,
                text_body=existing.get("text_body") if existing else None
            )
```

### 3l. Update `validate_templates()` method

Find the body check (~line 1177) and update:
```python
                subject = (tmpl.get("subject") or "").strip() if tmpl else ""
                body = (tmpl.get("html_body") or "").strip() if tmpl else ""
                text_body = (tmpl.get("text_body") or "").strip() if tmpl else ""
                if tmpl and subject and body:
```

### 3m. Add `_generate_text_content()` method

Add this after `_generate_content()` (~line 1023):

```python
    def _generate_text_content(self, seq_id: str, day: int, assets: dict) -> str:
        """Generate plain text version of email content for multipart emails."""
        if seq_id == "school":
            return self._generate_school_text_content(day, assets)
        elif seq_id in ("csr", "csr-wsl-5"):
            return self._generate_csr_text_content(day, assets)
        else:
            return self._generate_csr_text_content(day, assets)
```

### 3n. Add `_generate_school_text_content()` method

Add this after `_generate_school_content()` (~line 1075):

```python
    def _generate_school_text_content(self, day: int, assets: dict) -> str:
        a = assets
        contents = {
            1: f"""Dear Principal,

Imagine your students building robots, coding drones, and exploring AI — all within your school walls. For the 2026-27 academic year, this is no longer optional.

WE Smart Lab by RoboPirate brings cutting-edge STEAM/AI education to Indian schools. We're already in 85+ labs across 6 states, impacting 65,000+ students.

Everything is included — lab setup, 120+ DIY kits, full-time trained teacher, NEP 2020 aligned curriculum, LMS portal, and ongoing support. Schools simply open the door; we handle the rest.

Would you be open to a 15-minute call to discuss how WSL can transform your school?

Best regards,
Omkar
RoboPirate · WSL Initiative
robopirate.in

---
Resources:
📄 Brochure: {a.get('brochure', 'Available on request')}
🎥 WSL Video: {a.get('video_wsl', 'Available on request')}
📺 ABP News Coverage: {a.get('video_abp', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            3: f"""Dear Principal,

With NEP 2020 now in full implementation and the 2026-27 academic year approaching, schools across India are racing to comply with experiential learning and coding mandates from Class 6.

The question is: Will your school lead this change or play catch-up?

WSL provides:
• Ready-to-deploy STEM labs
• NEP-aligned curriculum
• Teacher training programs
• Progress tracking dashboards

Let's discuss how your school can be NEP-ready this academic year.

Best regards,
Omkar
RoboPirate · WSL Initiative

---
📺 ABP News Coverage: {a.get('video_abp', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            5: f"""Dear Principal,

Let me share a story that might resonate with you.

Veer Baji Prabhu Vidyalay — a school much like yours — partnered with us in 2024-25 through our WE Smart Lab program. Today, their students have built 12+ working robots, participated in state-level competitions, and seen measurable improvement in science engagement.

Your school could be our next success story.

Best regards,
Omkar
RoboPirate · WSL Initiative

---
📊 Impact Report (Veer Baji): {a.get('report_vbv', 'Available on request')}
🎥 Student Star Video: {a.get('video_star', 'Available on request')}
📁 Full Folder: {a.get('folder_vbv', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            7: f"""Dear Principal,

You're not alone in this journey. 85+ schools across Maharashtra, Karnataka, Gujarat, and more have already chosen WSL.

Ready to join them?

Best regards,
Omkar
RoboPirate · WSL Initiative

---
📄 Company Profile: {a.get('profile', 'Available on request')}
📺 ABP News Coverage: {a.get('video_abp', 'Available on request')}
🎥 Student Star Video: {a.get('video_star', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            10: f"""Dear Principal,

This is my final email for the 2026-27 academic year planning. With admissions season approaching, I don't want your students to miss this opportunity.

We've prepared flexible WE Smart Lab subscription plans for schools of all sizes. Every plan includes: complete lab setup, 120+ DIY kits, full-time trained teacher, NEP 2020 + NCF aligned curriculum, LMS portal, assessments, and ongoing support.

If now isn't the right time, I understand. But if you're even slightly curious, let's have a 10-minute conversation. No obligation.

Best regards,
Omkar
RoboPirate · WSL Initiative

---
📄 Plans & Pricing: {a.get('plans', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
"""
        }
        return contents.get(day, f"Template content for Day {day}")
```

### 3o. Add `_generate_csr_text_content()` method

Add this after `_generate_csr_content()` (~line 1137):

```python
    def _generate_csr_text_content(self, day: int, assets: dict) -> str:
        a = assets
        contents = {
            1: f"""Dear CSR Head,

Your CSR budget has the power to change thousands of young lives.

RoboPirate's WE Smart Lab sets up fully managed STEAM/AI Smart Labs inside schools across India. As of now, we've reached 65,000+ students across 6 states with 85+ labs delivered through strategic CSR partnerships.

Would you be open to exploring how your CSR mandate can create measurable STEM impact?

Best regards,
Omkar
RoboPirate

---
📊 Sangli Impact Report: {a.get('report_sangli1', 'Available on request')}
📺 ABP News Coverage: {a.get('video_abp', 'Available on request')}
🎥 Sangli Video: {a.get('video_sangli', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            3: f"""Dear CSR Head,

Schedule VII of the Companies Act explicitly supports:
• Education (item ii)
• Skill development (item x)
• Rural development (item xii)

WSL aligns perfectly with all three.

We deliver and we always deliver. We don't let people down.

Best regards,
Omkar
RoboPirate

---
📊 Sangli Impact Report: {a.get('report_sangli1', 'Available on request')}
📄 Brochure: {a.get('brochure', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            5: f"""Dear CSR Head,

Numbers tell stories better than words.

Sangli District Phase 2 Results — WE Smart Lab Impact (Delivered 2025-26):
• 15 schools equipped with fully managed STEAM/AI labs
• 4,500+ students trained in robotics, coding, AI & IoT
• 87% teacher satisfaction rate
• 3 students won state-level competitions
• 1.5L+ student projects completed across all programs

This could be your company's legacy.

Best regards,
Omkar
RoboPirate

---
📊 Sangli Report 2: {a.get('report_sangli2', 'Available on request')}
📊 Veer Baji Report: {a.get('report_vbv', 'Available on request')}
🎥 Student Star Video: {a.get('video_star', 'Available on request')}
📁 Sangli Folder: {a.get('folder_sangli', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            7: f"""Dear CSR Head,

FY 2026-27 budget season is here — this is when CSR allocations are locked. Where will your CSR rupees create the most impact?

Consider the WE Smart Lab model:
• Setup cost: Rs.2.5L – 8L per school (one-time, based on tier)
• Annual program cost: Rs.7L per school (CSR School Model)
• Cost per student impacted: Under Rs.500/year
• Tax benefits: 100% deductible under Companies Act 2013 Schedule VII
• Full compliance documentation + quarterly impact reports included

They can take 3/4 schools or something — partial adoption is absolutely possible. Every child reached is a life changed.

Let's discuss a pilot program for Q1.

Best regards,
Omkar
RoboPirate

---
📄 Plans & Pricing: {a.get('plans', 'Available on request')}
🎥 WSL Video: {a.get('video_wsl', 'Available on request')}
📺 ABP News Coverage: {a.get('video_abp', 'Available on request')}
🎥 Sangli Video: {a.get('video_sangli', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            10: f"""Dear CSR Head,

This is my final outreach for FY 2026-27 planning. With budgets being locked, I respect your time and decision.

Let me tell you a story.

There was a boy named Prajwal in one of our government schools. Quiet, always sitting in the back row. The kind of child teachers forget to call on. We set up a WE Smart Lab in his school — not a big one, just the basics. A few kits, a trainer who cared, and drone access.

Six months later, Prajwal had built a working obstacle-avoidance robot. Not from a kit manual — from his own design. His teachers showed us the report we develop over children like him. The data was clear: attendance up, science scores up, but more than that — he asked questions now. He stood in the front row.

That's the imprint I want to leave. Not a sales pitch. Not a begging letter. Just this: your CSR budget can create Prajwals. One at a time, or a hundred at a time. The math works either way.

If this resonates, you know where to find me. If not, I wish you and your team the very best this fiscal year.

Warmly,
Omkar
RoboPirate

---
📄 Company Profile: {a.get('profile', 'Available on request')}
📦 Sample Kits: {a.get('kits', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
"""
        }
        return contents.get(day, f"Template content for Day {day}")
```

### 3p. Add `_generate_csr_wsl5_text_content()` method (for csr-wsl-5 sequence)

Add this after `_generate_csr_text_content()`:

```python
    def _generate_csr_wsl5_text_content(self, day: int, assets: dict) -> str:
        a = assets
        contents = {
            1: f"""Dear CSR Head,

What if your CSR budget could fund a 5-year STEM lab — and you only pay for Year 1?

That's the WE Smart Lab 5-Year Model:
• Year 1: CSR funds the lab setup + first year operations (Rs.12L)
• Years 2-5: Government/Municipal funds take over through our PMC proposal
• Result: 400 students × 5 years = 2,000 lives changed

We handle everything — setup, trainer, curriculum, reporting. You fund Year 1, we make it self-sustaining.

Would you be open to a 15-minute call to see how this works?

Best regards,
Omkar
RoboPirate

---
📊 Veer Baji Report: {a.get('report_vbv', 'Available on request')}
📄 Brochure: {a.get('brochure', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            3: f"""Dear CSR Head,

We already did this. First WE Smart Lab. Full academic year. Government school.

The trainer we placed — from an underprivileged background himself — is now certified and training 200+ students. The school principal called last week to ask when we can expand to their secondary wing.

This isn't theory. It's already happening.

Best regards,
Omkar
RoboPirate

---
📊 Veer Baji Report: {a.get('report_vbv', 'Available on request')}
📺 ABP News Coverage: {a.get('video_abp', 'Available on request')}
🎥 Student Star Video: {a.get('video_star', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            5: f"""Dear CSR Head,

The job your CSR creates:

1 Trainer. 5 Years. Trained from underprivileged background.

That's not just a job. That's a career ladder. That's a family lifted. That's a community seeing what's possible.

We don't just place trainers. We train them at our Baner HQ, certify them, and support them for 5 years. The report we develop over each child tracks everything — attendance, engagement, project completion, competition results.

This is the kind of CSR impact that gets talked about in annual reports.

Best regards,
Omkar
RoboPirate

---
🎥 WSL Video: {a.get('video_wsl', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            7: f"""Dear CSR Head,

The math:

Rs.12L CSR + Rs.28L Government = 400 Students × 5 Years

That's Rs.40L total investment. Rs.20 per student per year.

For context: One corporate off-site costs more than this. One conference booth costs more than this.

But this — this changes 2,000 lives over 5 years. This creates a STEM culture in a government school that lasts decades. This is the kind of ROI no spreadsheet can capture.

Partial adoption works too. They can take 3 schools, or 4, or 10. Every child reached is a life changed.

Best regards,
Omkar
RoboPirate

---
📄 Brochure: {a.get('brochure', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
""",

            10: f"""Dear CSR Head,

This is my final email for FY 2026-27 planning.

I've shared the numbers, the stories, the math. Now I just want to leave you with this:

We deliver. We always deliver. We don't let people down.

85+ labs. 65,000+ students. 6 states. Government schools, private schools, CSR-funded, self-funded — every single one delivered. Every single one running.

If you want to see what we offer in detail: {a.get('plans', 'Available on request')}

If this resonates, you know where to find me. If not, I genuinely wish you the very best this fiscal year.

Warmly,
Omkar
RoboPirate

---
📄 Company Profile: {a.get('profile', 'Available on request')}
📱 Instagram: {a.get('video_ig', 'Available on request')}
"""
        }
        return contents.get(day, f"Template content for Day {day}")
```

### 3q. Update `_generate_text_content()` to include csr-wsl-5

Update the method from step 3m:
```python
    def _generate_text_content(self, seq_id: str, day: int, assets: dict) -> str:
        """Generate plain text version of email content for multipart emails."""
        if seq_id == "school":
            return self._generate_school_text_content(day, assets)
        elif seq_id == "csr-wsl-5":
            return self._generate_csr_wsl5_text_content(day, assets)
        elif seq_id == "csr":
            return self._generate_csr_text_content(day, assets)
        else:
            return self._generate_csr_text_content(day, assets)
```

---

## STEP 4: Testing Checklist

After implementing all changes:

1. **Start Raj** — verify no syntax errors
2. **Check DB migration** — look for "[DB] Migration complete: text_body added" in console
3. **Template health** — verify all templates show "ok" or get auto-repaired
4. **Test send** — send a test email to yourself, check both HTML and plain text versions
5. **Trial send** — run trial sequence to your email, verify all 5 days send correctly
6. **Check Gmail** — view email source to confirm multipart structure (both text/plain and text/html parts)

---

## How Multipart Emails Work

When `body_text` is provided:
- Gmail sends an email with TWO parts: `text/plain` and `text/html`
- Plain text email clients (some mobile apps, Outlook in plain mode) show the text version
- HTML-capable clients (Gmail web, Apple Mail) show the HTML version
- Spam filters see a well-formed multipart email = higher trust score
- Recipients can switch between views in their email client

When `body_text` is None (backward compatible):
- Sends HTML-only (existing behavior)
- All existing templates without text_body continue to work

---

## Summary of Changes

| File | Lines Changed | What |
|------|--------------|------|
| `db.py` | ~15 | Add `text_body` column, migration, update template_put/get |
| `gmail.py` | ~40 | Multipart email support in send_email, draft_email, create_scheduled_draft |
| `engine.py` | ~200 | html_to_text converter, text content generators, render/send updates |

**Total: ~255 lines across 3 files**

---

*Generated for Raj v4.3 — Plain Text Email Support*
