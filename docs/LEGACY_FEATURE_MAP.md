# Legacy Raj Feature Map

**Generated:** 2026-06-03  
**Scope:** Original `raj_chat.py` / `analytics.py` / `main.py` UI plus backend modules (`engine.py`, `gmail.py`, calendar/drive, `raj_brain.py`, `smart_importer.py`, `tracking_server.py`, `db.py`).  
**Purpose:** Record the legacy feature tree and identify what was lost, broken, or already restored in the new `web/` UI.

## Legend

| Icon | Meaning |
|------|---------|
| ✅ | Already present in the new web UI |
| ⚠️ | Partially implemented or wired differently |
| ❌ | Missing from the new web UI |
| 🔧 | Backend exists but no REST endpoint exposes it yet |

## Executive Summary

The new web UI has a solid shell (dashboard, batches, import, templates, replies, blacklist, settings, Google connect) but is missing several core capabilities that the legacy CustomTkinter UI provided:

1. **Analytics page** — fully missing.
2. **Batch family pipeline** — legacy grouped batches into `D1 → D10` campaign families; web UI is a flat table.
3. **Advanced template management** — A/B testing, lock/unlock, bulk sync/generate, and template health are missing or unexposed.
4. **Bounce scanner UI** — engine supports deep bounce scan; web button does nothing.
5. **Real AI reply drafting** — web endpoint uses a hardcoded template instead of `engine.generate_reply_draft()`.
6. **Settings parity** — morning brief email, per-sequence pause toggles, campaign export are missing.
7. **Chat with Raj** — deferred until `RajBrain` / memory / reasoning is properly integrated.

This document is the source of truth for Phase 0 and should be updated as features are restored.

---

## 1. Legacy UI Feature Inventory

### 1.1 App Lifecycle & Shell

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| Legacy Tkinter launcher | `main.py:35-103` | Bootstraps DB → Gmail → Engine → Brain → Guard → Tray → UI | Replaced by `desktop.py` |
| TCP single-instance lock | `main.py` (legacy does **not** use it) | New desktop uses `lock.py` port `55555` | N/A |
| Glass-style sidebar nav | `raj_chat.py:454-571` | 9-view switcher with emoji icons | ✅ Replaced by web sidebar |
| Theme toggle | `raj_chat.py:85-153`, `333-344` | Light/dark mode switch | ✅ Web theme toggle |
| Engine status + quick actions | `raj_chat.py:515-548` | Pause/Resume + Bounce scan in sidebar | ✅ Engine controls present |

### 1.2 Dashboard (`raj_chat.py:576-1244`)

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| Sequence summary cards | `raj_chat.py:576-609` | Cards for SCHOOL, CSR, CSR-WSL-5, GENERIC, TOTAL, BLACKLIST with Leads/Sent/Replied/Bounced/Pool | ⚠️ Web shows only Total/School/CSR/Blocked |
| Day-wise pipeline table | `raj_chat.py:610-631` | Aggregated D1/D3/D5/D7/D10 counts | ✅ `/api/dashboard/pipeline` |
| Active batch family cards | `raj_chat.py:632-638`, `794-857`, `1015-1244` | Running families as 5-day pill cards with per-day actions | ⚠️ Web shows flat list, no family cards |

### 1.3 Analytics (`analytics.py:10-201`)

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| Summary cards | `analytics.py:31-45` | Sent, Opened, Clicked, Open Rate, CTR | ❌ Missing |
| Daily activity bar chart | `analytics.py:101-144` | Last 14 days sends/opens/clicks | ❌ Missing |
| Conversion funnel | `analytics.py:145-182` | Sent → Opened → Clicked | ❌ Missing |
| Top clicked links | `analytics.py:183-201` | Most-clicked URLs | ❌ Missing |
| Refresh button | `analytics.py:79-81` | Manual refresh | ❌ Missing |

### 1.4 Chat (`raj_chat.py:1484-1527`)

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| Chat panel | `raj_chat.py:1484-1527` | Input/output console calling `brain.process(text)` | ❌ Missing (deferred) |

### 1.5 Import (`raj_chat.py:1531-1698`, `3810-3911`)

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| Import to pool | `raj_chat.py:1531-1626` | Sequence + sub-pool + file picker → `engine.smart_import()` | ✅ `/api/leads/import/file` |
| Trial send | `raj_chat.py:1577-1621`, `1630-1661` | Send all 5 days to a test email with 2-min gaps | ❌ Missing endpoint |
| Batch recipient import | `raj_chat.py:3810-3911` | Import Excel/CSV directly into a specific batch | ❌ Missing |

### 1.6 Templates (`raj_chat.py:1703-2127`)

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| 5-day status grid | `raj_chat.py:1703-1901` | Per sequence/day cards showing Exists/Empty/Locked/A-B/Source | ⚠️ Web editor exists, no status grid |
| Browser preview | `raj_chat.py:1849-1852`, `1902-1914` | Write HTML temp file and open browser | ⚠️ Web uses external browser preview |
| A/B test popup | `raj_chat.py:1855-1859`, `1916-1987` | Enable A/B, Subject A/B, split slider | ❌ UI missing; DB fields exist |
| Lock/unlock | `raj_chat.py:1862-1871`, `1989-2013` | Per-card lock toggle + Lock All | ❌ Not exposed |
| Generate / Generate Missing | `raj_chat.py:1874-1879`, `2015-2047`, `2124-2127` | Single or bulk AI generation | ⚠️ Single generate exists; bulk missing |
| Sync from Gmail | `raj_chat.py:1715-1716`, `2114-2117` | Pull matching Gmail drafts into templates | ❌ Missing |

### 1.7 Batch Management (`raj_chat.py:2130-3092`)

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| Create batch form | `raj_chat.py:2192-2278` | Name, Pull From, Sequence, Sub-Pool, Size, Day, Schedule | ✅ `/api/batches` |
| Family cards (D1→D10) | `raj_chat.py:2280-2290`, `2648-2958` | Grouped batches with expandable 5-day pills | ❌ Flat table only |
| Per-day Start/Pause/Create | `raj_chat.py:1245-1263`, `1328-1365` | Day-level actions on family pills | ❌ |
| Delete family (soft delete, return leads) | `raj_chat.py:2351-2401` | Whole-family delete with confirmation | ❌ Single batch delete only |
| Clone family | `raj_chat.py:2403-2499` | Clone a family with new name + sub-pool | ⚠️ Single batch clone only |
| Batch details popup | `raj_chat.py:1391-1440` | Counts + recipient list | ✅ `/api/batches/<id>` |
| Day report popup | `raj_chat.py:1295-1326` | Day-level stats | ❌ Missing |
| History section | `raj_chat.py:2291-2311`, `2501-2517` | Completed/deleted families | ❌ Missing |
| Sequence picker for unassigned | `raj_chat.py:1265-1293` | Assign sequence before start | ✅ `/api/batches/<id>/start` |

### 1.8 Replies (`raj_chat.py:3097-3341`)

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| Reply inbox + unread badge | `raj_chat.py:3097-3176` | List with unread count | ⚠️ List exists, badge missing |
| Sentiment filters | `raj_chat.py:3115-3121` | All / Positive / Neutral / Hostile / Unhandled | ❌ Missing |
| Reply detail popup | `raj_chat.py:3177-3294` | Body + AI draft + Send/Edit/Mark/Blacklist | ⚠️ Draft is hardcoded |
| AI draft generation | `raj_chat.py:3259-3310` | `engine.generate_reply_draft()` | ❌ Not wired |
| Blacklist from reply | `raj_chat.py:3291-3294` | One-click blacklist sender | ❌ Missing |

### 1.9 Blacklist (`raj_chat.py:3345-3458`)

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| Add/remove blacklist | `raj_chat.py:3345-3427` | Manual list management | ✅ `/api/blacklist` |
| Bounce scan | `raj_chat.py:3361-3458` | Range selector + deep bounce scan | ⚠️ Engine supports; UI not wired |

### 1.10 Settings (`raj_chat.py:3463-3658`)

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| Google connections | `raj_chat.py:3470-3647` | Gmail/Calendar/Drive OAuth | ✅ `/api/connect/*` |
| Morning brief email | `raj_chat.py:3510-3519`, `3579-3583` | Persist `brief_email` meta | ❌ Missing |
| Pause sequences toggles | `raj_chat.py:3521-3598` | Pause SCHOOL/CSR/CSR-WSL-5 | ❌ Missing |
| Export campaign state | `raj_chat.py:3543-3548`, `3649-3658` | Save Markdown report | ❌ Missing |
| Desktop notifications toggle | `raj_chat.py:3550-3578` | `meta.desktop_notifications` | ❌ Missing |

### 1.11 System Tray / Lifecycle

| Feature | File / Lines | What it does | Status |
|---------|--------------|--------------|--------|
| System tray icon | `main.py:88-98`, `raj_chat.py:3767-3793` | Minimize-to-tray | ✅ Implemented differently in `tray.py` |
| Graceful exit (`Ctrl+Space`) | `raj_chat.py:270-272`, `3795-3805` | Stop engine and exit | ✅ `Ctrl+Q` + `/api/shutdown` |
| 5-min background refresh | `raj_chat.py:1445-1467` | Auto-refresh active view | ⚠️ Web has heartbeat only |

---

## 2. Backend Capability Inventory

### 2.1 Engine Control & Lifecycle

| Capability | Location | Exposed Endpoint | Status |
|------------|----------|------------------|--------|
| `CampaignEngine.start()` | `engine.py:336` | — | 🔧 Missing |
| `CampaignEngine.stop()` | `engine.py:394` | — | 🔧 Missing |
| `CampaignEngine.pause()` / `resume()` | `engine.py:398` | `POST /api/engine/pause|resume` | ✅ |
| `CampaignEngine.is_running()` / `is_paused()` | `engine.py:406` | `GET /api/engine/status` | ✅ |
| `connect_gmail/calendar/drive` | `engine.py:230` | `POST /api/connect/*` | ✅ |
| `html_to_text` | `engine.py:287` | — | internal |
| Main 60s loop (`_loop`/`_tick`) | `engine.py:410` | — | internal |

### 2.2 Batch & Family Operations

| Capability | Location | Exposed Endpoint | Status |
|------------|----------|------------------|--------|
| `create_batch_from_pool` | `engine.py:1894` | `POST /api/batches` | ✅ |
| `assign_sequence_to_batch` | `engine.py:1937` | `POST /api/batches/<id>/start` | ✅ |
| `delete_batch` (soft delete) | `engine.py:1949` | `DELETE /api/batches/<id>` | ✅ |
| `clone_family` | `engine.py:1964` | `POST /api/batches/<id>/clone` | ✅ (single batch clone) |
| `get_batch_pipeline` | `engine.py:1881` | — | 🔧 Missing |
| `get_all_batch_pipelines` | `engine.py:1884` | — | 🔧 Missing |
| `get_pool` (rows) | `engine.py:1888` | — | 🔧 Missing |
| `get_pool_count` | `engine.py:1891` | `GET /api/pools/count` | ✅ |
| `send_batch(seq, day, limit, dry_run)` | `engine.py:1742` | — | 🔧 Missing |
| `resume_batch` | `engine.py:2855` | — | 🔧 Missing |
| `backdate_sequence` | `engine.py:2906` | — | 🔧 Missing |
| `stop_sequence_for_recipient` | `engine.py:627` | — | 🔧 Missing |
| `_auto_advance_batch` | `engine.py:650` | — | internal |
| `_check_auto_start_scheduled_batches` | `engine.py:724` | — | internal |

### 2.3 Sending, Drafts & Tracking

| Capability | Location | Exposed Endpoint | Status |
|------------|----------|------------------|--------|
| `GmailClient.send_email` | `gmail.py:93` | — | internal |
| `GmailClient.draft_email` | `gmail.py:123` | — | internal |
| `GmailClient.create_scheduled_draft` | `gmail.py:138` | — | internal |
| `GmailClient.list_drafts` | `gmail.py:158` | — | internal |
| `GmailClient.delete_draft` | `gmail.py:173` | — | internal |
| `GmailClient.get_draft_full` | `gmail.py:181` | — | internal |
| `GmailClient.search_messages` | `gmail.py:197` | — | internal |
| `GmailClient.draft_reply` | `gmail.py:222` | — | internal |
| `GmailClient.get_message_full` | `gmail.py:236` | — | internal |
| `GmailClient.trash_message` | `gmail.py:264` | — | internal |
| `_send_with_retry` | `engine.py:1720` | — | internal |
| `render` / `_ab_variant` / `due_recipients` | `engine.py:1688` | — | 🔧 Missing |
| `trial_send` | `engine.py:1783` | `POST /api/templates/<seq>/trial` | ✅ |
| `test_send` | `engine.py:1840` | `POST /api/templates/<seq>/<day>/test` | ✅ |
| `TrackingServer` + `TrackingHandler` | `tracking_server.py` | — | internal |
| `make_tracking_urls` / `inject_tracking_pixel` / `wrap_links` | `tracking_server.py:44` | — | internal |

### 2.4 Reply Workflow

| Capability | Location | Exposed Endpoint | Status |
|------------|----------|------------------|--------|
| `scan_replies(days_back)` | `engine.py:2510` | `GET /api/replies?refresh=true` | ✅ |
| `draft_replies_eod` | `engine.py:2579` | — | 🔧 Missing |
| `generate_reply_draft(reply_id)` | `engine.py:2638` | — | 🔧 Missing (web uses static body) |
| `send_reply_draft(reply_id, edited_html)` | `engine.py:2684` | — | 🔧 Missing (web uses its own send) |
| `blacklist_from_reply(reply_id)` | `engine.py:2711` | — | 🔧 Missing |
| `_persona_prompt` | `engine.py:2631` | — | internal |
| `get_replies_with_drafts` | `db.py:1066` | `GET /api/replies` | ✅ |
| `mark_reply_handled` | `db.py:1089` | `POST /api/replies/<id>/handled` | ✅ |

### 2.5 Calendar & Drive

| Capability | Location | Exposed Endpoint | Status |
|------------|----------|------------------|--------|
| Calendar auth | `calendar_integration.py:16` | via connect | ✅ auth only |
| `create_meeting` | `calendar_integration.py:64` | — | 🔧 Missing |
| `list_upcoming` | `calendar_integration.py:110` | — | 🔧 Missing |
| `cancel_event` | `calendar_integration.py:122` | — | 🔧 Missing |
| Drive auth | `drive_integration.py:16` | via connect | ✅ auth only |
| `list_files` | `drive_integration.py:64` | — | 🔧 Missing |
| `get_file_url` | `drive_integration.py:79` | — | 🔧 Missing |
| `validate_link` | `drive_integration.py:95` | — | 🔧 Missing |
| `upload_file` | `drive_integration.py:106` | — | 🔧 Missing |

### 2.6 AI / Agent Brain

| Capability | Location | Exposed Endpoint | Status |
|------------|----------|------------------|--------|
| `RajMemory` (learn/retrieve) | `raj_brain.py:37` | — | 🔧 Missing |
| `RajReasoning.analyze_situation` | `raj_brain.py:206` | — | 🔧 Missing |
| `RajReasoning.decide_next_action` | `raj_brain.py:256` | — | 🔧 Missing |
| `RajBrain.process` | `raj_brain.py:356` | — | 🔧 Missing |
| `RajBrain.proactive_check` | `raj_brain.py:483` | — | 🔧 Missing |
| `RajBrain.learn_from_outcome` | `raj_brain.py:498` | — | 🔧 Missing |

### 2.7 Analytics, Tracking & Reporting

| Capability | Location | Exposed Endpoint | Status |
|------------|----------|------------------|--------|
| `get_summary` | `engine.py:1861` | `GET /api/dashboard/summary` | ✅ |
| `get_catch_up` | `engine.py:1864` | — | 🔧 Missing |
| `morning_brief` | `engine.py:2738` | — | 🔧 Missing |
| `export_campaign_state` | `engine.py:2787` | — | 🔧 Missing |
| `get_engagement_stats` | `db.py:810` | — | 🔧 Missing |
| `get_engagement_by_day` | `db.py:836` | — | 🔧 Missing |
| `get_top_clicked_links` | `db.py:859` | — | 🔧 Missing |
| `get_ab_test_results` | `db.py:1137` | — | 🔧 Missing |
| `get_recent_activity` | `db.py:1157` | — | 🔧 Missing |
| `get_audit_log` | `db.py:897` | — | 🔧 Missing |

### 2.8 Import & Blacklist

| Capability | Location | Exposed Endpoint | Status |
|------------|----------|------------------|--------|
| `SmartImporter.analyze_file` | `smart_importer.py:324` | — | 🔧 Missing |
| `SmartImporter.get_import_preview` | `smart_importer.py:659` | — | 🔧 Missing |
| `SmartImporter.import_leads` | `smart_importer.py:367` | — | 🔧 Missing |
| `SmartImporter.import_to_pool` | `smart_importer.py:501` | via `engine.smart_import` | ✅ (CSV) |
| `engine.smart_import` | `engine.py:781` | `POST /api/leads/import/file` (CSV) | ✅ |
| `engine.import_recipients` | `engine.py:792` | `POST /api/leads/import/file` (Excel) | ✅ |
| `import_blacklist` | `engine.py:829` | — | 🔧 Missing |
| `import_blacklist_file` | `engine.py:2923` | — | 🔧 Missing |
| `blacklist_add/remove` | `engine.py:2014` | `POST/DELETE /api/blacklist` | ✅ (web uses DB) |
| `deep_bounce_scan` | `engine.py` bounce logic | — | 🔧 Missing |

### 2.9 Templates, A/B Tests & Locking

| Capability | Location | Exposed Endpoint | Status |
|------------|----------|------------------|--------|
| `sync_templates` | `engine.py:840` | — | 🔧 Missing |
| `lock_templates` / `lock_template` / `unlock_template` | `engine.py:926` | — | 🔧 Missing |
| `is_template_locked` | `engine.py:945` | — | 🔧 Missing |
| `create_missing_drafts` | `engine.py:948` | — | 🔧 Missing |
| `get_template_status` | `engine.py:968` | `GET /api/templates` | ✅ |
| `get_templates` | `engine.py:1002` | `GET /api/templates` | ✅ |
| `generate_template` | `engine.py:1012` | — | internal |
| `save_generated_template` | `engine.py:1585` | `POST /api/templates/<seq>/<day>/generate` | ✅ |
| `validate_templates` | `engine.py:1611` | — | 🔧 Missing |
| `get_template_health` | `engine.py:1655` | — | 🔧 Missing |
| `Database.template_put` incl. A/B fields | `db.py:646` | `PUT /api/templates/<seq>/<day>` | ⚠️ A/B fields ignored |
| `Database.template_lock/unlock/is_locked` | `db.py:673` | — | 🔧 Missing |

### 2.10 Settings, Configuration & Campaigns

| Capability | Location | Exposed Endpoint | Status |
|------------|----------|------------------|--------|
| `Database.set_meta` / `get_meta` | `db.py:884` | — | internal |
| `brief_email` meta | `engine.py:220` | — | ❌ No setting endpoint |
| `pause_school/csr/csr_wsl_5` meta | `engine.py:769`, `2778` | — | ❌ No setting endpoint |
| `desktop_notifications` meta | `engine.py:328` | `POST /api/state` | ⚠️ Web uses state.json |
| Autostart toggle | `autostart.py` | `POST /api/settings/autostart` | ✅ |
| Shutdown | `web/app.py:611` | `POST /api/shutdown` | ✅ |

---

## 3. Gap Matrix

| # | Feature | Legacy | Web UI | Backend | Priority |
|---|---------|--------|--------|---------|----------|
| 1 | Templates page loads saved data | ✅ | ✅ fixed | ✅ | **P0** |
| 2 | Batch sub-pool dropdown | ✅ | ✅ fixed | ✅ | **P0** |
| 3 | AI reply draft (not hardcoded) | ✅ | ✅ fixed | ✅ | **P0** |
| 4 | In-page template preview | ✅ | ✅ fixed | ✅ | **P1** |
| 5 | Header Refresh/Export buttons | ✅ | ✅ fixed | ✅ | **P1** |
| 6 | Analytics page | ✅ | ❌ | ✅ | **P2** |
| 7 | Batch family pipeline | ✅ | ✅ fixed | 🔧 | **P2** |
| 8 | A/B test UI + lock/unlock | ✅ | ✅ fixed | 🔧 | **P2** |
| 9 | Bounce scanner UI | ✅ | ✅ fixed | 🔧 | **P2** |
| 10 | Reply sentiment filters + blacklist-from-reply | ✅ | ✅ fixed | 🔧 | **P2** |
| 11 | Settings: brief email, pause sequences, export | ✅ | ✅ fixed | 🔧 | **P2** |
| 12 | Engine lifecycle + automation controls | ✅ | ✅ fixed | ✅ | **P3** |
| 13 | Chat with Raj | ✅ | ❌ | 🔧 | **Deferred** (after brain integration) |
| 14 | Calendar/Drive management | ✅ | ✅ fixed | 🔧 | **P3** |
| 15 | Analytics page | ✅ | ✅ fixed | ✅ | **P3** |
| 16 | Real-time updates / mobile layout | ⚠️ | ❌ | N/A | **P4** |

---

## 4. Notes for Restoration

- **Use existing engine methods first.** Most missing features already have a backend implementation (e.g., `generate_reply_draft`, `deep_bounce_scan`, `lock_template`, `export_campaign_state`). Add thin REST wrappers rather than rewriting logic in `web/app.py`.
- **Do not expose engine lifecycle start/stop lightly.** `engine.start()` spins up a tracking server and background loops; the desktop wrapper currently starts the Flask app only. Decide later if the engine main loop should run inside `desktop.py`.
- **Chat with Raj is intentionally deferred.** It depends on `RajBrain`, `RajMemory`, and `RajReasoning`, which are not wired to the web UI at all.
- **A/B fields exist in DB.** `subject_b`, `ab_test`, `ab_split` are stored by `Database.template_put` but ignored by the current `PUT` endpoint.
- **Auto-Generate spamming drafts.** `save_generated_template` always creates a Gmail draft. Add a `create_draft=false` option for the web UI workflow.
