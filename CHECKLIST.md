# Raj Desktop — Final Verification Checklist

Use this checklist before declaring the app production-ready on this machine.

## 1. Environment & Processes

- [ ] No stale `python.exe` / `pythonw.exe` holding port 5555
      ```bat
      taskkill //F //IM python.exe
      taskkill //F //IM pythonw.exe
      ```
- [ ] Python bytecode cache is cleared so code changes take effect:
      ```bash
      find . -type d -name __pycache__ -exec rm -rf {} +
      ```
- [ ] Virtual environment is up to date:
      ```bash
      .venv\Scripts\pip install -r requirements.txt
      ```
- [ ] `credentials.json` is present in project root (gitignored).
- [ ] `repair_db_phase6.py` has been run once:
      ```bash
      .venv\Scripts\python repair_db_phase6.py
      ```

## 2. Automated Tests

- [ ] Feature test suite passes:
      ```bash
      .venv\Scripts\python test_raj.py
      ```
      Expected: **6/6 passed**.
- [ ] Full API smoke test passes:
      ```bash
      .venv\Scripts\python full_smoke_test.py
      ```
      Expected: **26/26 checks passed**.

## 3. Desktop Entry Point

- [ ] Run `python desktop.py` (or `START.bat`).
- [ ] Window opens and loads `http://127.0.0.1:5555`.
- [ ] `/api/health` returns `version: "5.0.0"` (proves no stale backend).
- [ ] Sidebar navigation switches pages without errors.
- [ ] Theme toggle works (light/dark).
- [ ] Engine start/pause buttons update the status dot.

## 4. Integrations (requires Gmail auth)

- [ ] Go to **Integrations** → Connect Gmail.
- [ ] Connect Calendar.
- [ ] Connect Drive.
- [ ] Auth status shows all three green.

## 5. Leads & Batches

- [ ] Go to **Import** → upload a small CSV/Excel.
- [ ] Preview shows rows and column headers correctly.
- [ ] Confirm import; count increases.
- [ ] Go to **Batches** → create a batch from the pool.
- [ ] Batch card appears with correct D1 pill.
- [ ] Click **Start**; status changes to `running`.
- [ ] Click **Pause**; status changes to `paused`.
- [ ] Click **Report**; modal shows batch details.
- [ ] Click **Delete**; batch returns leads to pool.

## 6. Templates

- [ ] Go to **Templates** → select SCHOOL Day 1.
- [ ] Edit subject/body, click Save.
- [ ] Re-open Templates page; saved changes persist (cache invalidated).
- [ ] Click **Sync from Gmail**; no errors (requires Gmail drafts).
- [ ] Click **Open Preview**; browser opens a rendered preview.
- [ ] Click **Lock**; sync no longer overwrites the template.

## 7. Replies (requires Gmail auth + replies)

- [ ] Go to **Replies** → replies load.
- [ ] Click **Draft** on a reply; AI draft is generated (requires Ollama).
- [ ] Edit and send the draft (requires Gmail).

## 8. Analytics & Dashboard

- [ ] Dashboard summary cards show non-zero numbers.
- [ ] Pipeline table shows Day 1-10 rows.
- [ ] Analytics page loads charts/cards without JS errors.
- [ ] Refresh buttons work.

## 9. Blacklist

- [ ] Go to **Blacklist** → emails load.
- [ ] Add a test email manually.
- [ ] Search filters the list.
- [ ] Remove the test email.
- [ ] Bounce scan runs without error (requires Gmail).

## 10. Settings

- [ ] Go to **Settings** → update `brief_email` / `default_sender`.
- [ ] Settings persist after restart.
- [ ] Autostart toggle works (Windows).

## 11. Legacy UI (if still using `main.py`)

- [ ] Run `python main.py`.
- [ ] Dashboard loads without duplicate header errors.
- [ ] Basic batch/template flows work.

## 12. Known Issues to Monitor

- [ ] Orphan families reported by `repair_db_phase6.py` are reviewed.
- [ ] School D1/D3 re-synced from Gmail if drafts were edited there.
- [ ] Ollama is running at `http://localhost:11434` for AI reply drafting.
- [ ] `python.exe` on port 5555 is not a stale process from an old session.

---

*Last updated after the master-fix session. Checklist version: 1.0*
