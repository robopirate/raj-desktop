# SECURITY & ACCESS CONTROL DOCUMENT
## Raj AI Gmail Agent v5.0
### RoboPirate Technologies | 2026-06-03

---

## 1. SECURITY POSTURE

**Current Status:** Partially secured — production-hardened for single-user desktop use.
**Risk Level:** LOW (single-user desktop app with local data)
**Audit Date:** 2026-06-03

---

## 2. AUTHENTICATION

### 2.1 Gmail OAuth (Primary)
```
Flow:       Desktop OAuth 2.0 (installed application)
Scope:      https://www.googleapis.com/auth/gmail.send
Token:      Stored in token.pickle (local filesystem)
Expiry:     Auto-refreshed by google-auth library
Revocation: Manual via Google Account settings
```
**Security Notes:**
- ✅ Token is stored locally, not transmitted
- ✅ OAuth scope is minimal (send only, not full inbox access)
- ⚠️ token.pickle is not encrypted at rest
- ⚠️ No token expiry alerts

### 2.2 Web OAuth (Cloud — Render)
```
Flow:       Web server OAuth 2.0
Client ID:  Configured in Render environment
Secret:     Stored in Render env vars (encrypted at rest by Render)
Redirect:   https://raj-web-app.onrender.com/oauth2callback
```
**Security Notes:**
- ✅ Client secret in env vars (not in code)
- ✅ HTTPS redirect URI
- ⚠️ Session management not implemented (no JWT)

### 2.3 Recommended: Token Encryption (FUTURE)
```python
# Encrypt token.pickle with Fernet
from cryptography.fernet import Fernet
key = Fernet.generate_key()
# Store key in OS keychain (keyring library)
# Encrypt/decrypt token.pickle transparently
```

---

## 3. AUTHORIZATION

### 3.1 Current Model: Single User
```
Owner: info@robopirate.in
Access: Full control (no RBAC)
Scope: All features unrestricted
```
**Status:** Acceptable for single-user desktop app.

### 3.2 Gmail Scope Minimization
**Current scope:** `gmail.send` — Can only send emails.
**NOT requested:**
- ❌ gmail.readonly (inbox access)
- ❌ gmail.modify (modify emails)
- ❌ gmail.metadata (metadata access)

**This is CORRECT.** Raj only needs send permission.

### 3.3 Future: Multi-User (FUTURE)
```
Role: admin     → Full control, settings, all sequences
Role: operator  → Send batches, view analytics
Role: viewer    → Read-only dashboard access
```

---

## 4. DATA PROTECTION

### 4.1 Local Data (SQLite)
| Asset | Location | Protection | Risk |
|-------|----------|------------|------|
| campaign_data.db | Local filesystem | None (plaintext) | Low (single user) |
| token.pickle | Local filesystem | None (binary) | Medium (OAuth token) |
| credentials.json | Local filesystem | None (JSON) | Low (public client ID) |
| export/*.csv | Local filesystem | None (CSV) | Low (user-controlled) |

### 4.2 Cloud Data (PostgreSQL — Render)
| Asset | Location | Protection | Risk |
|-------|----------|------------|------|
| PostgreSQL DB | Render Singapore | SSL + password | Low (managed) |
| Connection URL | Render env vars | Encrypted at rest | Low |

### 4.3 Recommended: Database Encryption (FUTURE)
```sql
-- Encrypt sensitive fields
ALTER TABLE recipients ADD COLUMN email_encrypted BLOB;
-- Use SQLCipher for full DB encryption
```

### 4.4 PII Handling
**Data collected:**
- Recipient email addresses
- Recipient names
- Recipient organizations
- Email content (outbound)
- Reply content (inbound)

**Compliance:**
- ⚠️ No GDPR/CCPA compliance framework
- ⚠️ No data retention policy
- ⚠️ No data deletion mechanism (beyond blacklist)
- ✅ Data stored locally (not third-party servers)

---

## 5. BLACKLIST & ABUSE PREVENTION

### 5.1 Auto-Blacklist Rules (ACTIVE)
```
Rule 1: Hard bounce      → Auto-blacklist (permanent)
Rule 2: Hostile reply    → Auto-blacklist (permanent)
Rule 3: Unsubscribe req  → Auto-blacklist (permanent)
Rule 4: Own domain       → NEVER blacklist (protection)
Rule 5: Auto-reply (OOO) → Skip (not blacklisted)
```

### 5.2 Rate Limiting
```
Per-batch stagger:     2 minutes between sends
Daily limit:           Gmail API quota (1M/day)
Sequence cap:          5 touchpoints max (D1, D3, D5, D7, D10)
Sunday pause:          No sends on Sunday
```

### 5.3 Anti-Spam Measures
```
✅ Staggered sends (not bulk)
✅ HTML with unsubscribe text
✅ Reply-to set (info@robopirate.in)
✅ From name set (RoboPirate)
✅ Bounce handling (clean list)
✅ Blacklist protection (no re-send)
```

---

## 6. EMERGENCY CONTROLS

### 6.1 Email-Based Emergency Commands
```
Send email to: info@robopirate.in
Subject: STOP SCHOOL    → Pause school sequence
Subject: STOP CSR       → Pause CSR sequence
Subject: STOP ALL       → Pause all sequences
Subject: RESUME SCHOOL  → Resume school sequence
Subject: RESUME CSR     → Resume CSR sequence
Subject: RESUME ALL     → Resume all sequences
```
**Security:** Only processes emails FROM info@robopirate.in (owner)

### 6.2 System Tray
```
Right-click tray icon → Pause/Resume/Exit
```

### 6.3 Kill Switch
```
Ctrl+C in terminal    → Graceful shutdown
Force quit            → Resume-on-boot recovers
```

---

## 7. AUDIT & LOGGING

### 7.1 Audit Log (audit_log table)
```
Fields: timestamp, action, user, details, status
```
**Logged events:**
- Batch created/run/paused/deleted
- Email sent/bounced/replied
- Blacklist add/remove
- Template sync/lock
- Settings changed
- Emergency command received

### 7.2 Recommended: Security Audit Log (FUTURE)
```
Additional fields: ip_address, user_agent, session_id
Events: login, logout, failed_auth, permission_denied
```

---

## 8. VULNERABILITY ASSESSMENT

| # | Vulnerability | Severity | Status | Mitigation |
|---|--------------|----------|--------|------------|
| 1 | token.pickle not encrypted | MEDIUM | Open | Encrypt with Fernet |
| 2 | No session management (web) | LOW | Open | Add JWT for web mode |
| 3 | No input validation on import | LOW | Open | Validate CSV schema |
| 4 | SQL injection (theoretical) | LOW | Mitigated | Parameterized queries |
| 5 | No rate limiting on API | LOW | Open | Add Flask-Limiter |
| 6 | No HTTPS on local Flask | LOW | Accepted | Localhost only |
| 7 | credentials.json in repo | LOW | Mitigated | Public client ID only |
| 8 | No backup strategy | MEDIUM | Open | Automated DB backup |
| 9 | No data retention policy | MEDIUM | Open | Define retention rules |
| 10 | PII in plaintext DB | LOW | Accepted | Single-user desktop |

---

## 9. SECURITY CHECKLIST

### 9.1 Pre-Release
- [ ] Encrypt token.pickle
- [ ] Add input validation on all API endpoints
- [ ] Sanitize all SQL queries (verify parameterized)
- [ ] Remove any debug credentials from code
- [ ] Verify Gmail scope is minimal

### 9.2 Ongoing
- [ ] Review audit_log weekly
- [ ] Monitor blacklist additions
- [ ] Check for unusual send patterns
- [ ] Update dependencies monthly
- [ ] Backup database weekly

---

## 10. INCIDENT RESPONSE

| Incident | Response |
|----------|----------|
| Gmail account compromised | Revoke OAuth token immediately, re-authenticate |
| Database corruption | Restore from backup, run db_check.py |
| Unauthorized sends | STOP ALL via emergency email, investigate audit log |
| Ollama generating bad replies | Disable AI drafting, manual review |
| Token expiry | Re-run OAuth flow (automatic for desktop) |

---

**Document Owner:** Om (RoboPirate)
**Last Updated:** 2026-06-03
**Next Security Review:** 2026-07-03
**Status:** APPROVED
