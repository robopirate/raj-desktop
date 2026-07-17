# Raj Desktop — Master Fix Plan

> This is the consolidated repair roadmap for the Raj AI Gmail Agent desktop app.  
> It covers everything that was audited, what is already fixed, what is still broken, and the exact remediation order.

---

## 1. Current State

- **Database:** Backed up at `campaign_data.db.bak-masterplan`.
- **Git hygiene:** PII export files, plaintext patch files, and transient state files removed from tracking; `.gitignore` hardened.
- **OAuth/connect flow:** Rewritten in `gmail.py`, `calendar_integration.py`, `drive_integration.py` with `run_local_server(port=0)`, refresh-token fallback, bounded timeout, and explicit credential paths.
- **Reply pipeline:** `email.utils.parseaddr` From matching, NameErrors fixed, `draft_reply` To header fixed, plain-text newlines converted to `<br>` on send.
- **DB/data integrity:** `sub_pool` added to `Recipient`, `RLock` + `atomic()` added, re-import upsert no longer resets `batched`, protected-domain check moved into `blacklist_add`, family grouping uses `parent_batch_id`, `deleted_at IS NULL` filters added.
- **Sending correctness (partial):** verified sender via Gmail `sendAs`, tracking HMAC + localhost binding, catch-up-safe daily windows, `due_recipients` requires `sent`, start-batch clears `scheduled_at`, WSL STOP key fixed, bounce classifier defaults ambiguous to soft.

---

## 2. What Still Does Not Fit / Could Be Better

### 2.1 Engine (`engine.py`)

| Issue | Why it matters | Fix |
|-------|----------------|-----|
| `html_to_text` does not strip `<style>` / `<script>` | Embedded CSS/JS leaks into plain-text multipart emails and looks broken. | Strip `<style>...</style>` and `<script>...</script>` (with `re.DOTALL`) before other regexes. |
| HTML detection is too loose | A lone `<` or `>` in plain text triggers HTML path. | Detect HTML only with a real tag pattern, e.g. `<[a-zA-Z/][^>]*>`. |
| Batch send path has no empty-body guard | `send_batch` and `_process_running_batches` can queue/sends empty bodies if template body is blank. | Add the same empty-body checks used in `trial_send`/`test_send` before calling `_send_with_retry`. |
| Template sync ignores Gmail plain-text parts | `sync_templates_from_gmail` only takes `text/html`; if a user edits the Gmail draft as plain text, the change is lost. | Fall back to `text/plain` body when no `text/html` part exists; regenerate `text_body` from the new HTML. |
| Template lock system is split | Lock state lives partly as `locked` DB column and partly as `meta` keys. | Deprecate meta keys, read/write the `locked` column only, migrate any lingering meta locks. |
| `create_missing_drafts` passes `self.default_sender` as first arg to `draft_email` | `draft_email` signature is `(to, subject, body_html, ...)`; passing sender as `to` creates a self-draft. | Pass `self.default_sender` only in the `sender=` kwarg and a placeholder/test `to` address. |
| `_process_running_batches` uses 2-second slot lock | With 60s loop this is fine, but on fast machines it can starve other batches; also `hasattr` check is unnecessary. | Keep 2s throttle but initialize `_last_batch_process_time = None` in `__init__` and simplify guard. |
| `send_batch` and `_process_running_batches` duplicate send logic | Two code paths for the same action means fixes must be applied twice. | After Phase 5 consider a single `_send_to_recipient` helper; for now keep both in sync. |

### 2.2 Frontend (`web/static/js/`)

| Issue | Why it matters | Fix |
|-------|----------------|-----|
| `batches.js` renders `poolCount` as raw object | `API.poolCount` returns `{"count": N}` but code sets `textContent = count`. | Use `count.count ?? count`. |
| Family expand uses loose `==` and string/number keys | `rootId` may be string; `Set.has` with number fails. | Normalize to string everywhere: `String(rootId)`. |
| Day pills re-render inside family details and root row | Same day pills rendered twice; click handlers may attach to wrong instance. | Render once, or scope handlers to the root card. |
| Day-pill click is not wired | `data-day` attribute exists but no listener opens a day report. | Add click handler (or remove unused attribute). |
| `batchReport` shown via `alert(JSON.stringify(...))` | Poor UX; long reports truncate. | Render in a modal or at least a preformatted dialog. |
| XSS via unescaped innerHTML | `pipe.root_name`, `b.sent`, `statusBadge`, etc. are interpolated raw. | Escape all user-controlled values before `innerHTML` (helper `escapeHtml`). |
| No fetch timeout / abort | Long hangs freeze UI with no feedback. | Add `AbortController` timeout in `api.js`. |
| Asset cache-busting still `?v=4` | Browsers may load stale JS/CSS after fixes. | Bump to `?v=5` in `index.html`. |
| Theme flash / `bg-white` | The dark theme may flash white on load; some components hardcode `bg-white`. | Audit `index.html` for hardcoded light classes and switch to theme variables. |
| Templates cache not invalidated | Editing a template may not refresh the templates view. | Add `page:templates` reload and clear any in-memory cache. |
| Excel import `mapping=None` | Pasted/import path may call preview with `mapping=None` and crash. | Default `mapping` to `{}` in all preview helpers. |
| Batch 404 handling | Starting a missing batch gives generic error. | Add explicit 404 path. |
| Duplicate `/api/preview` route | `preview_template` and `open_preview` both register `POST /api/preview`; second wins silently. | Rename `open_preview` route to `/api/preview/window` and update `api.js`. |
| `/api/shutdown` dead code | `werkzeug.server.shutdown` no longer exists in modern Flask/Werkzeug. | Remove route or use `os._exit` / signal only when called from desktop wrapper. |

### 2.3 Web Backend (`web/app.py`)

| Issue | Why it matters | Fix |
|-------|----------------|-----|
| `_last_connect_error` exposed but not returned by health | UI cannot show connect error details. | Add `last_error` to `/api/health` or `/api/auth/status`. |
| `/api/batches/<id>/start` does not validate batch exists | Returns 500 instead of 404. | Check `batch_get` first and return 404. |
| `/api/batches/<id>/start` does not block `unassigned` | Engine now blocks this; API should too with clear message. | Return 400 if `sequence_id == 'unassigned'`. |
| `/api/engine/status` uses `getattr(..., lambda)` | If `engine` lacks methods it silently returns defaults; better to use real methods. | Add `is_running`/`is_paused` methods (already exist in engine). |

### 2.4 Database / Data Repairs (one-time)

| Issue | Why it matters | Fix |
|-------|----------------|-----|
| Corrupt batch rows 101/102 and `a` family chain | Leftover from earlier crashes; pipeline view may show phantom families. | Inspect rows, delete or repair if orphaned. |
| Zombie `pending` sends | Sends stuck in `pending` from killed processes never become `sent`/`failed`. | Mark old pending sends without a Gmail message id as `failed` (or re-queue). |
| Uppercase `CSR-WSL-5` templates | Sequence id is lowercased in code but some DB rows may be uppercase, causing misses. | Normalize to lowercase in `templates` table. |
| School D1/D3 out of sync with Gmail | Edits in Gmail may not be reflected in DB. | Re-sync school D1/D3 from Gmail drafts. |
| `batched` flags inconsistent | Some recipients may have `batched=0` while being in active batches. | Reconcile using `batch_recipients` membership. |

### 2.5 Housekeeping

| Issue | Why it matters | Fix |
|-------|----------------|-----|
| No `VERSION` constant | `main.py` and docs disagree; hard to know what is running. | Add `VERSION = "5.0.0"` in `engine.py` (or new `version.py`) and expose via `/api/health`. |
| `raj_chat.py` duplicated header | Large legacy file has a duplicate module docstring/header. | Remove duplicate. |
| `raj_brain.py` dead import | Unused import causes warnings. | Remove. |
| `desktop.py` stale-server detection | Does not detect port 5555 occupied by old code. | Add a startup ping test and warn/kill stale process. |
| `AGENTS.md` out of date | New fixes and entry points not documented. | Update after all phases. |

---

## 3. Execution Order

### Phase 4 — Engine Send Correctness (next)
1. Harden `html_to_text`: strip `<style>`/`<script>`, use real HTML tag detection.
2. Add empty-body guard in `_process_running_batches` and `send_batch`.
3. Make template sync extract `text/plain` from Gmail drafts and regenerate `text_body`.
4. Unify template lock on `locked` column; migrate meta keys.
5. Fix `create_missing_drafts` self-draft bug.

### Phase 5 — Frontend Robustness
1. Fix `batches.js` pool count, family key normalization, duplicate rendering, day-pill handler, report UX.
2. Add `escapeHtml` helper and apply to all interpolated HTML.
3. Add fetch timeout/abort in `api.js`.
4. Bump asset version to `?v=5`; fix `bg-white` flashes; fix templates cache.
5. Fix Excel import `mapping=None`; add batch 404; remove duplicate `/api/preview` route; fix `/api/shutdown`.
6. Expose `_last_connect_error` in health/auth status.

### Phase 6 — Database Data Repairs
1. Inspect and repair corrupt batch rows 101/102 and `a` family.
2. Mark zombie pending sends failed.
3. Normalize uppercase `CSR-WSL-5` templates.
4. Re-sync school D1/D3 from Gmail.
5. Reconcile `batched` flags.

### Phase 7 — Housekeeping
1. Add `VERSION` constant and expose in `/api/health`.
2. Clean `raj_chat.py` duplicated header.
3. Remove dead import in `raj_brain.py`.
4. Update `AGENTS.md` with new OAuth/tracking/lock behavior.
5. Improve `desktop.py` stale-server detection.

### Phase 8 — Verification
1. Run `python test_raj.py`.
2. Run import/preview checks.
3. Run desktop smoke test (`python desktop.py`).
4. Confirm no `python.exe` stale on port 5555.

---

## 4. Risks & Notes

- **Stale processes:** Before every test run, execute `taskkill //F //IM python.exe & taskkill //F //IM pythonw.exe` to avoid port-5555 ghosts.
- **Ollama dependency:** AI reply drafting requires local Ollama; if offline, those features fail gracefully.
- **OAuth tokens:** Tokens are stored unencrypted locally. Do not commit `*.pickle` or `credentials.json`.
- **DB repairs are destructive:** Phase 6 changes are one-time; always re-verify against the `.bak-masterplan` backup.
- **No formal test suite:** `test_raj.py` is the only verification; rely on it plus manual smoke tests.

---

*Plan version: 1.0 — created during master-fix session after Phases 0-3 and partial Phase 4.*
