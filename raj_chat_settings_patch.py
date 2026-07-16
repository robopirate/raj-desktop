"""
raj_chat.py — Settings View Patch for Plain Text Email Toggle
===============================================================
This file contains ONLY the code to add/modify in raj_chat.py.

STEP 1: In RajChatApp.__init__(), add after line ~137:
    self.email_format_var = ctk.StringVar(value="html")

STEP 2: In RajChatApp._build_settings_view(), insert the Email Format section
    after the notif_frame section (after line ~3232).

STEP 3: Add the three methods at the end of the RajChatApp class.
"""

# ============================================================================
# STEP 1: Add to __init__ (after self._current_view = "dashboard" line ~137)
# ============================================================================

# self.email_format_var = ctk.StringVar(value="html")


# ============================================================================
# STEP 2: Insert into _build_settings_view() — after notif_frame, before
#         _save_notification_setting method
# ============================================================================

# Paste this block:

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


# ============================================================================
# STEP 3: Add these three methods to RajChatApp class (at the end)
# ============================================================================

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
            if not hasattr(self, 'email_format_var'):
                self.email_format_var = ctk.StringVar(value="html")
            self._set_email_format("html")

    def get_email_format(self) -> str:
        """Return current email format preference."""
        fmt_var = getattr(self, 'email_format_var', None)
        if fmt_var:
            return fmt_var.get()
        saved = self.engine.db.get_meta("email_format")
        return saved if saved in ("html", "plain") else "html"
