# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Raj: AI Gmail Automation Agent
### Version 5.0 | RoboPirate Technologies | 2026-06-03

---

## 1. EXECUTIVE SUMMARY

**Product Name:** Raj AI Gmail Agent
**Codename:** RoboPirate Raj
**Version:** 5.0
**Owner:** Om (RoboPirate)
**Status:** Production (v4.2.1 live, v5.0 in development)

**What is Raj?**
Raj is an AI-powered desktop email automation agent that manages multi-step cold outreach campaigns through Gmail. It combines local AI (Ollama), pool-based batch architecture, and vertical-specific business logic to automate the entire email lifecycle — from lead import to reply handling — without API costs.

**Why does it exist?**
Traditional email tools (Mailchimp, SendGrid) are generic, expensive, and don't understand business context. Raj is built for a specific Indian market use case (SCHOOL + CSR outreach) with hardcoded business logic that no off-the-shelf tool provides.

---

## 2. PRODUCT VISION

### 2.1 Vision Statement
> "An autonomous AI agent that manages email relationships end-to-end — importing leads, sending personalized sequences, handling replies with sentiment analysis, and learning from outcomes — all running locally with zero API costs."

### 2.2 Target Market
- **Primary:** Indian education CSR coordinators (SCHOOL sequence)
- **Secondary:** Indian corporate CSR managers (CSR sequence)
- **Geography:** India (timezone: Asia/Kolkata)
- **Language:** English (Hinglish tolerant)

### 2.3 Value Proposition
| Pain Point | Raj's Solution |
|-----------|---------------|
| Generic email tools don't understand verticals | Hardcoded SCHOOL/CSR personas |
| API costs scale with volume | Local AI (Ollama) = $0 |
| Manual follow-up tracking | Auto-advance D1→D3→D5→D7→D10 |
| Bounce handling is manual | 11-regex auto-detection + auto-blacklist |
| Reply management is chaotic | AI sentiment + auto-draft replies |
| Crash = lost progress | Resume-on-boot crash recovery |

---

## 3. USER PERSONAS

### 3.1 Primary: The CSR Coordinator ("Priya")
- **Role:** CSR coordinator at an Indian education NGO
- **Goal:** Reach 50 schools per week for partnership proposals
- **Pain:** Manually tracking who replied, who bounced, who needs follow-up
- **Uses:** SCHOOL sequence (warm, education-focused tone)

### 3.2 Secondary: The Corporate CSR Manager ("Rahul")
- **Role:** CSR manager at an Indian corporation
- **Goal:** Partner with NGOs for CSR mandate compliance
- **Pain:** Managing hundreds of outreach emails across multiple campaigns
- **Uses:** CSR sequence (formal, corporate tone)

### 3.3 System User: The Admin ("Om")
- **Role:** Product owner, manages Raj infrastructure
- **Goal:** Monitor campaign health, fix issues, review AI drafts
- **Pain:** No visibility into campaign performance without checking logs
- **Uses:** Desktop UI + Charts tab + morning brief emails

---

## 4. FUNCTIONAL REQUIREMENTS

### 4.1 Core Engine (MUST HAVE)

| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| F-01 | Pool-based batch architecture | Leads stored in pool (batched=0), batches created from pool | ✅ v4.0 |
| F-02 | Auto-advance sequences | D1 auto-creates D3 batch, D3→D5, D5→D7, D7→D10 | ✅ v4.0 |
| F-03 | Staggered batch sending | 2-minute intervals between sends, race-condition protected | ✅ v4.0 |
| F-04 | Resume-on-boot | Survives crashes, resumes exact state from pending_resumes table | ✅ v4.0 |
| F-05 | Quota rollback | If quota hit mid-batch, rollback + resume later | ✅ v4.0 |
| F-06 | Sunday pause | No sends on Sunday, auto-resume Monday | ✅ v4.0 |
| F-07 | Two sequences | SCHOOL (warm) + CSR (formal) with different personas | ✅ v4.0 |
| F-08 | HTML email branding | RoboPirate branded HTML template with logo | ✅ v4.0 |
| F-09 | Placeholder substitution | {{NAME}}, {{ORG}}, {{EMAIL}} auto-replaced | ✅ v4.0 |
| F-10 | Backdate sequences | Can start sequences from past date for catch-up | ✅ v4.0 |

### 4.2 Template Management (MUST HAVE)

| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| F-11 | Gmail draft sync | Pulls templates from Gmail drafts via regex (SCHOOL/CSR EMAIL N) | ✅ v4.0 |
| F-12 | Template locking | Lock prevents accidental overwrite during sync | ✅ v4.0 |
| F-13 | Auto-generated templates | Fallback auto-generated if no draft found | ✅ v4.0 |
| F-14 | Template versioning | Track template changes over time | ❌ Not built |

### 4.3 Bounce Handling (MUST HAVE)

| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| F-15 | Bounce scanning | Multi-query inbox scan for bounces | ✅ v4.0 |
| F-16 | 11-regex detection | Comprehensive bounce pattern matching | ✅ v4.0 |
| F-17 | Deep bounce scan | 30-day historical bounce search | ✅ v4.0 |
| F-18 | Auto-blacklist | Hard bounces → automatic blacklist | ✅ v4.0 |
| F-19 | Auto-reply detection | Won't blacklist out-of-office replies | ✅ v4.0 |
| F-20 | False-positive filtering | Reduces incorrect blacklisting | ✅ v4.0 |
| F-21 | Blacklist file import | Bulk blacklist from CSV/txt file | ✅ v4.0 |
| F-22 | Domain protection | Never blacklist @robopirate.in emails | ✅ v4.0 |

### 4.4 Reply Handling (MUST HAVE)

| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| F-23 | Reply scanning | Multi-strategy inbox scan for replies | ✅ v4.0 |
| F-24 | AI sentiment analysis | Classifies replies: positive/neutral/hostile (Ollama) | ✅ v4.0 |
| F-25 | AI reply drafting | Generates draft replies EOD for approval | ✅ v4.0 |
| F-26 | Reply sentiment storage | Stores sentiment in replies table | ✅ v4.0 |
| F-27 | Reply summary | AI-generated summary of reply content | ✅ v4.0 |

### 4.5 Automation (MUST HAVE)

| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| F-28 | Morning brief | Daily 8 AM email report with campaign stats | ✅ v4.0 |
| F-29 | Emergency commands | STOP SCHOOL/CSR/ALL via email to self | ✅ v4.0 |
| F-30 | Campaign export | Markdown report of campaign state | ✅ v4.0 |
| F-31 | Audit logging | Full action history in audit_log table | ✅ v4.0 |
| F-32 | Database auto-migration | Safe schema updates without data loss | ✅ v4.0 |

### 4.6 Data Management (MUST HAVE)

| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| F-33 | Smart CSV/Excel import | Auto-detects columns, maps to schema | ✅ v4.0 |
| F-34 | Pool management | View pool count, create batches from pool | ✅ v4.0 |
| F-35 | Desktop→Cloud sync | SQLite → PostgreSQL sync for cloud deployment | ✅ v4.2 |
| F-36 | CSV export | Export all tables to CSV | ✅ v4.0 |

### 4.7 Integrations (NICE TO HAVE)

| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| F-37 | Google Calendar | Optional calendar integration | ✅ v4.0 |
| F-38 | Google Drive | Optional drive backup | ✅ v4.0 |
| F-39 | Gmail API | Desktop OAuth flow | ✅ v4.0 |
| F-40 | Web OAuth | Cloud OAuth for render deployment | ✅ v4.2 |

### 4.8 Analytics (SHOULD HAVE — CURRENTLY MISSING)

| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| F-41 | Send trends chart | 14-day area chart (School vs CSR) | ✅ v4.3 |
| F-42 | Sentiment pie chart | Reply sentiment breakdown | ✅ v4.3 |
| F-43 | Sequence comparison | School vs CSR bar chart | ✅ v4.3 |
| F-44 | KPI summary cards | Total Leads, Sent, Replied, Reply Rate | ✅ v4.3 |
| F-45 | Recent activity feed | Live send/reply stream | ✅ v4.3 |
| F-46 | Pipeline visualization | Visual D1→D10 grid with progress | ❌ Not built |
| F-47 | Batch progress bars | Visual progress per batch | ❌ Not built |
| F-48 | Reply rate trends | Track reply rate over time | ❌ Not built |
| F-49 | Bounce rate analytics | Track bounce trends | ❌ Not built |
| F-50 | Campaign comparison | Compare multiple campaigns | ❌ Not built |

---

## 5. NON-FUNCTIONAL REQUIREMENTS

### 5.1 Performance
| Requirement | Target |
|------------|--------|
| Batch send rate | 1 email per 45 seconds |
| Stagger interval | 2 minutes between batch sends |
| Reply scan frequency | Every 60 minutes |
| Bounce scan frequency | Every 6 hours |
| Morning brief time | 8:00 AM IST |
| EOD reply drafting | 7:00 PM IST |

### 5.2 Reliability
| Requirement | Target |
|------------|--------|
| Crash recovery | 100% (resume-on-boot) |
| Quota handling | Graceful rollback + resume |
| DB integrity | Auto-migration + check tools |
| Uptime | Desktop app = user's machine uptime |

### 5.3 Security
| Requirement | Target |
|------------|--------|
| Gmail OAuth | Desktop flow (secure) |
| Token storage | token.pickle (local file) |
| Credential storage | credentials.json (local file) |
| Blacklist protection | Never blacklist own domain |
| Data encryption | Not implemented (FUTURE) |

### 5.4 Scalability
| Requirement | Target |
|------------|--------|
| Max leads per sequence | 10,000 (tested) |
| Max batches active | Unlimited (pool-constrained) |
| Max sequences | 2 (SCHOOL + CSR) — extensible |
| Database | SQLite (local) + PostgreSQL (cloud) |

---

## 6. SEQUENCE DEFINITIONS

### 6.1 SCHOOL Sequence (Warm Tone)
```
Day 1:  Introduction + partnership proposal (warm, educational)
Day 3:  Follow-up with value proposition (soft reminder)
Day 5:  Social proof + case studies (credibility)
Day 7:  Final call-to-action (gentle urgency)
Day 10: Breakup email (professional closure)
```
**Persona:** Education-focused, warm, collaborative
**Signature:** RoboPirate branding
**Stagger:** 2 minutes between sends

### 6.2 CSR Sequence (Formal Tone)
```
Day 1:  Professional introduction + CSR mandate alignment
Day 3:  Compliance benefits + partnership model
Day 5:  Impact metrics + previous partnerships
Day 7:  Meeting request + flexible options
Day 10: Final follow-up with deadline
```
**Persona:** Corporate, formal, compliance-focused
**Signature:** RoboPirate branding
**Stagger:** 2 minutes between sends

---

## 7. COMPETITIVE POSITIONING

### 7.1 GitHub Landscape Score
| Competitor | Stars | Score /70 | vs. Raj |
|-----------|-------|-----------|---------|
| **Raj (You)** | N/A | **65/70** | — |
| django-crm | 568 | 42/70 | +23 |
| colossus | 562 | 39/70 | +26 |
| aomail-app | 61 | 35/70 | +30 |
| pigeon-rs | 82 | 28/70 | +37 |

### 7.2 Unique Differentiators
1. **Pool-based architecture** — No other project has this
2. **Auto-advance sequences** — Fully automated lifecycle
3. **Resume-on-boot** — Production-hardened crash recovery
4. **Local AI** — $0 API costs (Ollama)
5. **Vertical logic** — Hardcoded SCHOOL/CSR personas
6. **Dual UI** — Desktop + Web simultaneously
7. **Cloud sync** — SQLite → PostgreSQL migration path

---

## 8. RELEASE CRITERIA

### 8.1 v4.3 (Current — Charts Release)
- ✅ Analytics charts in desktop UI
- ✅ KPI cards
- ✅ 14-day trends
- ✅ Sentiment breakdown
- ✅ Sequence comparison

### 8.2 v5.0 (Next — AI Agent Release)
- [ ] Pipeline visualization (D1→D10 grid)
- [ ] Batch progress bars
- [ ] Auto-refresh data
- [ ] AI-powered lead scoring
- [ ] Smart send-time optimization
- [ ] A/B testing for templates

### 8.3 v6.0 (Future — Platform Release)
- [ ] Multi-provider (Outlook, IMAP)
- [ ] MCP protocol support
- [ ] Docker containerization
- [ ] REST API documentation
- [ ] WebSocket real-time updates
- [ ] Multi-user support

---

## 9. METRICS & SUCCESS

| Metric | Current | Target |
|--------|---------|--------|
| Leads managed | ~500 | 2,000 |
| Reply rate | ~8% | 15% |
| Bounce rate | ~3% | <2% |
| AI draft approval rate | ~60% | 80% |
| Crash recovery success | 100% | 100% |
| Daily sends | ~50 | 100 |

---

## 10. RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Gmail API quota exhaustion | Medium | High | Quota rollback + resume |
| Ollama server down | Medium | Medium | Graceful fallback (no AI) |
| Database corruption | Low | High | DB check + cleanup tools |
| Google OAuth expiry | Medium | Medium | Web OAuth fallback |
| No analytics visibility | Low (FIXED) | Medium | Charts v4.3 |

---

**Document Owner:** Om (RoboPirate)
**Last Updated:** 2026-06-03
**Next Review:** 2026-07-03
**Status:** APPROVED
