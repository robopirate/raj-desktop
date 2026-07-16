"""
engine.py — Plain Text Email Support Patch
============================================
This file contains the exact modifications needed in engine.py to support
plain text emails alongside HTML emails.

No database schema changes are required — the preference is stored in the
existing meta table (key: "email_format").

STEP 1: Add 'import html' to the imports section
STEP 2: Replace the render() method
STEP 3: Add _html_to_plain_text() helper
STEP 4: Modify _send_with_retry() signature and body
STEP 5: Modify _process_running_batches() send block
STEP 6: Modify send_batch() send block
STEP 7: Modify trial_send() and test_send() if needed
"""

# ============================================================================
# STEP 1: Add import (after existing imports, around line 30)
# ============================================================================

# Add this line:
# import html


# ============================================================================
# STEP 2: Replace render() method (lines 1246-1267)
# ============================================================================

# OLD CODE:
#     def render(self, seq_id: str, day: int, rec: Recipient) -> Tuple[Optional[str], Optional[str], Optional[str]]:
#         tmpl = self.db.template_get(seq_id, day)
#         if not tmpl: return None, None, None
#         subj, body = tmpl["subject"] or "", tmpl["html_body"] or ""
#         variant = None
#         if tmpl.get("ab_test"):
#             variant = self._ab_variant(rec.email, tmpl.get("ab_split", 0.5))
#             subj = tmpl["subject"] if variant == "A" else (tmpl.get("subject_b") or tmpl["subject"])
#         extra = json.loads(rec.extra_json or "{}")
#         placeholders = {
#             "{{PRINCIPAL_NAME}}": rec.name, "{{SCHOOL_NAME}}": rec.org,
#             "{{CSR_HEAD_NAME}}": rec.name, "{{COMPANY_NAME}}": rec.org,
#             "{{OPENING_LINE}}": extra.get("Opening Line", extra.get("opening_line", "")),
#             "{{NAME}}": rec.name, "{{ORG}}": rec.org, "{{EMAIL}}": rec.email,
#         }
#         for ph, val in placeholders.items():
#             subj = subj.replace(ph, str(val))
#             body = body.replace(ph, str(val))
#         return subj, body, variant

# NEW CODE — paste this:

    def render(self, seq_id: str, day: int, rec: Recipient, prefer_plain: bool = False) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Render email for recipient. Returns (subject, body_html, body_text, ab_variant).
        If prefer_plain=True, also generates a plain text version of the body."""
        tmpl = self.db.template_get(seq_id, day)
        if not tmpl:
            return None, None, None, None

        subj, body = tmpl["subject"] or "", tmpl["html_body"] or ""
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
            body = body.replace(ph, str(val))

        # Generate plain text version if requested
        body_text = None
        if prefer_plain:
            body_text = self._html_to_plain_text(body)

        return subj, body, body_text, variant


# ============================================================================
# STEP 3: Add _html_to_plain_text() helper (after render(), before _send_with_retry)
# ============================================================================

    def _html_to_plain_text(self, html_body: str) -> str:
        """Convert HTML email body to clean plain text.
        Handles links, lists, headings, and preserves structure."""
        import re
        import html as html_module

        text = html_body

        # Decode HTML entities (&amp; -> &, &lt; -> <, etc.)
        text = html_module.unescape(text)

        # Replace <br> variants with newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

        # Replace </p> with double newline
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)

        # Replace </div> with single newline
        text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)

        # Replace <li> with bullet point
        text = re.sub(r'<li[^>]*>', '\n• ', text, flags=re.IGNORECASE)

        # Replace headings with spacing
        text = re.sub(r'<h[1-6][^>]*>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</h[1-6]>', '\n', text, flags=re.IGNORECASE)

        # Extract link text and URLs
        def link_replacer(m):
            href = m.group(1) if m.group(1) else ""
            link_text = m.group(2) if m.group(2) else ""
            href = href.strip()
            link_text = link_text.strip()
            # Clean up the link text (remove nested tags)
            link_text = re.sub(r'<[^>]+>', '', link_text)
            if not link_text:
                return f"\n{href}\n"
            if link_text == href or not href:
                return f"\n{link_text}\n"
            return f"{link_text} ({href})"

        text = re.sub(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            link_replacer, text,
            flags=re.IGNORECASE | re.DOTALL
        )

        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Clean up excessive whitespace
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        text = re.sub(r'[ \t]+\n', '\n', text)
        text = re.sub(r'\n[ \t]+', '\n', text)
        text = re.sub(r' {2,}', ' ', text)

        # Strip leading/trailing whitespace per line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        # Final cleanup
        text = text.strip()

        return text


# ============================================================================
# STEP 4: Modify _send_with_retry() (lines 1269-1287)
# ============================================================================

# OLD CODE:
#     def _send_with_retry(self, to: str, subject: str, body_html: str, thread_id=None, max_retries: int = 3):
#         """Send via Gmail with exponential backoff for transient SSL/network errors."""
#         if not self.gmail or not self.gmail.is_connected():
#             raise Exception("Gmail not connected. Go to Settings > Google Connections.")
#         last_err = None
#         for attempt in range(max_retries):
#             try:
#                 return self.gmail.send_email(to, subject, body_html, thread_id)
#             except Exception as e:
#                 last_err = e
#                 err_text = str(e).lower()
#                 if any(k in err_text for k in ["ssl", "wrong_version", "connection", "timeout", "temporary"]):
#                     wait = 2 ** attempt
#                     self._log(f"[GmailRetry] Attempt {attempt + 1}/{max_retries} failed ({e}); retrying in {wait}s...")
#                     time.sleep(wait)
#                     continue
#                 raise
#         raise last_err

# NEW CODE — paste this:

    def _send_with_retry(self, to: str, subject: str, body_html: str, body_text: str = None, thread_id=None, max_retries: int = 3):
        """Send via Gmail with exponential backoff for transient SSL/network errors.
        If body_text is provided, sends as plain text instead of HTML."""
        if not self.gmail or not self.gmail.is_connected():
            raise Exception("Gmail not connected. Go to Settings > Google Connections.")
        last_err = None
        for attempt in range(max_retries):
            try:
                if body_text:
                    return self.gmail.send_email_plain(to, subject, body_text, thread_id)
                return self.gmail.send_email(to, subject, body_html, thread_id)
            except Exception as e:
                last_err = e
                err_text = str(e).lower()
                if any(k in err_text for k in ["ssl", "wrong_version", "connection", "timeout", "temporary"]):
                    wait = 2 ** attempt
                    self._log(f"[GmailRetry] Attempt {attempt + 1}/{max_retries} failed ({e}); retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                raise
        raise last_err


# ============================================================================
# STEP 5: Modify _process_running_batches() send block (around lines 510-570)
# ============================================================================

# Find this section in _process_running_batches():
#                 # Send email
#                 subj, body, ab_variant = self.render(seq_id, day_offset, rec)
#                 if not subj:
#                     ...
#                 try:
#                     ...
#                     msg = self._send_with_retry(rec.email, subj, body)

# REPLACE with:

                # Send email
                prefer_plain = self.db.get_meta("email_format") == "plain"
                subj, body_html, body_text, ab_variant = self.render(seq_id, day_offset, rec, prefer_plain=prefer_plain)
                if not subj:
                    self._log(f"[Batch {batch_id}] No template for {rec.email} Day {day_offset}, skipping")
                    self.db.execute("UPDATE batch_recipients SET status='failed' WHERE batch_id=? AND recipient_id=?",
                        (batch_id, rec.id))
                    continue

                try:
                    # Determine if draft or immediate send
                    sched_str = batch.get("scheduled_at")
                    use_draft = False
                    if sched_str:
                        try:
                            sched_dt = datetime.fromisoformat(sched_str.replace("Z", "+00:00"))
                            use_draft = sched_dt > now
                        except:
                            pass

                    # Use plain text body if available, otherwise HTML
                    body_to_send = body_text if body_text else body_html

                    # Pre-insert sends record to get send_id for tracking
                    placeholder_status = "drafted" if use_draft else "pending"
                    send_id = self.db.campaign_queue_send(rec.id, day_offset, subj, "pending", placeholder_status, batch_id, ab_variant)

                    # Inject tracking pixel and wrapped links with real send_id
                    # Note: tracking pixel only works with HTML; skip for plain text
                    if not body_text and self.tracker and self.tracker.base_url and send_id:
                        body_to_send = self.tracker.inject_tracking(body_to_send, rec.id, batch_id, send_id)

                    if use_draft:
                        draft = self.gmail.create_scheduled_draft(rec.email, subj, body_to_send, sched_str)
                        self.db.execute("""
                            UPDATE batch_recipients SET status='drafted', sent_at=?
                            WHERE batch_id=? AND recipient_id=?
                        """, (now.isoformat(), batch_id, rec.id))
                        self.db.execute("UPDATE sends SET draft_id=?, status='drafted', ab_variant=? WHERE id=?",
                                        (draft.get("id"), ab_variant, send_id))
                        self.db.commit()
                        self._log(f"[Batch {batch['name']}] Scheduled draft for {rec.email} ({seq_id.upper()} Day {day_offset})")
                    else:
                        # Delete any old scheduled draft before sending for real
                        old_draft = self.db.execute("""
                            SELECT draft_id FROM sends
                            WHERE recipient_id=? AND batch_id=? AND status='drafted' AND draft_id IS NOT NULL
                            ORDER BY id DESC LIMIT 1
                        """, (rec.id, batch_id)).fetchone()
                        if old_draft and old_draft[0]:
                            try:
                                self.gmail.delete_draft(old_draft[0])
                                self._log(f"[Batch {batch['name']}] Deleted old draft for {rec.email}")
                            except Exception as del_err:
                                self._log(f"[Batch {batch['name']}] Draft delete skipped: {del_err}")

                        msg = self._send_with_retry(rec.email, subj, body_html, body_text, thread_id=None)
                        self.db.execute("""
                            UPDATE batch_recipients SET status='sent', sent_at=?
                            WHERE batch_id=? AND recipient_id=?
                        """, (now.isoformat(), batch_id, rec.id))
                        self.db.execute("UPDATE sends SET draft_id=?, status='sent', sent_at=?, ab_variant=? WHERE id=?",
                                        (msg.get("id"), now.isoformat(), ab_variant, send_id))
                        self.db.commit()
                        fmt_label = "plain" if body_text else "HTML"
                        self._log(f"[Batch {batch['name']}] Sent ({fmt_label}) to {rec.email} ({seq_id.upper()} Day {day_offset})")


# ============================================================================
# STEP 6: Modify send_batch() send block (around lines 1295-1328)
# ============================================================================

# Find this section in send_batch():
#         for i, rec in enumerate(due):
#             subj, body, ab_variant = self.render(seq_id, day, rec)
#             if not subj:
#                 ...
#             try:
#                 send_id = self.db.campaign_queue_send(rec.id, day, subj, "pending", "pending", None, ab_variant)
#                 if self.tracker and self.tracker.base_url and send_id:
#                     body = self.tracker.inject_tracking(body, rec.id, None, send_id)
#                 msg = self.gmail.send_email(rec.email, subj, body)

# REPLACE with:

        prefer_plain = self.db.get_meta("email_format") == "plain"
        for i, rec in enumerate(due):
            subj, body_html, body_text, ab_variant = self.render(seq_id, day, rec, prefer_plain=prefer_plain)
            if not subj:
                self._log(f"No template for {rec.email}, skipping")
                continue
            try:
                body_to_send = body_text if body_text else body_html
                send_id = self.db.campaign_queue_send(rec.id, day, subj, "pending", "pending", None, ab_variant)
                if not body_text and self.tracker and self.tracker.base_url and send_id:
                    body_to_send = self.tracker.inject_tracking(body_to_send, rec.id, None, send_id)
                if body_text:
                    msg = self.gmail.send_email_plain(rec.email, subj, body_to_send)
                else:
                    msg = self.gmail.send_email(rec.email, subj, body_to_send)


# ============================================================================
# STEP 7: Modify trial_send() (around lines 1349-1364)
# ============================================================================

# Find:
#         for i, day in enumerate(days):
#             subj, body, _ = self.render(seq_id, day, rec)
#
# REPLACE with:

        prefer_plain = self.db.get_meta("email_format") == "plain"
        for i, day in enumerate(days):
            subj, body_html, body_text, _ = self.render(seq_id, day, rec, prefer_plain=prefer_plain)

# And in the send block, replace:
#                 self._send_with_retry(email, f"[TRIAL] {subj}", body)
# WITH:
#                 self._send_with_retry(email, f"[TRIAL] {subj}", body_html, body_text)


# ============================================================================
# STEP 8: Modify test_send() (around lines 1387-1400)
# ============================================================================

# Find:
#         subj, body, _ = self.render(seq_id, day, rec)
#
# REPLACE with:

        prefer_plain = self.db.get_meta("email_format") == "plain"
        subj, body_html, body_text, _ = self.render(seq_id, day, rec, prefer_plain=prefer_plain)

# And replace:
#         self._send_with_retry(email, f"[TEST] {subj}", body)
# WITH:
#         self._send_with_retry(email, f"[TEST] {subj}", body_html, body_text)
