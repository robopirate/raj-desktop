# AGENTS.md — Raj AI Gmail Agent

> Agent-facing guide for the Raj codebase. This project is a single-user desktop email-automation agent built by RoboPirate Technologies. If you are modifying code here, read this first.

---

## 1. Project Overview

**Raj** is an AI-powered Gmail outreach agent for Indian education (SCHOOL) and corporate CSR (CSR-WSL-5) campaigns. It automates the full cold-email lifecycle: lead import → batch creation → staggered sending → auto-advance follow-ups (D1→D3→D5→D7→D10) → reply scanning → sentiment analysis → AI-drafted replies.

Key facts:

- **Current version:** v5.0.0 (defined as `VERSION` in `engine.py`); v4.3 (analytics charts) is the last stable baseline.
- **Runtime modes:**
  - **Desktop (primary):** `desktop.py` runs the backend (Flask app served by **waitress WSGI**) and wraps the web UI in a `pywebview` window.
  - **Web browser:** `web_start.py` runs the same backend and opens it in the default browser.
  - **Legacy Tkinter UI:** removed (July 2026). `main.py` is now a shim that launches `desktop.py`.
- **Database location:** the live SQLite DB lives OUTSIDE OneDrive at `%LOCALAPPDATA%\RajData\campaign_data.db` (OneDrive+WAL corrupts databases). `RAJ_DB_PATH` env var overrides. Nightly backup at 23:00 into the OneDrive-synced `backups/` folder (`backup_db.py`, keeps 14 days).
- **Target market:** Indian private schools and corporate CSR managers; timezone hard-coded to `Asia/Kolkata`.
- **AI backend:** Local Ollama instance at `http://localhost:11434`, model `gpt-oss:20b-cloud`.
- **Owner / author:** Om (RoboPirate). Commit history and documentation use English.

---

## 2. Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Web backend | Flask 3.x, Flask-CORS, served by **waitress** (production WSGI) |
| New desktop UI | pywebview 5.x wrapping the Flask web app |
| Web frontend | Vanilla JS + Tailwind CSS (loaded from CDN) |
| Database | SQLite (`%LOCALAPPDATA%\RajData\campaign_data.db`, `raj_memory.db`), WAL mode enabled |
| Email | Gmail API v1 via `google-api-python-client` |
| Calendar / Drive | Google Calendar API, Google Drive API |
| AI | Ollama local LLM (`gpt-oss:20b-cloud`) |
| Tracking | Built-in `http.server` pixel/redirect tracker (`tracking_server.py`) |
| Notifications | `plyer` desktop toasts |
| System tray | `pystray` + Pillow |
| Import parsing | `openpyxl` for Excel, stdlib `csv` for CSV/TSV |

Important external dependency: **Ollama must be running locally** for AI features (sentiment, reply drafting, chat). If Ollama is down, AI steps are skipped gracefully.

---

## 3. Repository Layout

```
raj-desktop/
├── desktop.py                 # Primary entry point (waitress + pywebview desktop)
├── web_start.py               # Browser-based entry point
├── main.py                    # Shim → launches desktop.py (legacy UI removed)
├── START.bat                  # Windows launcher: creates .venv and runs desktop.py
├── requirements.txt           # pip dependencies (no pyproject.toml / setup.py)
│
├── engine.py                  # Core CampaignEngine (batches, sends, scans, auto-advance)
├── rewritten_email_templates.py # Active email copy: HTML + plain-text generators, subjects, preheaders
├── regenerate_templates.py    # Regenerate DB templates + export snapshots to export/emails/
├── db.py                      # SQLite Database class + schema + migrations (local app-data path)
├── backup_db.py               # Nightly SQLite backup into OneDrive-synced backups/
├── gmail.py                   # GmailClient (OAuth, send, draft, search)
├── raj_brain.py               # AI agent brain: memory, reasoning, sentiment, drafting
├── smart_importer.py          # CSV/Excel lead importer with auto-detect columns
│
├── web/                       # New web UI
│   ├── app.py                 # Flask REST backend (waitress-served)
│   ├── templates/index.html   # Single-page web app
│   └── static/{css,js}/       # Frontend assets
│
├── calendar_integration.py    # Google Calendar OAuth + meeting creation
├── drive_integration.py       # Google Drive OAuth + file listing/upload
├── tracking_server.py         # Email open/click tracking server
├── notifications.py           # Desktop toast notifications
├── tray.py                    # System-tray manager
├── state.py                   # Persistent state.json (window, theme, settings)
├── lock.py                    # Single-instance guard via TCP port
├── autostart.py               # Windows startup shortcut helper
│
├── test_raj.py                # Feature-verification test script
├── credentials.json           # Google OAuth client secrets (gitignored, required)
├── token.pickle               # Gmail OAuth token (gitignored)
├── calendar_token.pickle      # Calendar OAuth token (gitignored)
├── drive_token.pickle         # Drive OAuth token (gitignored)
└── state.json                 # UI state (gitignored)
```

**Note:** `ARCHITECTURE_LOCK.txt` and `UI_CHECKLIST.txt` are **Microsoft Word `.docx` files** saved with a `.txt` extension. Do not treat them as plain text.

---

## 4. How to Run

All commands assume a Python 3.12+ environment on Windows (the project is developed on Windows).

### 4.1 Recommended desktop run

```bat
START.bat
```

`START.bat` will:

1. Create `.venv` if it does not exist.
2. Install packages from `requirements.txt` if imports fail.
3. Verify the database.
4. Launch `desktop.py`.

### 4.2 Manual runs

```bash
# New desktop app (waitress backend + pywebview window)
python desktop.py

# Browser-only web UI
python web_start.py

# Feature verification tests
python test_raj.py

# Backend directly
python -m web.app

# One-off DB backup
python backup_db.py
```

The backend binds to `127.0.0.1:5555` by default.

### 4.3 Killing stale processes (important)

Because the desktop app launches the backend in a background thread and multiple entry points can start Python, stale `python.exe` processes sometimes keep port `5555` (or the single-instance lock port `55555`) bound and serve old code.

Before restarting Raj after code changes — or if the window shows old UI/errors — run:

```bat
taskkill //F //IM python.exe
taskkill //F //IM pythonw.exe
```

Then restart normally:

```bat
.venv\Scripts\python desktop.py
```

If port `5555` is still reported as in use, wait a few seconds and try again, or find the lingering process with:

```bat
netstat -ano | findstr :5555
```

### 4.4 First-time setup

1. Obtain a Gmail API OAuth client from Google Cloud Console.
2. Download the JSON and save it as `credentials.json` in the project root.
3. Install Ollama locally and pull `gpt-oss:20b-cloud` (or update `ollama_url` / model references if using a different model).
4. Run `START.bat` or `python desktop.py` and complete OAuth when prompted.

---

## 5. Code Organization & Key Modules

### 5.1 `engine.py` — CampaignEngine

The background orchestrator. Runs in a daemon thread once `engine.start()` is called.

Key responsibilities:

- Process running batches (`_process_running_batches`).
- Create batches from the recipient pool (`create_batch_from_pool`).
- Auto-advance sequences D1→D3→D5→D7→D10.
- Scan bounces and replies on scheduled intervals.
- Draft AI replies end-of-day.
- Send morning brief emails.
- Check emergency STOP/RESUME commands.
- Validate/repair templates on startup.
- Enforce **daily send cap** (`daily_send_cap` meta, default 100), **send gap** (`send_gap_seconds` meta, default 45, min 30), and the **bounce guard** (pauses sends if bounces exceed 10% of today's sends).
- Nightly DB backup at 23:00 (`_check_backup`).

Sequences are defined at module level in `SEQUENCES` (the legacy `csr` sequence was retired in July 2026 — only two sequences remain active):

```python
SEQUENCES = {
    "school":      {"days": [1, 3, 5, 7, 10], "template_prefix": "SCHOOL EMAIL ", ...},
    "csr-wsl-5":   {"days": [1, 3, 5, 7, 10], "template_prefix": "CSR-WSL-5 EMAIL ", ...},
}
```

**Email templates** live in `rewritten_email_templates.py` (HTML + plain-text generators per sequence/day, plus `REWRITTEN_SUBJECTS` and `PREHEADERS` for inbox preview text). `engine.generate_template()` wraps the content in the shared `HTML_TEMPLATE` (WE Smart Lab branding: pink `#FF2E88` header with the WSL logo from Google Drive, yellow→purple divider, yellow `#FFD400` CTA buttons). The `templates` DB table is the source of truth at send time; `export/emails/<seq>/` holds dated HTML+TXT snapshots for review (regenerated by `regenerate_templates.py`). Each template also stores a `format` (`html`/`plain`) — the editor's HTML/Plain toggle is honored by Send Test, Trial sends, and (when saved) real campaign sends. Plain-mode sends go out as minimal personal-style HTML (clickable link labels, no raw URLs) with a text fallback (`_text_to_simple_html`).

**Personalization:** `render()` resolves a per-recipient greeting — person first name from the name field (titles stripped, role/org words rejected), else from the email local part (`first.last@` pattern, role accounts excluded), else role fallback ("Principal" / "CSR Head"). `{{PRINCIPAL_NAME}}`/`{{CSR_HEAD_NAME}}` resolve the same way.

Timing constants:

- `BOUNCE_INTERVAL = 6` hours.
- `REPLY_INTERVAL = 60` minutes.
- `EMERGENCY_INTERVAL = 15` minutes.
- EOD reply drafting at 19:00 IST; morning brief at 08:00 IST; DB backup at 23:00 IST.
- Send gap and daily cap are runtime settings (meta keys `send_gap_seconds`, `daily_send_cap`), editable in Settings → Campaign Settings.

### 5.2 `db.py` — Database

SQLite database wrapper. Key tables:

- `recipients` — lead pool (`sequence_id`, `email`, `name`, `org`, `sub_pool`, `batched`).
- `batches` — campaign batches (`status`, `scheduled_at`, `day_offset`, `parent_batch_id`, `deleted_at`).
- `batch_recipients` — many-to-many with per-recipient status (`pending`, `sent`, `failed`, `bounced`, `replied`, `stopped`, etc.).
- `templates` — email templates per `(sequence_id, day)`, supports A/B test fields (`subject_b`, `ab_test`, `ab_split`).
- `sends` — sent-email log with open/click timestamps and `ab_variant`.
- `archived_sends` — old send records moved here by the re-campaign reset (recoverable).
- `replies` — inbound replies with sentiment, summary, draft.
- `blacklist` — suppressed emails.
- `engagement_events` — open/click tracking events.
- `pending_resumes` — crash-recovery state.
- `meta` — key/value settings.
- `audit_log` — action history.

`_migrate_schema()` adds missing columns/tables automatically on startup. Pool helpers: `pool_stats()` (segment totals), `reset_pool_for_recampaign()` (re-campaign reset — archives sends, resets `batched=0`, never touches replied/blacklisted).

### 5.3 `gmail.py` — GmailClient

- Desktop OAuth 2.0 flow using `credentials.json` via `flow.run_local_server(port=0, open_browser=True)`.
- Refresh-token fallback with bounded timeout, pickle-error handling, and explicit credential paths.
- Scope: `https://www.googleapis.com/auth/gmail.modify` (code), although internal docs sometimes reference `gmail.send`.
- Token stored in `token.pickle`.
- Supports HTML-only or multipart HTML+plain-text sends/drafts.
- Provides `send_email`, `draft_email`, `create_scheduled_draft`, `search_messages`, `get_draft_full` (now returns `text_body` too), and message-reading helpers.

### 5.4 `raj_brain.py` — Raj AI Brain

- `RajMemory` persists interactions, decisions, and learnings to `raj_memory.db`.
- `RajReasoning` queries Ollama for situation analysis.
- Sentiment analysis returns `positive` / `neutral` / `hostile`.
- `draft_reply` and `summarize_reply` generate Gmail draft replies.
- `chat` powers the interactive Raj chatbot.

### 5.5 `smart_importer.py`

Auto-detects columns from CSV/Excel/TXT and maps them to `email`, `name`, `org`, phone, city, etc. Called by the engine for file imports.

### 5.6 `tracking_server.py`

Lightweight `http.server` thread that serves a 1x1 tracking pixel and link redirects, recording opens/clicks to `engagement_events`. The engine starts this automatically.

- Binds `127.0.0.1` by default; set `tracking_public_url` meta to enable external tracking URLs.
- HMAC-signs tracking tokens and validates redirect destinations before recording clicks.
- Tracking pixels/links are only injected when `tracker.base_url` is set.

### 5.7 `raj_guard.py`

Background daemon that periodically scans source files for known bug patterns and auto-applies small fixes (e.g. restoring an empty `HTML_TEMPLATE`). It is started from `main.py`; treat its behavior as non-blocking and defensive.

---

## 6. REST API (Flask, waitress-served)

The new UI talks to `web/app.py`. Base URL: `http://127.0.0.1:5555`.

Representative endpoints:

- `GET /api/health` — backend status.
- `GET /api/dashboard/summary` — campaign KPIs.
- `GET /api/dashboard/send-stats` — daily cap usage, gap, queue estimate, warm-up ramp suggestion, bounce-guard state.
- `GET /api/dashboard/pipeline` — pipeline + day-wise breakdown.
- `GET /api/batches` — list batches.
- `POST /api/batches` — create batch from pool.
- `POST /api/batches/<id>/start|pause` — control batch.
- `GET /api/pools/stats` — segment totals (total/available/contacted/blacklisted/replied).
- `POST /api/pools/<seq>/reset-recampaign` — re-campaign reset for a segment.
- `POST /api/leads/import/file` — upload CSV/Excel.
- `POST /api/leads/import/paste` — paste preview.
- `POST /api/leads/import/confirm` — confirm pasted leads.
- `GET /api/templates` / `GET /api/templates/<seq>/<day>` — templates.
- `PUT /api/templates/<seq>/<day>` — update template (lock state is stored on the `templates.locked` column; legacy `meta` lock keys are auto-migrated).
- `POST /api/templates/<seq>/<day>/test` — test send; honors `format`/`subject`/`body` overrides from the editor toggle.
- `POST /api/templates/<seq>/trial` — full-sequence trial; honors the editor's HTML/Plain toggle.
- `GET /api/replies` — reply inbox.
- `POST /api/replies/<id>/draft|send-draft|update-draft` — reply drafting.
- `GET /api/blacklist` / `POST /api/blacklist` / `DELETE /api/blacklist/<email>`.
- `GET /api/settings/campaign` / `POST` — brief email, default sender, sequence pauses, `send_gap_seconds`, `daily_send_cap`.
- `GET /api/settings/deliverability` — live SPF/DKIM/DMARC check for the sending domain.
- `POST /api/engine/pause|resume`.
- `POST /api/connect/<gmail|calendar|drive>` — trigger OAuth.

All JSON responses use the shape:

```json
{"success": true, "data": {...}, "error": null}
```

---

## 7. Build, Test & Release

### 7.1 Build

There is no formal build step. Use `START.bat` or create a virtual environment manually:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 7.2 Test

The only test file is `test_raj.py`. It is a standalone verification script, not a `pytest` suite. Run it directly:

```bash
python test_raj.py
```

It checks database schema, sub-pool support, soft delete, personalization (greeting resolution, email extraction), plain-link conversion, pool stats, re-campaign reset on a temp DB, and import-pipeline method signatures.

There is no CI/CD pipeline, no `pytest.ini`, and no automated linting.

### 7.3 Release workflow

The project uses a lightweight manual release process (documented in `06_Market_SOP.md`):

1. Update the version string in `main.py` / relevant entry point.
2. Run `test_raj.py`.
3. Test desktop and web modes with real data.
4. Update README / documentation.
5. Tag: `git tag -a v4.3 -m "Analytics charts"`
6. Push tags and create GitHub release notes.

---

## 8. Code Style Guidelines

- **Language:** English for all comments, docstrings, and documentation.
- **Docstrings:** Use triple-quoted module/function docstrings; many modules include a one-line summary at the top.
- **Type hints:** Used in newer files (`desktop.py`, `state.py`, `tray.py`) but inconsistently across older modules.
- **Emoji:** Allowed in UI strings and log messages (e.g. `📊 Dashboard`, `🤖 Raj`).
- **String formatting:** Mixed use of f-strings and `.format()`; prefer f-strings for new code.
- **Database access:** Use parameterized queries; the project relies on `sqlite3.Row` for dict-like rows.
- **Threading:** Heavy use of `threading.Thread(daemon=True)` for background work (engine loop, Flask, tray, OAuth flows). Ensure new background code is daemonic and handles `_running` / `_paused` flags.

There is no configured formatter (Black/Ruff) or linter. Do not introduce one unless explicitly requested.

---

## 9. Testing Instructions

Before committing changes, verify:

1. **Schema compatibility:** Run `python test_raj.py` and ensure database migrations still work.
2. **One-time repairs:** After pulling these fixes on an existing DB, run `python repair_db_phase6.py`.
3. **Desktop launch:** Run `python desktop.py`, confirm the backend starts on `:5555` (waitress), the `/api/health` `version` matches `engine.py`, and the window opens.
4. **Web launch:** Run `python web_start.py` and confirm the dashboard loads in the browser.
5. **OAuth not required for pure UI work:** The app starts without Gmail auth, but auth-related pages will show a "Connect Gmail" state.

If you add new database columns, add the corresponding `ALTER TABLE` migration in `db.py::_migrate_schema()`.

---

## 10. Security Considerations

- **Single-user desktop app:** No RBAC, sessions, or multi-user support.
- **OAuth tokens** are stored unencrypted in local `.pickle` files (`token.pickle`, `calendar_token.pickle`, `drive_token.pickle`).
- **`credentials.json`** is required and gitignored. Never commit it.
- **PII** (emails, names, orgs, reply bodies) is stored in plaintext SQLite in `%LOCALAPPDATA%\RajData`.
- **Gmail scope** in code is `gmail.modify`, which is broader than `gmail.send`; be aware when auditing or documenting.
- **Blacklisting:** Hard bounces, hostile replies, and STOP requests auto-blacklist. The own domain (`robopirate.in`) is protected from blacklisting.
- **Emergency commands:** Emails with subjects `STOP SCHOOL`, `STOP CSR`, `STOP ALL`, `RESUME ...` from the owner address can pause/resume sequences.
- **Backend** runs on localhost only (`127.0.0.1:5555`). Do not expose it to the network without a proper WSGI server (waitress is now used; still bind to localhost).

---

## 11. Common Gotchas

- **`desktop.py` vs `main.py`:** `START.bat` runs `desktop.py`. `main.py` is only a shim. The legacy Tkinter UI (`raj_chat.py`) was deleted in July 2026.
- **`.txt` Word files:** `ARCHITECTURE_LOCK.txt` and `UI_CHECKLIST.txt` are `.docx` binaries. Open them with a docx reader or unzip tool.
- **Ollama model name:** The code calls `gpt-oss:20b-cloud`. If a model is renamed or unavailable, AI features fail gracefully but produce no output.
- **Database moved out of OneDrive:** the live DB is at `%LOCALAPPDATA%\RajData\campaign_data.db` (see §1). The old project-dir `campaign_data.db` is a stale leftover — do not point code at it.
- **WAL files:** Because the database uses WAL mode, you will see `campaign_data.db-shm` and `campaign_data.db-wal` next to the live DB while the app runs. These are normal.
- **Single-instance lock:** `desktop.py` uses TCP port `55555` to prevent multiple Raj instances. If a prior process crashed, the port may remain bound for a short time.
- **Stale backend:** `desktop.py` checks the `/api/health` `version` and kills lingering `python.exe` processes if an old server is bound to port `5555`.
- **Tracking server port:** The tracking server auto-selects an available port and stores it on the engine instance.
- **JS caching:** `index.html` script tags use `?v=N` params — bump `N` after editing any static JS file or the webview serves stale code.

---

## 12. Useful Documentation

The root directory contains extensive Markdown specs. When in doubt, consult:

- `01_PRD_Raj_AI_Gmail_Agent.md` — product requirements and feature matrix.
- `02_Technical_Architecture.md` — architecture diagrams and module breakdown.
- `03_Security_Access_Control.md` — security posture and vulnerability list.
- `04_Frontend_Specification.md` — design system (colors, fonts, layout).
- `05_Feature_Ticket_List.md` — roadmap and sprint tickets.
- `06_Market_SOP.md` — market positioning and release process.

---

*Last updated 2026-07-25: waitress WSGI, DB moved out of OneDrive (+nightly backups), send gap/cap + warm-up ramp + bounce guard, deliverability DNS card, leads-first segments with re-campaign reset, personal-name greetings, plain-mode clickable links, legacy UI deleted. Keep this file in sync with structural or workflow changes.*

---

