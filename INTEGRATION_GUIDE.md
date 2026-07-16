# Plain Text Email Toggle — Integration Guide

## Overview
This adds a **Settings UI toggle** to switch between HTML and Plain Text email formats. The preference is persisted to the SQLite DB and respected by the engine when sending emails.

---

## Files Modified

| File | Change Type | Description |
|------|-------------|-------------|
| `raj_chat.py` | Add | UI toggle in Settings, format preference state |
| `engine.py` | Modify | `render()` returns plain text, `_send_with_retry()` uses it |
| `gmail.py` | Add | `send_email_plain()` method for plain text sends |

---

## Integration Steps (10 minutes)

### Step 1: raj_chat.py — Add state variable

In `RajChatApp.__init__()`, after the line:
```python
self._current_view = "dashboard"
```

Add:
```python
self.email_format_var = ctk.StringVar(value="html")
```

---

### Step 2: raj_chat.py — Insert UI into Settings view

In `_build_settings_view()`, after the `notif_frame` section (after the notifications checkbox), paste the **Email Format Toggle block** from `raj_chat_settings_patch.py`.

The block starts with:
```python
        # ─── Email Format Toggle ───
        email_format_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
```

---

### Step 3: raj_chat.py — Add helper methods

At the **end of the `RajChatApp` class** (before the final closing of the class), paste the three methods from `raj_chat_settings_patch.py`:

- `_set_email_format(self, fmt: str)`
- `_load_email_format(self)`
- `get_email_format(self) -> str`

---

### Step 4: engine.py — Add import

At the top of `engine.py`, add:
```python
import html
```

---

### Step 5: engine.py — Replace render() method

Replace the existing `render()` method with the new version from `engine_plaintext_patch.py` that accepts `prefer_plain` and returns `(subject, body_html, body_text, ab_variant)`.

---

### Step 6: engine.py — Add _html_to_plain_text()

Add the `_html_to_plain_text()` helper method after `render()`.

---

### Step 7: engine.py — Modify _send_with_retry()

Replace the `_send_with_retry()` method signature and body with the version from `engine_plaintext_patch.py` that accepts `body_text` and routes to `send_email_plain()` when provided.

---

### Step 8: engine.py — Update send blocks

In `_process_running_batches()`, `send_batch()`, `trial_send()`, and `test_send()`, update the calls to:
1. Pass `prefer_plain` to `render()`
2. Pass `body_text` to `_send_with_retry()`

Exact replacements are documented in `engine_plaintext_patch.py` with "OLD CODE" / "NEW CODE" markers.

---

### Step 9: gmail.py — Add send_email_plain()

Paste the `send_email_plain()` method from `gmail_plaintext_patch.py` into the `GmailClient` class, after the existing `send_email()` method.

---

### Step 10: Test

1. Launch the app
2. Go to **Settings** tab
3. Toggle between **HTML** and **Plain Text**
4. Verify the info panel appears/disappears
5. Send a test email — check Gmail sent folder to confirm format

---

## How It Works

```
User toggles format in Settings
        ↓
Preference saved to DB meta table (key: "email_format")
        ↓
Engine reads preference before each send
        ↓
render(seq_id, day, rec, prefer_plain=True) → generates body_text
        ↓
_send_with_retry(rec.email, subj, body_html, body_text)
        ↓
If body_text exists → gmail.send_email_plain()
If body_text is None → gmail.send_email() [HTML]
```

---

## No Schema Changes Required

The preference uses the existing `meta` table:
```sql
INSERT INTO meta (key, value) VALUES ('email_format', 'plain')
ON CONFLICT(key) DO UPDATE SET value=excluded.value;
```

---

## Visual Result

The Settings tab will show:

```
⚙️ Settings

[Google Connections]
...

[Morning Brief Email]
...

📧 Email Format:
Choose how emails are sent to recipients. Plain text avoids spam filters but has no styling.

[🎨 HTML (Styled)]  [📝 Plain Text]     HTML format active — rich styling with dark theme

📋 Plain Text Mode Details:
  • All HTML styling is stripped — emails look like personal messages
  • Links are preserved as full URLs (not clickable buttons)
  • Images and videos appear as text links to Drive/YouTube/Instagram
  • Signatures are simplified — no logos, just text
  • Better deliverability: less likely to trigger spam filters
  • Best for: cold outreach, first-touch emails, CSR conversations

[Pause Sequences]
...
```
