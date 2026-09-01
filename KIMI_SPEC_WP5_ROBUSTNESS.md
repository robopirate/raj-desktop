# KIMI SPEC — WP5: Office-PC Robustness

## ROLE: Senior Developer
You are the Senior Developer. I am the System Architect. Do not redesign. Do not refactor. Only execute the exact tasks listed below.

## PROJECT CONTEXT
- **Project path:** `C:\Users\itsom\OneDrive\Documents\GitHub\raj-desktop`
- **Python:** 3.12+, project venv at `.venv\Scripts\` (run everything as `.venv\Scripts\python`)
- **Runtime:** Windows 11, single-user desktop app (Flask + waitress on `127.0.0.1:5555`, pywebview shell)
- **Current state:** App works. 2 email sequences (school, csr-wsl-5), 10 templates regenerated and LOCKED in the live DB at `%LOCALAPPDATA%\RajData\campaign_data.db`. `test_raj.py` passes 6/6.
- **Critical constraints:**
  - DO NOT touch `SEQUENCES`, email template content, or Drive links in `engine.py` — they were just fixed and the DB templates are locked.
  - DO NOT touch `rewritten_email_templates.py`.
  - DO NOT change any API route shapes — the frontend depends on them.
  - The live DB is at `%LOCALAPPDATA%\RajData\campaign_data.db` (NOT the project-dir `campaign_data.db` — that one is a stale leftover).

## YOUR TASKS (execute in order)

### TASK 1: Fix Windows boot autostart shortcut target
- **File:** `autostart.py`
- **Problem:** `add_to_startup()` creates `Raj.lnk` pointing directly at `desktop.py`. This relies on Windows `.py` file association and the SYSTEM Python — it ignores the project `.venv`, so on boot it can fail or run with wrong/missing packages. It also opens a console window.
- **Change:** In `add_to_startup()`, resolve the target as:
  1. If `<project_root>\.venv\Scripts\pythonw.exe` exists → shortcut `TargetPath` = that exe, and set `lnk.Arguments = `"<project_root>\desktop.py"`` in the VBS.
  2. Else fall back to current behavior (shortcut to `desktop.py`).
  - Update `_create_shortcut_vbs()` to accept an optional `arguments` string and emit `lnk.Arguments = "..."` when provided.
  - `pythonw.exe` (not `python.exe`) so no console window appears on boot.
  - Keep `is_autostart_enabled()` and `remove_from_startup()` unchanged.
- **Verify:** `.venv\Scripts\python -c "from autostart import add_to_startup, is_autostart_enabled, remove_from_startup; print(add_to_startup()); print(is_autostart_enabled()); print(remove_from_startup())"` → `True`, `True`, `True`. Inspect the created `.lnk` before removing: TargetPath must be the venv `pythonw.exe`.

### TASK 2: Auto-resume interrupted sends on engine start
- **File:** `engine.py`
- **Problem:** When Gmail rate-limits a batch mid-send, remaining recipients are saved to `pending_resumes` (see ~line 1474) — but resuming them requires a manual chat command (`resume batch ...`, handler ~line 2707). If the office PC reboots or the app restarts, those staged sends sit forever.
- **Change:** In `CampaignEngine.start()`, AFTER template validation, add an auto-resume step:
  - Query `pending_resumes WHERE status='pending'` grouped by `(sequence_id, day)` (same query as ~line 2707).
  - If none: log `[Engine] No pending resumes` and continue.
  - If rows exist: log how many, then resume them by calling the EXISTING resume logic (the same code path the manual `resume batch` command uses — factor it into a helper like `_resume_pending(seq_id, day)` if the manual command and this auto-path need to share it).
  - The resume MUST respect the existing daily send cap (`daily_send_cap` meta) and send gap (`send_gap_seconds` meta) — do not bypass them. If the cap is hit, leave the rest as `status='pending'` for the next start; log that.
  - Wrap the whole auto-resume in try/except so a failure can never prevent `start()` from completing.
- **Verify:** `.venv\Scripts\python -c "from engine import CampaignEngine; print('import ok')"` and `python test_raj.py` (via `.venv\Scripts\python`) still passes 6/6.

### TASK 3: Pre-send email validation (syntax + MX) at import
- **Files:** NEW `email_validator.py`, `smart_importer.py`, `web/app.py`, `requirements.txt`
- **Problem:** Bad emails (typos, dead domains) are only discovered AFTER sending, as bounces — which trips the bounce guard and hurts sender reputation. Validation must happen at import time.
- **Change:**
  1. `requirements.txt`: add `dnspython>=2.4.0`.
  2. NEW `email_validator.py`:
     ```python
     """email_validator.py — syntax + MX validation for imported leads."""
     import re, dns.resolver
     from functools import lru_cache

     SYNTAX = re.compile(r'^[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}$')

     @lru_cache(maxsize=2048)
     def _domain_has_mx(domain: str) -> bool:
         try:
             answers = dns.resolver.resolve(domain, 'MX', lifetime=4.0)
             return len(answers) > 0
         except Exception:
             # Fall back to A record — some domains receive mail without MX
             try:
                 dns.resolver.resolve(domain, 'A', lifetime=4.0)
                 return True
             except Exception:
                 return False

     def validate_email(addr: str) -> tuple[bool, str]:
         """Return (ok, reason). reason is '' when ok."""
         addr = (addr or '').strip()
         if not addr or not SYNTAX.match(addr):
             return False, 'bad-syntax'
         domain = addr.rsplit('@', 1)[1].lower()
         if not _domain_has_mx(domain):
             return False, 'no-mx'
         return True, ''
     ```
  3. `smart_importer.py` — in `import_to_pool()` (~line 501): after extracting each email, call `validate_email()`. If invalid, skip the row and count it as skipped with the reason (use the existing skip/reporting mechanism — do NOT invent a new result shape). Wrap validation in try/except: on any validator error, treat the email as VALID (never block imports on a DNS outage).
  4. `web/app.py` — in `_normalize_lead_row()` (~line 808): same validation, same rule (validator error → treat as valid). Invalid rows keep flowing through the existing rejection path with reason `bad-syntax` / `no-mx`.
- **Verify:**
  ```bash
  .venv\Scripts\pip install dnspython
  .venv\Scripts\python -c "from email_validator import validate_email; print(validate_email('om@robopirate.in')); print(validate_email('bad-email')); print(validate_email('x@thisdomaindoesnotexist12345.com'))"
  ```
  Expected: `(True, '')`, `(False, 'bad-syntax')`, `(False, 'no-mx')`.
  Then `.venv\Scripts\python test_raj.py` → 6/6 pass.

## TESTING COMMANDS (run after ALL tasks)
```bash
.venv\Scripts\python -m py_compile autostart.py engine.py email_validator.py smart_importer.py web/app.py
.venv\Scripts\python test_raj.py
```
Both must succeed. `test_raj.py` must show 6/6.

## RULES
- Do not ask clarifying questions. Execute.
- Do not change anything not listed above.
- If a test fails, fix it before moving to the next task.
- Commit after every task with a descriptive message:
  - `WP5-T1: autostart shortcut targets venv pythonw + desktop.py arg`
  - `WP5-T2: auto-resume pending_resumes on engine start, respects cap/gap`
  - `WP5-T3: syntax+MX email validation at import (dnspython)`
- Do NOT regenerate or delete DB templates. Do NOT touch the live DB.

## HANDOFF BACK
When done, report: files changed, test output, and any deviation from this spec. The Architect (Kimi Work) will then run independent verification.
