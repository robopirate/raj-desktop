# TECHNICAL ARCHITECTURE DOCUMENT
## Raj AI Gmail Agent v5.0
### RoboPirate Technologies | 2026-06-03

---

## 1. SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Desktop UI  │  │  Web UI      │  │  Emergency Commands  │  │
│  │ (customtkinter│  │ (React SPA)  │  │ (Email STOP/ALL)    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼──────────────────┼─────────────────────┼──────────────┘
          │                  │                     │
┌─────────▼──────────────────▼─────────────────────▼──────────────┐
│                    APPLICATION LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  RajChatApp (raj_chat.py) — Desktop window manager       │  │
│  │  ├─ Dashboard view                                       │  │
│  │  ├─ Chat view (RajBrain integration)                     │  │
│  │  ├─ Import view                                          │  │
│  │  ├─ Templates view                                       │  │
│  │  ├─ Batches view                                         │  │
│  │  ├─ Replies view                                         │  │
│  │  ├─ Blacklist view                                       │  │
│  │  ├─ Settings view                                        │  │
│  │  └─ Charts view (v4.3)                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Flask Server (app.py) — Web API (port 5000)             │  │
│  │  ├─ Serves React SPA (dist/)                             │  │
│  │  └─ REST API endpoints                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬─────────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────────┐
│                    ENGINE LAYER                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CampaignEngine (engine.py) — Core orchestrator          │  │
│  │  ├─ _process_running_batches() — Batch lifecycle         │  │
│  │  ├─ _process_pool_batches() — Pool management            │  │
│  │  ├─ _advance_sequences() — Auto-advance D1→D10         │  │
│  │  ├─ _scan_bounces() — Bounce detection                   │  │
│  │  ├─ _scan_replies() — Reply detection                    │  │
│  │  ├─ _draft_replies_eod() — AI reply drafting            │  │
│  │  ├─ _send_morning_brief() — Daily report                 │  │
│  │  ├─ _check_emergency_commands() — STOP/RESUME           │  │
│  │  └─ _load_sequences() — Template management             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  RajBrain (raj_brain.py) — AI Agent                      │  │
│  │  ├─ sentiment_analysis() — positive/neutral/hostile      │  │
│  │  ├─ draft_reply() — Generate reply drafts                │  │
│  │  ├─ summarize_reply() — Reply content summary            │  │
│  │  └─ chat() — Interactive chat interface                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬─────────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────────┐
│                    INTEGRATION LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Gmail API│  │ Calendar │  │ Drive    │  │  Ollama AI   │  │
│  │ (OAuth)  │  │ (Google) │  │ (Google) │  │  (Local LLM) │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
└──────────────────────────┬─────────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────────┐
│                    DATA LAYER                                    │
│  ┌──────────────────────┐  ┌──────────────────────────────┐   │
│  │  SQLite (local)      │  │  PostgreSQL (cloud — Render) │   │
│  │  campaign_data.db    │  │  via sync_to_cloud.py        │   │
│  └──────────────────────┘  └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. MODULE BREAKDOWN

### 2.1 main.py (Entry Point)
```python
main.py
├── Initialize Database
├── Connect GmailClient
├── Start CampaignEngine (background thread)
├── Initialize RajBrain
├── Launch RajChatApp (main thread)
└── On exit: engine.stop(), cleanup
```

### 2.2 engine.py (Core — 93 KB)
**Thread:** Background daemon thread
**Responsibilities:**
- Batch lifecycle management
- Pool-to-batch conversion
- Auto-advance sequence logic
- Bounce/reply scanning (scheduled)
- AI reply drafting (EOD)
- Morning brief (8 AM)
- Emergency command processing

**Key Data Flow:**
```
recipients (pool, batched=0)
    → create_batch() → batches table
    → process_running_batches() → sends table
    → advance_sequences() → next day batch
    → scan_bounces() → blacklist (if bounce)
    → scan_replies() → replies table + sentiment
    → draft_replies_eod() → reply drafts
```

### 2.3 raj_brain.py (AI — 51 KB)
**Model:** Ollama GPT-OSS 20B (local)
**Endpoint:** http://localhost:11434
**Functions:**
- `sentiment_analysis(reply_text)` → positive/neutral/hostile
- `draft_reply(reply_text, context)` → draft reply
- `summarize_reply(reply_text)` → 1-line summary
- `chat(message)` → interactive conversation

**Prompt Engineering:**
- System prompt defines RoboPirate persona
- Context includes sequence history
- Temperature: 0.7 for creativity
- Max tokens: 500 for replies

### 2.4 raj_chat.py (Desktop UI — 129 KB)
**Framework:** customtkinter
**Views:** Dashboard, Chat, Import, Templates, Batches, Replies, Blacklist, Settings, Charts
**Pattern:** Sidebar navigation + content area switching

### 2.5 db.py (Database — 31 KB)
**Dual Mode:**
```python
if DATABASE_URL:
    PostgreSQL (cloud)
else:
    SQLite (local)
```

**Tables:**
| Table | Purpose |
|-------|---------|
| recipients | Lead data (email, name, org, sequence, batched) |
| batches | Batch definitions (name, sequence, status, schedule) |
| batch_recipients | Many-to-many: batch ↔ recipient |
| sends | Send log (recipient, day, status, timestamp) |
| replies | Incoming replies (from, subject, body, sentiment) |
| blacklist | Blocked emails (email, reason, timestamp) |
| templates | Email templates (sequence, day, subject, body, locked) |
| pending_resumes | Crash recovery state |
| meta | Key-value config |
| audit_log | Action history |

### 2.6 gmail.py (API — 7.5 KB)
**Auth:** Desktop OAuth 2.0 flow
**Scope:** https://www.googleapis.com/auth/gmail.send
**Methods:**
- `send_email(to, subject, body)` — Send via Gmail API
- `get_drafts()` — List Gmail drafts for template sync
- `scan_inbox(query)` — Search inbox for bounces/replies

### 2.7 sync_to_cloud.py (Migration — 6 KB)
**Purpose:** SQLite → PostgreSQL sync
**Method:** Direct table copy with ON CONFLICT upsert
**Tables synced:** All 10 tables
**Trigger:** Manual (not automated)

---

## 3. DATA FLOW DIAGRAMS

### 3.1 Lead Import → Send
```
User uploads CSV/Excel
    → smart_importer.py (auto-detect columns)
    → recipients table (batched=0, in pool)
    → User clicks "Create Batch"
    → engine._create_batch_from_pool()
    → batches table + batch_recipients
    → engine._process_running_batches()
    → gmail.py send_email()
    → sends table (status='sent')
    → recipient marked batched=1
```

### 3.2 Reply Handling
```
Engine._scan_replies() (every 60 min)
    → gmail.py scan_inbox('in:replyto')
    → New reply found
    → replies table (status='pending')
    → raj_brain.sentiment_analysis()
    → Update sentiment (positive/neutral/hostile)
    → If hostile → blacklist email
    → EOD: raj_brain.draft_reply()
    → Update reply status to 'drafted'
    → User reviews draft in UI
    → User sends or discards
```

### 3.3 Crash Recovery
```
Engine starts
    → Check pending_resumes table
    → If entries exist:
        → Restore batch state
        → Resume from last sent email
    → Log recovery to audit_log
    → Continue normal processing
```

---

## 4. API SPECIFICATION (Flask)

### 4.1 Endpoint List
```
GET    /api/dashboard         → Campaign summary
GET    /api/batches           → All batches
POST   /api/batches           → Create from pool
POST   /api/batches/{id}/run    → Run batch
POST   /api/batches/{id}/pause  → Pause batch
DELETE /api/batches/{id}      → Delete batch
POST   /api/chat              → Raj chatbot
GET    /api/templates         → All templates
GET    /api/templates/{seq}/{day} → Single template
POST   /api/templates/sync    → Sync from Gmail
POST   /api/import            → File upload
GET    /api/blacklist         → Blacklist
POST   /api/blacklist         → Add entry
DELETE /api/blacklist         → Remove entry
GET    /api/replies           → All replies
POST   /api/replies/{id}/handled → Mark handled
POST   /api/scan-replies      → Trigger scan
POST   /api/scan-bounces      → Trigger scan
GET    /api/engine/status     → Engine state
POST   /api/engine/{action}   → Control engine
GET    /api/settings          → Get settings
POST   /api/settings          → Save settings
```

### 4.2 Response Format
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2026-06-03T10:00:00"
}
```

---

## 5. DATABASE SCHEMA

### 5.1 Entity Relationship
```
recipients (1) ───< sends (many)
recipients (1) ───< batch_recipients >─── batches (many)
recipients (1) ───< replies (many)
batches (1) ───< batch_recipients >─── recipients (many)
recipients (1) ─── blacklist (0..1)
```

### 5.2 Key Fields
**recipients:**
- id, email, name, org, sequence_id, batched, created_at

**batches:**
- id, name, sequence_id, status, scheduled_at, day_offset, stagger_minutes, created_at

**sends:**
- id, recipient_id, batch_id, day, status (sent/bounced/replied), created_at

**replies:**
- id, recipient_id, subject, body, sentiment, summary, draft_reply, status, created_at

---

## 6. ERROR HANDLING

| Error Type | Handler | Recovery |
|-----------|---------|----------|
| Gmail API quota exceeded | Quota rollback | Auto-resume next cycle |
| Ollama server down | Graceful skip | Retry next cycle |
| Database locked | Retry with backoff | Wait + retry |
| SMTP send failure | Log + skip | Manual retry via UI |
| Invalid CSV import | Error message | Fix CSV + re-import |
| OAuth token expired | Re-auth prompt | Web OAuth fallback |

---

## 7. TECHNOLOGY STACK

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.12 |
| Desktop UI | customtkinter | 5.2 |
| Web Backend | Flask | 3.0 |
| Web Frontend | React | 18 |
| Database (local) | SQLite | 3 |
| Database (cloud) | PostgreSQL | 15 |
| AI | Ollama | latest |
| LLM | GPT-OSS | 20B |
| Charts | matplotlib | 3.9 |
| HTTP | requests | 2.31 |
| Email | Gmail API | v1 |
| Auth | OAuth 2.0 | Desktop flow |

---

## 8. DEPLOYMENT OPTIONS

### 8.1 Desktop Mode (Current)
```
User machine → Python → main.py → Desktop UI + Flask
Database: campaign_data.db (SQLite, local)
AI: Ollama (localhost:11434)
```

### 8.2 Cloud Mode (Future)
```
Render → Docker → Flask API + React
Database: PostgreSQL (Render)
AI: Ollama (Render or external)
```

### 8.3 Hybrid Mode (Target)
```
Desktop (control) ↔ Cloud (analytics/storage)
Real-time sync via sync_to_cloud.py
Best of both worlds
```

---

## 9. PERFORMANCE CHARACTERISTICS

| Metric | Value |
|--------|-------|
| Memory usage (idle) | ~80 MB |
| Memory usage (sending) | ~120 MB |
| CPU usage (idle) | <1% |
| CPU usage (AI inference) | ~30% (GPU), ~80% (CPU) |
| Disk space (app) | ~5 MB |
| Disk space (database) | ~2 MB per 1000 leads |
| Startup time | ~3 seconds |
| Email send latency | 45s (configured delay) |
| Batch creation time | <1 second |
| Reply scan time | ~10 seconds |
| Bounce scan time | ~30 seconds |

---

**Document Owner:** Om (RoboPirate)
**Last Updated:** 2026-06-03
**Status:** APPROVED
