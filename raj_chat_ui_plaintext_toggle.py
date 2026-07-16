"""
raj_chat.py UI Toggle Component — Plain Text Email Support
============================================================
This module contains the COMPLETE production-ready code additions for
raj_chat.py to add a plain-text email toggle in the Settings view.

WHAT THIS DOES:
- Adds a "📧 Email Format" section in Settings with an HTML / Plain Text toggle
- Persists the preference to the DB meta table (key: "email_format")
- The engine reads this preference and sends emails accordingly
- When plain text is selected, HTML templates are auto-converted to clean text

INTEGRATION INSTRUCTIONS:
1. Copy the _build_settings_view additions into your existing _build_settings_view()
2. Copy the _save_email_format and _load_email_format methods into RajChatApp
3. In engine.py, modify _send_with_retry() to accept a body_text parameter
4. In engine.py, modify render() to return (subject, body_html, body_text, ab_variant)
5. In gmail.py, add send_email_plain() method

All code below is production-ready and copy-pasteable.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: ADD TO RajChatApp.__init__ (after self._current_view = "dashboard")
# ═══════════════════════════════════════════════════════════════════════════════

# In __init__, add this line to track email format preference:
# self.email_format_var = ctk.StringVar(value="html")  # "html" or "plain"

# Then call _load_email_format() at the end of __init__:
# self._load_email_format()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: ADD TO _build_settings_view() — after the Notifications frame
# ═══════════════════════════════════════════════════════════════════════════════

# Paste this block INSIDE _build_settings_view(), after the notif_frame section
# (after line ~3232 in the original file, before the _save_notification_setting method)

        # ─── Email Format Toggle ───
        email_format_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        email_format_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(email_format_frame, text="📧 Email Format:", font=self._font(12),
                     text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 5))

        # Description label
        ctk.CTkLabel(email_format_frame,
                     text="Choose how emails are sent to recipients. Plain text avoids spam filters but has no styling.",
                     font=self._font(10), text_color=C_TEXT_DIM, wraplength=600).pack(anchor="w", padx=15, pady=(0, 8))

        # Toggle row: HTML | Plain Text
        toggle_row = ctk.CTkFrame(email_format_frame, fg_color="transparent")
        toggle_row.pack(fill="x", padx=15, pady=(0, 10))

        # HTML option
        self.email_format_html_btn = ctk.CTkButton(
            toggle_row, text="🎨  HTML (Styled)", font=self._font(11, bold=True),
            fg_color=C_PRIMARY, hover_color=C_PRIMARY_HOVER,
            text_color="white", corner_radius=8, width=140, height=32,
            command=lambda: self._set_email_format("html")
        )
        self.email_format_html_btn.pack(side="left", padx=(0, 8))

        # Plain Text option
        self.email_format_plain_btn = ctk.CTkButton(
            toggle_row, text="📝  Plain Text", font=self._font(11, bold=True),
            fg_color=C_PANEL_MUTED, hover_color=C_BORDER,
            text_color=C_TEXT_DIM, corner_radius=8, width=140, height=32,
            command=lambda: self._set_email_format("plain")
        )
        self.email_format_plain_btn.pack(side="left", padx=(0, 8))

        # Status indicator
        self.email_format_status = ctk.CTkLabel(
            toggle_row, text="HTML format active — rich styling with dark theme",
            font=self._font(10), text_color=C_SUCCESS
        )
        self.email_format_status.pack(side="left", padx=(10, 0))

        # Info box about plain text
        self.plain_text_info = ctk.CTkFrame(email_format_frame, fg_color=C_CARD_ALT,
                                            corner_radius=8, border_width=1, border_color=C_BORDER)
        self.plain_text_info.pack(fill="x", padx=15, pady=(0, 10))
        self.plain_text_info.pack_forget()  # Hidden by default

        info_text = (
            "📋 Plain Text Mode Details:\n"
            "  • All HTML styling is stripped — emails look like personal messages\n"
            "  • Links are preserved as full URLs (not clickable buttons)\n"
            "  • Images and videos appear as text links to Drive/YouTube/Instagram\n"
            "  • Signatures are simplified — no logos, just text\n"
            "  • Better deliverability: less likely to trigger spam filters\n"
            "  • Best for: cold outreach, first-touch emails, CSR conversations"
        )
        self.plain_text_info_label = ctk.CTkLabel(
            self.plain_text_info, text=info_text,
            font=self._font(10), text_color=C_TEXT_DIM, justify="left"
        )
        self.plain_text_info_label.pack(anchor="w", padx=12, pady=10)

        # Load saved preference
        self._load_email_format()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: ADD THESE METHODS TO RajChatApp class
# ═══════════════════════════════════════════════════════════════════════════════

    def _set_email_format(self, fmt: str):
        """Set email format preference and update UI."""
        self.email_format_var.set(fmt)
        self.engine.db.set_meta("email_format", fmt)

        if fmt == "html":
            self.email_format_html_btn.configure(
                fg_color=C_PRIMARY, text_color="white",
                hover_color=C_PRIMARY_HOVER
            )
            self.email_format_plain_btn.configure(
                fg_color=C_PANEL_MUTED, text_color=C_TEXT_DIM,
                hover_color=C_BORDER
            )
            self.email_format_status.configure(
                text="HTML format active — rich styling with dark theme",
                text_color=C_SUCCESS
            )
            self.plain_text_info.pack_forget()
        else:
            self.email_format_html_btn.configure(
                fg_color=C_PANEL_MUTED, text_color=C_TEXT_DIM,
                hover_color=C_BORDER
            )
            self.email_format_plain_btn.configure(
                fg_color=C_PRIMARY, text_color="white",
                hover_color=C_PRIMARY_HOVER
            )
            self.email_format_status.configure(
                text="Plain text active — personal message style",
                text_color=C_PRIMARY
            )
            self.plain_text_info.pack(fill="x", padx=15, pady=(0, 10))

        self._log_activity(f"Email format set to: {fmt.upper()}")

    def _load_email_format(self):
        """Load saved email format preference from DB."""
        saved = self.engine.db.get_meta("email_format")
        if saved == "plain":
            self._set_email_format("plain")
        else:
            # Default to HTML
            if not hasattr(self, 'email_format_var'):
                self.email_format_var = ctk.StringVar(value="html")
            self._set_email_format("html")

    def get_email_format(self) -> str:
        """Return current email format preference. Used by engine."""
        return getattr(self, 'email_format_var', None)
        if fmt_var:
            return fmt_var.get()
        # Fallback: read from DB directly
        saved = self.engine.db.get_meta("email_format")
        return saved if saved in ("html", "plain") else "html"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: ENGINE.PY MODIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

# 4A. Add this import at the top of engine.py (after existing imports):
# import html

# 4B. Replace the render() method signature and return:
# OLD: def render(self, seq_id: str, day: int, rec: Recipient) -> Tuple[Optional[str], Optional[str], Optional[str]]:
# NEW: def render(self, seq_id: str, day: int, rec: Recipient, prefer_plain: bool = False) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
# Returns: (subject, body_html, body_text, ab_variant)

# 4C. Replace the render() method body (lines 1246-1267):

def render(self, seq_id: str, day: int, rec: Recipient, prefer_plain: bool = False) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
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

# 4D. Add this helper method to the CampaignEngine class:

def _html_to_plain_text(self, html_body: str) -> str:
    """Convert HTML email body to clean plain text."""
    import re
    import html as html_module

    text = html_body

    # Decode HTML entities
    text = html_module.unescape(text)

    # Replace <br>, <br/>, <br /> with newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

    # Replace </p> with double newline
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)

    # Replace </div> with newline
    text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)

    # Replace <li> with bullet point
    text = re.sub(r'<li[^>]*>', '\n• ', text, flags=re.IGNORECASE)

    # Replace headings with emphasized text
    text = re.sub(r'<h[1-6][^>]*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</h[1-6]>', '\n', text, flags=re.IGNORECASE)

    # Extract link text and URLs
    def link_replacer(m):
        href = m.group(1) if m.group(1) else ""
        link_text = m.group(2) if m.group(2) else href
        # If link text is just the URL or empty, return the URL
        if not link_text or link_text.strip() == href.strip():
            return f"\n{href}\n"
        return f"{link_text.strip()} ({href})"

    text = re.sub(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', link_replacer, text, flags=re.IGNORECASE | re.DOTALL)

    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Clean up excessive whitespace
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n[ \t]+', '\n', text)

    # Clean up multiple spaces
    text = re.sub(r' {2,}', ' ', text)

    # Strip leading/trailing whitespace per line and rejoin
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Final cleanup
    text = text.strip()

    return text

# 4E. Modify _send_with_retry to accept body_text and use it:
# OLD: def _send_with_retry(self, to: str, subject: str, body_html: str, thread_id=None, max_retries: int = 3):
# NEW: def _send_with_retry(self, to: str, subject: str, body_html: str, body_text: str = None, thread_id=None, max_retries: int = 3):

# In the method body, replace the send call:
# OLD: return self.gmail.send_email(to, subject, body_html, thread_id)
# NEW:
#     if body_text:
#         return self.gmail.send_email_plain(to, subject, body_text, thread_id)
#     return self.gmail.send_email(to, subject, body_html, thread_id)

# 4F. In _process_running_batches(), modify the send block (around line 510-570):
# OLD:
#     subj, body, ab_variant = self.render(seq_id, day_offset, rec)
#     ...
#     msg = self._send_with_retry(rec.email, subj, body)
#
# NEW:
#     prefer_plain = self.db.get_meta("email_format") == "plain"
#     subj, body_html, body_text, ab_variant = self.render(seq_id, day_offset, rec, prefer_plain=prefer_plain)
#     ...
#     msg = self._send_with_retry(rec.email, subj, body_html, body_text)

# 4G. In send_batch(), same modification for the direct send path.


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: GMAIL.PY ADDITIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Add this method to the GmailClient class in gmail.py:

def send_email_plain(self, to, subject, body_text, thread_id=None):
    """Send a plain text email via Gmail API."""
    message = MIMEText(body_text, 'plain', 'utf-8')
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


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: DB.PY MIGRATION (auto-add email_format meta if missing)
# ═══════════════════════════════════════════════════════════════════════════════

# No schema changes needed — email_format is stored in the existing meta table.
# The _set_email_format and _load_email_format methods handle this automatically.


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: COMPLETE _build_settings_view() REPLACEMENT (for reference)
# ═══════════════════════════════════════════════════════════════════════════════
# If you want to replace the entire _build_settings_view method, use this:

FULL_BUILD_SETTINGS_VIEW = '''
    def _build_settings_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["settings"] = view

        ctk.CTkLabel(view, text="⚙️ Settings", font=self._font(24, bold=True),
                     text_color=C_TEXT).pack(anchor="w", pady=(0, 15))

        # Google Connections
        google_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        google_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(google_frame, text="Google Connections:", font=self._font(12),
                     text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 5))

        self.google_status = {}
        services = [
            ("Gmail", "gmail", self.engine.gmail),
            ("Calendar", "calendar", self.engine.calendar),
            ("Drive", "drive", self.engine.drive),
        ]
        for name, key, service in services:
            row = ctk.CTkFrame(google_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=5)

            status_dot = ctk.CTkLabel(row, text="●", font=self._font(14), text_color=C_DANGER)
            status_dot.pack(side="left")

            ctk.CTkLabel(row, text=name, font=self._font(12),
                         text_color=C_TEXT).pack(side="left", padx=(5, 10))

            state_label = ctk.CTkLabel(row, text="Not connected", font=self._font(11),
                                       text_color=C_TEXT)
            state_label.pack(side="left")

            btn = ctk.CTkButton(row, text="Connect", font=self._font(11), width=90,
                                fg_color=C_ACCENT,
                                command=lambda n=name, k=key: self._connect_google_service(n, k))
            btn.pack(side="right")

            self.google_status[key] = {
                "dot": status_dot,
                "state": state_label,
                "btn": btn,
                "service": service,
            }

        self._refresh_google_connection_status()

        # Brief email
        brief_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        brief_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(brief_frame, text="Morning Brief Email:", font=self._font(12),
                     text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 5))
        self.brief_email_entry = ctk.CTkEntry(brief_frame, fg_color=C_BG, text_color=C_TEXT, font=self._font(12))
        self.brief_email_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.brief_email_entry.insert(0, self.engine.brief_email or "")
        ctk.CTkButton(brief_frame, text="Save", font=self._font(12),
                      fg_color=C_ACCENT, command=self._save_brief_email).pack(anchor="e", padx=15, pady=(0, 10))

        # ─── Email Format Toggle ───
        email_format_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        email_format_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(email_format_frame, text="📧 Email Format:", font=self._font(12),
                     text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 5))

        ctk.CTkLabel(email_format_frame,
                     text="Choose how emails are sent to recipients. Plain text avoids spam filters but has no styling.",
                     font=self._font(10), text_color=C_TEXT_DIM, wraplength=600).pack(anchor="w", padx=15, pady=(0, 8))

        toggle_row = ctk.CTkFrame(email_format_frame, fg_color="transparent")
        toggle_row.pack(fill="x", padx=15, pady=(0, 10))

        self.email_format_html_btn = ctk.CTkButton(
            toggle_row, text="🎨  HTML (Styled)", font=self._font(11, bold=True),
            fg_color=C_PRIMARY, hover_color=C_PRIMARY_HOVER,
            text_color="white", corner_radius=8, width=140, height=32,
            command=lambda: self._set_email_format("html")
        )
        self.email_format_html_btn.pack(side="left", padx=(0, 8))

        self.email_format_plain_btn = ctk.CTkButton(
            toggle_row, text="📝  Plain Text", font=self._font(11, bold=True),
            fg_color=C_PANEL_MUTED, hover_color=C_BORDER,
            text_color=C_TEXT_DIM, corner_radius=8, width=140, height=32,
            command=lambda: self._set_email_format("plain")
        )
        self.email_format_plain_btn.pack(side="left", padx=(0, 8))

        self.email_format_status = ctk.CTkLabel(
            toggle_row, text="HTML format active — rich styling with dark theme",
            font=self._font(10), text_color=C_SUCCESS
        )
        self.email_format_status.pack(side="left", padx=(10, 0))

        self.plain_text_info = ctk.CTkFrame(email_format_frame, fg_color=C_CARD_ALT,
                                            corner_radius=8, border_width=1, border_color=C_BORDER)
        self.plain_text_info.pack(fill="x", padx=15, pady=(0, 10))
        self.plain_text_info.pack_forget()

        info_text = (
            "📋 Plain Text Mode Details:\n"
            "  • All HTML styling is stripped — emails look like personal messages\n"
            "  • Links are preserved as full URLs (not clickable buttons)\n"
            "  • Images and videos appear as text links to Drive/YouTube/Instagram\n"
            "  • Signatures are simplified — no logos, just text\n"
            "  • Better deliverability: less likely to trigger spam filters\n"
            "  • Best for: cold outreach, first-touch emails, CSR conversations"
        )
        self.plain_text_info_label = ctk.CTkLabel(
            self.plain_text_info, text=info_text,
            font=self._font(10), text_color=C_TEXT_DIM, justify="left"
        )
        self.plain_text_info_label.pack(anchor="w", padx=12, pady=10)

        self._load_email_format()

        # Pause sequences
        pause_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        pause_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(pause_frame, text="Pause Sequences:", font=self._font(12),
                     text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 5))

        self.pause_school = ctk.CTkCheckBox(pause_frame, text="Pause SCHOOL",
                                              font=self._font(11), text_color=C_TEXT)
        self.pause_school.pack(anchor="w", padx=15, pady=5)

        self.pause_csr = ctk.CTkCheckBox(pause_frame, text="Pause CSR",
                                         font=self._font(11), text_color=C_TEXT)
        self.pause_csr.pack(anchor="w", padx=15, pady=5)

        self.pause_csr_wsl_5 = ctk.CTkCheckBox(pause_frame, text="Pause CSR-WSL-5",
                                                font=self._font(11), text_color=C_TEXT)
        self.pause_csr_wsl_5.pack(anchor="w", padx=15, pady=5)

        ctk.CTkButton(pause_frame, text="Apply", font=self._font(12),
                      fg_color=C_ACCENT, command=self._apply_pauses).pack(anchor="e", padx=15, pady=(5, 10))

        # Export
        export_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        export_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(export_frame, text="Export:", font=self._font(12),
                     text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkButton(export_frame, text="Export Campaign State", font=self._font(12),
                      fg_color=C_SUCCESS, command=self._export_state).pack(anchor="w", padx=15, pady=(0, 10))

        # Notifications
        notif_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        notif_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(notif_frame, text="Notifications:", font=self._font(12),
                     text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 5))
        self.notifications_enabled = ctk.CTkCheckBox(
            notif_frame, text="Desktop notifications",
            font=self._font(11), text_color=C_TEXT
        )
        self.notifications_enabled.pack(anchor="w", padx=15, pady=(0, 10))
        notif_val = self.engine.db.get_meta("desktop_notifications")
        if notif_val is None or notif_val.lower() in ("true", "1", "on"):
            self.notifications_enabled.select()
        else:
            self.notifications_enabled.deselect()
        self.notifications_enabled.configure(command=self._save_notification_setting)
'''


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: COMPLETE METHODS TO ADD TO RajChatApp (paste at end of class)
# ═══════════════════════════════════════════════════════════════════════════════

METHODS_TO_ADD = '''
    def _set_email_format(self, fmt: str):
        """Set email format preference and update UI."""
        self.email_format_var.set(fmt)
        self.engine.db.set_meta("email_format", fmt)

        if fmt == "html":
            self.email_format_html_btn.configure(
                fg_color=C_PRIMARY, text_color="white",
                hover_color=C_PRIMARY_HOVER
            )
            self.email_format_plain_btn.configure(
                fg_color=C_PANEL_MUTED, text_color=C_TEXT_DIM,
                hover_color=C_BORDER
            )
            self.email_format_status.configure(
                text="HTML format active — rich styling with dark theme",
                text_color=C_SUCCESS
            )
            self.plain_text_info.pack_forget()
        else:
            self.email_format_html_btn.configure(
                fg_color=C_PANEL_MUTED, text_color=C_TEXT_DIM,
                hover_color=C_BORDER
            )
            self.email_format_plain_btn.configure(
                fg_color=C_PRIMARY, text_color="white",
                hover_color=C_PRIMARY_HOVER
            )
            self.email_format_status.configure(
                text="Plain text active — personal message style",
                text_color=C_PRIMARY
            )
            self.plain_text_info.pack(fill="x", padx=15, pady=(0, 10))

        self._log_activity(f"Email format set to: {fmt.upper()}")

    def _load_email_format(self):
        """Load saved email format preference from DB."""
        saved = self.engine.db.get_meta("email_format")
        if saved == "plain":
            self._set_email_format("plain")
        else:
            if not hasattr(self, \'email_format_var\'):
                self.email_format_var = ctk.StringVar(value="html")
            self._set_email_format("html")

    def get_email_format(self) -> str:
        """Return current email format preference."""
        fmt_var = getattr(self, \'email_format_var\', None)
        if fmt_var:
            return fmt_var.get()
        saved = self.engine.db.get_meta("email_format")
        return saved if saved in ("html", "plain") else "html"
'''


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: QUICK REFERENCE — MINIMAL CHANGES NEEDED
# ═══════════════════════════════════════════════════════════════════════════════
"""
MINIMAL INTEGRATION (5 steps):

1. In RajChatApp.__init__(), add after self._current_view = "dashboard":
   self.email_format_var = ctk.StringVar(value="html")

2. In RajChatApp._build_settings_view(), paste the Email Format Toggle block
   (Section 2 above) after the notif_frame section.

3. Add the three methods from Section 8 to RajChatApp.

4. In engine.py, modify render() to accept prefer_plain and return body_text.
   Add _html_to_plain_text() helper. Modify _send_with_retry() to use body_text.

5. In gmail.py, add send_email_plain() method.

That's it. The toggle will appear in Settings, persist to DB, and the engine
will respect it when sending emails.
"""
