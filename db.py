"""
db.py -- RoboPirate Campaign Database v5.0 (Pool-Based Architecture)
All leads go to DB first. Batches are created FROM the pool.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "campaign_data.db"

# Valid batch_recipient statuses
BATCH_RECIPIENT_STATUSES = [
    'pending', 'sent', 'failed', 'skipped', 'drafted', 'bounced', 'replied', 'stopped'
]

class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or str(DB_PATH)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        # Enable WAL mode for concurrent reads during writes (fixes UI lag)
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        self._init_tables()
        self._migrate_schema()

    def _init_tables(self):
        self.conn.executescript("""
            PRAGMA foreign_keys = ON;

            -- Sequences
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                audience TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            -- Recipients (leads) -- POOL
            CREATE TABLE IF NOT EXISTS recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_id TEXT,
                email TEXT NOT NULL,
                name TEXT,
                org TEXT,
                extra_json TEXT,
                sub_pool TEXT DEFAULT '',
                import_status TEXT DEFAULT 'pending',
                import_error TEXT,
                imported_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sequence_id, email)
            );
            CREATE INDEX IF NOT EXISTS idx_recipients_sequence ON recipients(sequence_id);

            -- Batches
            CREATE TABLE IF NOT EXISTS batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sequence_id TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                scheduled_at TEXT,
                timezone TEXT DEFAULT 'Asia/Kolkata',
                send_rate INTEGER DEFAULT 0,
                stagger_minutes INTEGER DEFAULT 0,
                day_offset INTEGER DEFAULT 1,
                parent_batch_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                started_at TEXT,
                completed_at TEXT,
                deleted_at TEXT
            );

            -- Batch Recipients
            CREATE TABLE IF NOT EXISTS batch_recipients (
                batch_id INTEGER,
                recipient_id INTEGER,
                status TEXT DEFAULT 'pending',
                sent_at TEXT,
                opened_at TEXT,
                replied_at TEXT,
                bounced_at TEXT,
                PRIMARY KEY (batch_id, recipient_id),
                FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id) ON DELETE CASCADE
            );

            -- Templates
            CREATE TABLE IF NOT EXISTS templates (
                sequence_id TEXT,
                day INTEGER,
                subject TEXT,
                subject_b TEXT,
                html_body TEXT,
                source TEXT DEFAULT 'unknown',
                locked INTEGER DEFAULT 0,
                ab_test INTEGER DEFAULT 0,
                ab_split REAL DEFAULT 0.5,
                cached_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (sequence_id, day)
            );

            -- Sends (pipeline tracking)
            CREATE TABLE IF NOT EXISTS sends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER,
                batch_id INTEGER,
                day INTEGER,
                subject TEXT,
                draft_id TEXT,
                status TEXT DEFAULT 'drafted',
                ab_variant TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                sent_at TEXT,
                opened_at TEXT,
                clicked_at TEXT,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id),
                FOREIGN KEY (batch_id) REFERENCES batches(id)
            );
            CREATE INDEX IF NOT EXISTS idx_sends_recipient ON sends(recipient_id);
            CREATE INDEX IF NOT EXISTS idx_sends_batch ON sends(batch_id);
            CREATE INDEX IF NOT EXISTS idx_sends_status ON sends(status);

            -- Blacklist
            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                reason TEXT,
                source TEXT DEFAULT 'manual',
                added_by TEXT DEFAULT 'user',
                added_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_blacklist_email ON blacklist(email);

            -- Replies
            CREATE TABLE IF NOT EXISTS replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                send_id INTEGER,
                recipient_id INTEGER,
                thread_id TEXT NOT NULL,
                message_id TEXT NOT NULL UNIQUE,
                from_addr TEXT,
                subject TEXT,
                body TEXT,
                sentiment TEXT,
                summary TEXT,
                draft_reply_id TEXT,
                draft_html TEXT,
                status TEXT DEFAULT 'pending',
                received_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id),
                FOREIGN KEY (send_id) REFERENCES sends(id)
            );
            CREATE INDEX IF NOT EXISTS idx_replies_status ON replies(status);

            -- Calendar Events
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reply_id INTEGER,
                event_id TEXT,
                calendar_link TEXT,
                scheduled_at TEXT,
                status TEXT DEFAULT 'draft',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reply_id) REFERENCES replies(id)
            );

            -- Drive Files
            CREATE TABLE IF NOT EXISTS drive_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT,
                file_id TEXT,
                file_name TEXT,
                file_url TEXT,
                validated_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            -- Pending Resumes
            CREATE TABLE IF NOT EXISTS pending_resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_id TEXT NOT NULL,
                day INTEGER NOT NULL,
                recipient_id INTEGER NOT NULL,
                subject TEXT,
                status TEXT DEFAULT 'pending',
                error TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                resumed_at TEXT,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id)
            );

            -- Meta / Config
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            -- Outreach Campaigns
            CREATE TABLE IF NOT EXISTS outreach_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sequence_id TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                total_leads INTEGER DEFAULT 0,
                auto_advance INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                started_at TEXT,
                completed_at TEXT
            );

            -- Audit Log
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT,
                user TEXT DEFAULT 'system',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);

            -- Engagement Events (opens, clicks)
            CREATE TABLE IF NOT EXISTS engagement_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER,
                batch_id INTEGER,
                send_id INTEGER,
                event_type TEXT NOT NULL,
                url TEXT,
                user_agent TEXT,
                ip_address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id),
                FOREIGN KEY (batch_id) REFERENCES batches(id),
                FOREIGN KEY (send_id) REFERENCES sends(id)
            );
            CREATE INDEX IF NOT EXISTS idx_engagement_type ON engagement_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_engagement_recipient ON engagement_events(recipient_id);
            CREATE INDEX IF NOT EXISTS idx_engagement_batch ON engagement_events(batch_id);
        """)

        for seq_id, name, audience in [("school","SCHOOL","private_school"), ("csr","CSR","csr"), ("csr-wsl-5","CSR-WSL-5","csr")]:
            self.execute("INSERT OR IGNORE INTO campaigns (id, name, audience) VALUES (?, ?, ?)", 
                        (seq_id, name, audience))
        self.conn.commit()

    def _migrate_schema(self):
        """Auto-migrate database schema when code updates."""
        # Add parent_batch_id to batches if missing
        try:
            self.conn.execute("SELECT parent_batch_id FROM batches LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Adding parent_batch_id to batches...")
            self.conn.execute("ALTER TABLE batches ADD COLUMN parent_batch_id INTEGER")
            self.conn.commit()
            print("[DB] Migration complete: parent_batch_id added")
        # Add engagement_events table if missing
        try:
            self.conn.execute("SELECT 1 FROM engagement_events LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Adding engagement_events table...")
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS engagement_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient_id INTEGER,
                    batch_id INTEGER,
                    send_id INTEGER,
                    event_type TEXT NOT NULL,
                    url TEXT,
                    user_agent TEXT,
                    ip_address TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (recipient_id) REFERENCES recipients(id),
                    FOREIGN KEY (batch_id) REFERENCES batches(id),
                    FOREIGN KEY (send_id) REFERENCES sends(id)
                );
                CREATE INDEX IF NOT EXISTS idx_engagement_type ON engagement_events(event_type);
                CREATE INDEX IF NOT EXISTS idx_engagement_recipient ON engagement_events(recipient_id);
                CREATE INDEX IF NOT EXISTS idx_engagement_batch ON engagement_events(batch_id);
            """)
            self.conn.commit()
            print("[DB] Migration complete: engagement_events table added")

        # Add sub_pool to recipients if missing
        try:
            self.conn.execute("SELECT sub_pool FROM recipients LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Adding sub_pool to recipients...")
            self.conn.execute("ALTER TABLE recipients ADD COLUMN sub_pool TEXT DEFAULT ''")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_recipients_sub_pool ON recipients(sub_pool)")
            self.conn.commit()
            print("[DB] Migration complete: sub_pool added")

        # Add batched flag to recipients if missing
        try:
            self.conn.execute("SELECT batched FROM recipients LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Adding batched flag to recipients...")
            self.conn.execute("ALTER TABLE recipients ADD COLUMN batched INTEGER DEFAULT 0")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_recipients_batched ON recipients(batched)")
            self.conn.commit()
            print("[DB] Migration complete: batched flag added")

            # Fix: Mark leads already in batches as batched=1
            print("[DB] Fixing existing batch recipients...")
            self.conn.execute("""
                UPDATE recipients SET batched=1 
                WHERE id IN (SELECT DISTINCT recipient_id FROM batch_recipients)
            """)
            self.conn.commit()
            fixed = self.conn.execute("SELECT changes()").fetchone()[0]
            print(f"[DB] Marked {fixed} existing batch recipients as batched=1")

        # Add campaign_id to batches if missing
        try:
            self.conn.execute("SELECT campaign_id FROM batches LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Adding campaign_id to batches...")
            self.conn.execute("ALTER TABLE batches ADD COLUMN campaign_id INTEGER")
            self.conn.commit()
            print("[DB] Migration complete: campaign_id added")

        # Add deleted_at to batches if missing
        try:
            self.conn.execute("SELECT deleted_at FROM batches LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Adding deleted_at to batches...")
            self.conn.execute("ALTER TABLE batches ADD COLUMN deleted_at TEXT")
            self.conn.commit()
            print("[DB] Migration complete: deleted_at added")

        # Create outreach_campaigns table if missing
        try:
            self.conn.execute("SELECT 1 FROM outreach_campaigns LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Creating outreach_campaigns table...")
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS outreach_campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sequence_id TEXT NOT NULL,
                    status TEXT DEFAULT 'draft',
                    total_leads INTEGER DEFAULT 0,
                    auto_advance INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    started_at TEXT,
                    completed_at TEXT
                )
            """)
            self.conn.commit()
            print("[DB] Migration complete: outreach_campaigns table created")

        # Add recipient_id to replies if missing
        try:
            self.conn.execute("SELECT recipient_id FROM replies LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Adding recipient_id to replies...")
            self.conn.execute("ALTER TABLE replies ADD COLUMN recipient_id INTEGER")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_replies_recipient ON replies(recipient_id)")
            self.conn.commit()
            # Backfill recipient_id from sends
            self.conn.execute("""
                UPDATE replies SET recipient_id = (
                    SELECT recipient_id FROM sends WHERE sends.id = replies.send_id
                ) WHERE recipient_id IS NULL
            """)
            self.conn.commit()
            print("[DB] Migration complete: recipient_id added to replies")

        # Add draft_html to replies if missing
        try:
            self.conn.execute("SELECT draft_html FROM replies LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Adding draft_html to replies...")
            self.conn.execute("ALTER TABLE replies ADD COLUMN draft_html TEXT")
            self.conn.commit()
            print("[DB] Migration complete: draft_html added to replies")

        # Add A/B test columns to templates if missing
        for col, col_type in [("subject_b", "TEXT"), ("ab_test", "INTEGER DEFAULT 0"), ("ab_split", "REAL DEFAULT 0.5")]:
            try:
                self.conn.execute(f"SELECT {col} FROM templates LIMIT 1")
            except sqlite3.OperationalError:
                print(f"[DB] Migrating: Adding {col} to templates...")
                self.conn.execute(f"ALTER TABLE templates ADD COLUMN {col} {col_type}")
                self.conn.commit()
                print(f"[DB] Migration complete: {col} added to templates")

        # Add ab_variant to sends if missing
        try:
            self.conn.execute("SELECT ab_variant FROM sends LIMIT 1")
        except sqlite3.OperationalError:
            print("[DB] Migrating: Adding ab_variant to sends...")
            self.conn.execute("ALTER TABLE sends ADD COLUMN ab_variant TEXT")
            self.conn.commit()
            print("[DB] Migration complete: ab_variant added to sends")

    def execute(self, sql, params=()):
        return self.conn.execute(sql, params)

    def commit(self):
        self.conn.commit()

    # -- RECIPIENTS / POOL --
    def recipient_add(self, sequence_id, email, name, org, extra_json=None, sub_pool=None):
        try:
            self.execute("""
                INSERT INTO recipients (sequence_id, email, name, org, extra_json, sub_pool, import_status, batched)
                VALUES (?, ?, ?, ?, ?, ?, 'success', 0)
                ON CONFLICT(sequence_id, email) DO UPDATE SET
                    name=excluded.name, org=excluded.org, extra_json=excluded.extra_json,
                    sub_pool=excluded.sub_pool, import_status='success', import_error=NULL, batched=0
            """, (sequence_id, email.lower().strip(), name, org, extra_json, sub_pool or ''))
            self.commit()
            return True, None
        except Exception as e:
            return False, str(e)

    def recipient_get_by_sequence(self, sequence_id):
        rows = self.execute("SELECT * FROM recipients WHERE sequence_id=? ORDER BY id", (sequence_id,)).fetchall()
        return [dict(r) for r in rows]

    def recipient_count(self, sequence_id=None):
        if sequence_id:
            row = self.execute("SELECT COUNT(*) FROM recipients WHERE sequence_id=?", (sequence_id,)).fetchone()
        else:
            row = self.execute("SELECT COUNT(*) FROM recipients").fetchone()
        return row[0] if row else 0

    def recipient_delete(self, recipient_id):
        self.execute("DELETE FROM recipients WHERE id=?", (recipient_id,))
        self.commit()

    # -- POOL METHODS (NEW) --
    def get_pool(self, sequence_id, sub_pool=None, limit=None):
        """Get unbatched leads from the pool. Excludes blacklisted emails.
        Optionally filter by sub_pool tag."""
        if sequence_id is None or sequence_id == "leads":
            where_clause = "r.sequence_id='leads' AND r.batched=0"
            params = []
        else:
            where_clause = "r.sequence_id=? AND r.batched=0"
            params = [sequence_id]
        if sub_pool:
            where_clause += " AND r.sub_pool = ?"
            params.append(sub_pool)
        sql = f"""
            SELECT r.* FROM recipients r
            WHERE {where_clause}
              AND NOT EXISTS (SELECT 1 FROM blacklist b WHERE b.email=r.email)
            ORDER BY r.id
        """
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        rows = self.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def get_pool_count(self, sequence_id, sub_pool=None):
        """Count unbatched leads in pool. Excludes blacklisted emails.
        Optionally filter by sub_pool tag."""
        if sequence_id is None or sequence_id == "leads":
            where_clause = "r.sequence_id='leads' AND r.batched=0"
            params = []
        else:
            where_clause = "r.sequence_id=? AND r.batched=0"
            params = [sequence_id]
        if sub_pool:
            where_clause += " AND r.sub_pool = ?"
            params.append(sub_pool)
        row = self.execute(f"""
            SELECT COUNT(*) FROM recipients r
            WHERE {where_clause}
              AND NOT EXISTS (SELECT 1 FROM blacklist b WHERE b.email=r.email)
        """, params).fetchone()
        return row[0] if row else 0

    def mark_batched(self, recipient_ids):
        """Mark leads as batched (moved from pool to a batch)."""
        if not recipient_ids:
            return
        placeholders = ','.join('?' * len(recipient_ids))
        self.execute(f"UPDATE recipients SET batched=1 WHERE id IN ({placeholders})", recipient_ids)
        self.commit()

    def unmark_batched(self, recipient_ids):
        """Return leads to pool (e.g., batch deleted)."""
        if not recipient_ids:
            return
        placeholders = ','.join('?' * len(recipient_ids))
        self.execute(f"UPDATE recipients SET batched=0 WHERE id IN ({placeholders})", recipient_ids)
        self.commit()

    # -- BATCHES --
    def batch_create(self, name, sequence_id, scheduled_at=None, timezone='Asia/Kolkata', 
                     send_rate=0, stagger_minutes=0, day_offset=1, parent_batch_id=None, campaign_id=None):
        cur = self.execute("""
            INSERT INTO batches (name, sequence_id, status, scheduled_at, timezone, send_rate, stagger_minutes, day_offset, parent_batch_id, campaign_id)
            VALUES (?, ?, 'draft', ?, ?, ?, ?, ?, ?, ?)
        """, (name, sequence_id, scheduled_at, timezone, send_rate, stagger_minutes, day_offset, parent_batch_id, campaign_id))
        self.commit()
        return cur.lastrowid

    def batch_add_recipient(self, batch_id, recipient_id):
        try:
            self.execute("INSERT OR IGNORE INTO batch_recipients (batch_id, recipient_id) VALUES (?, ?)",
                        (batch_id, recipient_id))
            self.commit()
            return True
        except:
            return False

    def batch_get(self, batch_id):
        row = self.execute("SELECT * FROM batches WHERE id=?", (batch_id,)).fetchone()
        return dict(row) if row else None

    def batch_get_all(self, sequence_id=None):
        if sequence_id:
            rows = self.execute("SELECT * FROM batches WHERE sequence_id=? AND deleted_at IS NULL ORDER BY created_at DESC", (sequence_id,)).fetchall()
        else:
            rows = self.execute("SELECT * FROM batches WHERE deleted_at IS NULL ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def batch_soft_delete(self, batch_id):
        """Soft delete a batch: mark as deleted and return leads to pool.
        Returns number of leads returned."""
        self.execute("UPDATE batches SET deleted_at = CURRENT_TIMESTAMP, status='deleted' WHERE id=?", (batch_id,))
        recipient_rows = self.execute("SELECT recipient_id FROM batch_recipients WHERE batch_id=?", (batch_id,)).fetchall()
        recipient_ids = [r[0] for r in recipient_rows]
        self.unmark_batched(recipient_ids)
        self.commit()
        return len(recipient_ids)

    def batch_get_deleted(self):
        """Get all soft-deleted batches, newest first."""
        rows = self.execute("SELECT * FROM batches WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC").fetchall()
        return [dict(r) for r in rows]

    def batch_exists(self, batch_id):
        """Check if a batch exists (including deleted)."""
        return self.batch_get(batch_id) is not None

    def get_running_batches(self):
        """Get all batches currently in 'running' status. For resume-on-boot."""
        rows = self.execute("SELECT * FROM batches WHERE status='running' AND deleted_at IS NULL ORDER BY created_at").fetchall()
        return [dict(r) for r in rows]

    def get_scheduled_batches(self):
        """Get all batches in 'scheduled' status. For auto-start check."""
        rows = self.execute("SELECT * FROM batches WHERE status='scheduled' AND deleted_at IS NULL ORDER BY scheduled_at").fetchall()
        return [dict(r) for r in rows]

    def batch_update_status(self, batch_id, status):
        self.execute("UPDATE batches SET status=? WHERE id=?", (status, batch_id))
        if status == 'running':
            self.execute("UPDATE batches SET started_at=CURRENT_TIMESTAMP WHERE id=?", (batch_id,))
        elif status == 'completed':
            self.execute("UPDATE batches SET completed_at=CURRENT_TIMESTAMP WHERE id=?", (batch_id,))
        self.commit()

    def batch_get_recipients(self, batch_id):
        rows = self.execute("""
            SELECT r.*, br.status as batch_status, br.sent_at 
            FROM recipients r 
            JOIN batch_recipients br ON r.id = br.recipient_id 
            WHERE br.batch_id=?
        """, (batch_id,)).fetchall()
        return [dict(r) for r in rows]

    def batch_delete(self, batch_id):
        # Return leads to pool before deleting
        recipient_ids = [r["id"] for r in self.batch_get_recipients(batch_id)]
        self.unmark_batched(recipient_ids)
        # Delete sends first (FK constraint)
        self.execute("DELETE FROM sends WHERE batch_id=?", (batch_id,))
        self.execute("DELETE FROM batches WHERE id=?", (batch_id,))
        self.commit()

    def batch_count_recipients(self, batch_id):
        row = self.execute("SELECT COUNT(*) FROM batch_recipients WHERE batch_id=?", (batch_id,)).fetchone()
        return row[0] if row else 0

    def batch_count_by_status(self, batch_id):
        rows = self.execute("""
            SELECT status, COUNT(*) FROM batch_recipients WHERE batch_id=? GROUP BY status
        """, (batch_id,)).fetchall()
        return {r[0]: r[1] for r in rows}

    # -- CREATE BATCH FROM POOL (NEW) --
    def batch_from_pool(self, name, sequence_id, batch_size, sub_pool=None, day_offset=1, 
                        scheduled_at=None, timezone='Asia/Kolkata', send_rate=0, stagger_minutes=0, campaign_id=None):
        """Create a batch from unbatched leads in the pool.
        SAFETY: Only picks leads with batched=0. Double-checks before marking.
        Optionally filter by sub_pool tag."""
        pool_seq_id = "leads" if sequence_id is None or sequence_id == "leads" else sequence_id
        batch_seq_id = "unassigned" if sequence_id is None or sequence_id == "leads" else sequence_id
        
        pool = self.get_pool(pool_seq_id, sub_pool, limit=batch_size)
        if not pool:
            return None, "No unbatched leads in pool for this sequence"

        # EXTRA SAFETY: Re-verify all leads are still unbatched (race condition protection)
        verified_pool = []
        for lead in pool:
            check = self.execute("SELECT batched FROM recipients WHERE id=?", (lead["id"],)).fetchone()
            if check and check[0] == 0:
                verified_pool.append(lead)
            else:
                print(f"[DB-SAFETY] Skipping lead {lead['id']} — already batched (race condition)")

        if not verified_pool:
            return None, "All available leads were taken by another batch (race condition). Try again."

        batch_id = self.batch_create(
            name=name,
            sequence_id=batch_seq_id,
            scheduled_at=scheduled_at,
            timezone=timezone,
            send_rate=send_rate,
            stagger_minutes=stagger_minutes,
            day_offset=day_offset,
            campaign_id=campaign_id
        )

        recipient_ids = []
        for lead in verified_pool:
            self.batch_add_recipient(batch_id, lead["id"])
            recipient_ids.append(lead["id"])

        self.mark_batched(recipient_ids)
        return batch_id, None

    # -- TEMPLATES --
    def template_put(self, sequence_id, day, subject, html_body, source="synced",
                      subject_b=None, ab_test=0, ab_split=0.5):
        self.execute("""
            INSERT INTO templates (sequence_id, day, subject, subject_b, html_body, source, ab_test, ab_split)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sequence_id, day) DO UPDATE SET
                subject=excluded.subject, subject_b=excluded.subject_b,
                html_body=excluded.html_body, source=excluded.source,
                ab_test=excluded.ab_test, ab_split=excluded.ab_split,
                cached_at=CURRENT_TIMESTAMP
        """, (sequence_id, day, subject, subject_b, html_body, source, ab_test, ab_split))
        self.commit()

    def template_get(self, sequence_id, day):
        row = self.execute("""
            SELECT subject, subject_b, html_body, source, locked, ab_test, ab_split
            FROM templates WHERE sequence_id=? AND day=?
        """, (sequence_id, day)).fetchone()
        if not row:
            return None
        return {
            "subject": row[0], "subject_b": row[1], "html_body": row[2],
            "source": row[3], "locked": bool(row[4]),
            "ab_test": bool(row[5]), "ab_split": row[6]
        }

    def template_lock(self, sequence_id, day):
        self.execute("UPDATE templates SET locked=1 WHERE sequence_id=? AND day=?", (sequence_id, day))
        self.commit()

    def template_unlock(self, sequence_id, day):
        self.execute("UPDATE templates SET locked=0 WHERE sequence_id=? AND day=?", (sequence_id, day))
        self.commit()

    def template_is_locked(self, sequence_id, day):
        row = self.execute("SELECT locked FROM templates WHERE sequence_id=? AND day=?", (sequence_id, day)).fetchone()
        return bool(row[0]) if row else False

    # -- SENDS / PIPELINE --
    def campaign_queue_send(self, recipient_id, day, subject, draft_id, status="drafted",
                            batch_id=None, ab_variant=None):
        cur = self.execute("""
            INSERT INTO sends (recipient_id, day, subject, draft_id, status, batch_id, ab_variant)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (recipient_id, day, subject, draft_id, status, batch_id, ab_variant))
        self.commit()
        return cur.lastrowid

    def get_pipeline(self, sequence_id=None):
        sql = """
            SELECT 
                r.sequence_id,
                COUNT(DISTINCT r.id) as total_recipients,
                COUNT(DISTINCT CASE WHEN s.status='drafted' THEN s.recipient_id END) as drafted,
                COUNT(DISTINCT CASE WHEN s.status='sent' THEN s.recipient_id END) as sent,
                COUNT(DISTINCT CASE WHEN s.status='bounced' THEN s.recipient_id END) as bounced,
                COUNT(DISTINCT CASE WHEN s.status='replied' THEN s.recipient_id END) as replied
            FROM recipients r
            LEFT JOIN sends s ON r.id = s.recipient_id
        """
        if sequence_id:
            sql += " WHERE r.sequence_id=?"
            rows = self.execute(sql + " GROUP BY r.sequence_id", (sequence_id,)).fetchall()
        else:
            rows = self.execute(sql + " GROUP BY r.sequence_id").fetchall()
        return [dict(r) for r in rows]

    def get_day_wise_pipeline(self, sequence_id):
        rows = self.execute("""
            SELECT day,
                COUNT(DISTINCT recipient_id) as total,
                COUNT(DISTINCT CASE WHEN status='sent' THEN recipient_id END) as sent,
                COUNT(DISTINCT CASE WHEN status='bounced' THEN recipient_id END) as bounced,
                COUNT(DISTINCT CASE WHEN status='replied' THEN recipient_id END) as replied
            FROM sends
            WHERE recipient_id IN (SELECT id FROM recipients WHERE sequence_id=?)
            GROUP BY day
            ORDER BY day
        """, (sequence_id,)).fetchall()
        return {r[0]: {"total": r[1], "sent": r[2], "bounced": r[3], "replied": r[4]} for r in rows}

    # -- BLACKLIST --
    def blacklist_add(self, email, reason="manual", source="user"):
        self.execute("""
            INSERT INTO blacklist (email, reason, source) 
            VALUES (?, ?, ?) 
            ON CONFLICT(email) DO UPDATE SET reason=excluded.reason, source=excluded.source
        """, (email.lower().strip(), reason, source))
        self.commit()

    def blacklist_remove(self, email_or_id):
        if isinstance(email_or_id, int):
            self.execute("DELETE FROM blacklist WHERE id=?", (email_or_id,))
        else:
            self.execute("DELETE FROM blacklist WHERE email=?", (email_or_id.lower().strip(),))
        self.commit()

    def blacklist_has(self, email):
        return self.execute("SELECT 1 FROM blacklist WHERE email=?", (email.lower().strip(),)).fetchone() is not None

    def recipient_exists(self, email):
        """Check if email exists in the recipients table (our lead pool)."""
        return self.execute("SELECT 1 FROM recipients WHERE email=?", (email.lower().strip(),)).fetchone() is not None

    def was_sent_to(self, email):
        """Check if we have a 'sent' record for this email in the sends table."""
        return self.execute(
            "SELECT 1 FROM sends s JOIN recipients r ON s.recipient_id = r.id WHERE r.email=? AND s.status='sent' LIMIT 1",
            (email.lower().strip(),)
        ).fetchone() is not None

    def blacklist_get_all(self):
        rows = self.execute("SELECT * FROM blacklist ORDER BY added_at DESC").fetchall()
        return [dict(r) for r in rows]

    def mark_email_bounced(self, email, reason="bounce"):
        """Mark the latest sent send for an email as bounced and update batch_recipients."""
        rows = self.execute(
            "SELECT id FROM recipients WHERE email=? ORDER BY id",
            (email.lower().strip(),)
        ).fetchall()
        if not rows:
            return 0

        updated = 0
        for (recipient_id,) in rows:
            send_row = self.execute(
                """SELECT id, batch_id FROM sends
                   WHERE recipient_id=? AND status='sent'
                   ORDER BY COALESCE(sent_at, created_at) DESC LIMIT 1""",
                (recipient_id,)
            ).fetchone()
            if not send_row:
                continue
            send_id, batch_id = send_row
            self.execute("UPDATE sends SET status='bounced' WHERE id=?", (send_id,))
            if batch_id:
                self.execute(
                    """UPDATE batch_recipients
                       SET status='bounced', bounced_at=CURRENT_TIMESTAMP
                       WHERE batch_id=? AND recipient_id=?""",
                    (batch_id, recipient_id)
                )
            updated += 1

        self.commit()
        return updated

    # -- ENGAGEMENT TRACKING --
    def record_engagement(self, event_type, recipient_id=None, batch_id=None, send_id=None, url=None, user_agent=None, ip_address=None):
        """Record an open or click event."""
        self.execute("""
            INSERT INTO engagement_events (recipient_id, batch_id, send_id, event_type, url, user_agent, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (recipient_id, batch_id, send_id, event_type, url, user_agent, ip_address))
        # Also update the sends table for quick lookups
        if send_id:
            if event_type == 'open':
                self.execute("UPDATE sends SET opened_at=COALESCE(opened_at, CURRENT_TIMESTAMP) WHERE id=?", (send_id,))
            elif event_type == 'click':
                self.execute("UPDATE sends SET clicked_at=COALESCE(clicked_at, CURRENT_TIMESTAMP) WHERE id=?", (send_id,))
        self.commit()

    def get_engagement_stats(self, batch_id=None, sequence_id=None, days_back=30):
        """Get aggregated engagement stats. Returns dict with sent, opened, clicked, ctr."""
        params = []
        where = "WHERE s.status='sent'"
        if batch_id:
            where += " AND s.batch_id=?"
            params.append(batch_id)
        if sequence_id:
            where += " AND b.sequence_id=?"
            params.append(sequence_id)
        if days_back:
            where += " AND s.sent_at >= datetime('now', '-{} days')".format(int(days_back))

        sent = self.execute(f"SELECT COUNT(*) FROM sends s JOIN batches b ON s.batch_id=b.id {where}", params).fetchone()[0] or 0
        opened = self.execute(f"SELECT COUNT(DISTINCT s.id) FROM sends s JOIN batches b ON s.batch_id=b.id {where} AND s.opened_at IS NOT NULL", params).fetchone()[0] or 0
        clicked = self.execute(f"SELECT COUNT(DISTINCT s.id) FROM sends s JOIN batches b ON s.batch_id=b.id {where} AND s.clicked_at IS NOT NULL", params).fetchone()[0] or 0

        return {
            "sent": sent,
            "opened": opened,
            "clicked": clicked,
            "open_rate": round(opened / sent * 100, 1) if sent else 0,
            "ctr": round(clicked / sent * 100, 1) if sent else 0,
            "ctor": round(clicked / opened * 100, 1) if opened else 0,
        }

    def get_engagement_by_day(self, sequence_id=None, days_back=30):
        """Get daily engagement breakdown for charting."""
        params = []
        where = "WHERE s.status='sent'"
        if sequence_id:
            where += " AND b.sequence_id=?"
            params.append(sequence_id)
        if days_back:
            where += " AND date(s.sent_at) >= date('now', '-{} days')".format(int(days_back))

        rows = self.execute(f"""
            SELECT date(s.sent_at) as day,
                   COUNT(*) as sent,
                   SUM(CASE WHEN s.opened_at IS NOT NULL THEN 1 ELSE 0 END) as opened,
                   SUM(CASE WHEN s.clicked_at IS NOT NULL THEN 1 ELSE 0 END) as clicked
            FROM sends s
            JOIN batches b ON s.batch_id=b.id
            {where}
            GROUP BY date(s.sent_at)
            ORDER BY day
        """, params).fetchall()
        return [dict(r) for r in rows]

    def get_top_clicked_links(self, batch_id=None, limit=10):
        """Get most clicked URLs."""
        where = "WHERE event_type='click'"
        params = []
        if batch_id:
            where += " AND batch_id=?"
            params.append(batch_id)
        rows = self.execute(f"""
            SELECT url, COUNT(*) as clicks
            FROM engagement_events
            {where}
            GROUP BY url
            ORDER BY clicks DESC
            LIMIT ?
        """, params + [limit]).fetchall()
        return [dict(r) for r in rows]

    def get_send_id_by_recipient_batch(self, recipient_id, batch_id):
        """Get the latest send_id for a recipient in a batch."""
        row = self.execute("""
            SELECT id FROM sends WHERE recipient_id=? AND batch_id=? ORDER BY id DESC LIMIT 1
        """, (recipient_id, batch_id)).fetchone()
        return row[0] if row else None

    # -- META --
    def set_meta(self, key, value):
        self.execute("INSERT INTO meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
        self.commit()

    def get_meta(self, key):
        row = self.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    # -- AUDIT LOG --
    def log_action(self, action, details=None, user='system'):
        self.execute("INSERT INTO audit_log (action, details, user) VALUES (?, ?, ?)", (action, details, user))
        self.commit()

    def get_audit_log(self, limit=50):
        rows = self.execute("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

    # -- BATCH PIPELINE TRACKING --
    def batch_get_pipeline(self, batch_id: int) -> dict:
        batch = self.batch_get(batch_id)
        if not batch:
            return {}

        root_id = batch.get("parent_batch_id") or batch_id
        if batch.get("parent_batch_id") and batch["parent_batch_id"] != batch_id:
            root = self.batch_get(batch["parent_batch_id"])
            if root:
                root_id = root["id"]

        rows = self.execute("""
            SELECT * FROM batches 
            WHERE parent_batch_id=? OR id=? 
            ORDER BY day_offset
        """, (root_id, root_id)).fetchall()

        pipeline_batches = []
        for r in rows:
            b = dict(r)
            counts = self.batch_count_by_status(b["id"])
            b["counts"] = counts
            b["total_recipients"] = sum(counts.values())
            b["sent"] = counts.get("sent", 0)
            pipeline_batches.append(b)

        return {
            "root_batch_id": root_id,
            "root_name": self.batch_get(root_id)["name"] if self.batch_get(root_id) else "Unknown",
            "sequence_id": batch.get("sequence_id", ""),
            "batches": pipeline_batches,
            "total_days": len(pipeline_batches),
            "completed_days": sum(1 for b in pipeline_batches if b["status"] == "completed"),
            "running_days": sum(1 for b in pipeline_batches if b["status"] == "running"),
        }

    def batch_get_all_pipelines(self, sequence_id: str = None) -> list:
        if sequence_id:
            roots = self.execute("""
                SELECT DISTINCT parent_batch_id FROM batches 
                WHERE sequence_id=? AND parent_batch_id IS NOT NULL
            """, (sequence_id,)).fetchall()
        else:
            roots = self.execute("""
                SELECT DISTINCT parent_batch_id FROM batches 
                WHERE parent_batch_id IS NOT NULL
            """).fetchall()

        pipelines = []
        for (root_id,) in roots:
            if root_id:
                pipe = self.batch_get_pipeline(root_id)
                if pipe:
                    pipelines.append(pipe)

        return pipelines


    # -- CAMPAIGNS (NEW) --
    def campaign_create(self, name, sequence_id, total_leads=0, auto_advance=1):
        """Create a new outreach campaign."""
        cur = self.execute("""
            INSERT INTO outreach_campaigns (name, sequence_id, status, total_leads, auto_advance)
            VALUES (?, ?, 'draft', ?, ?)
        """, (name, sequence_id, total_leads, auto_advance))
        self.commit()
        return cur.lastrowid

    def campaign_get(self, campaign_id):
        row = self.execute("SELECT * FROM outreach_campaigns WHERE id=?", (campaign_id,)).fetchone()
        return dict(row) if row else None

    def campaign_get_all(self, status=None):
        if status:
            rows = self.execute("SELECT * FROM outreach_campaigns WHERE status=? ORDER BY created_at DESC", (status,)).fetchall()
        else:
            rows = self.execute("SELECT * FROM outreach_campaigns ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def campaign_update_status(self, campaign_id, status):
        self.execute("UPDATE outreach_campaigns SET status=? WHERE id=?", (status, campaign_id))
        if status == 'active':
            self.execute("UPDATE outreach_campaigns SET started_at=CURRENT_TIMESTAMP WHERE id=?", (campaign_id,))
        elif status == 'completed':
            self.execute("UPDATE outreach_campaigns SET completed_at=CURRENT_TIMESTAMP WHERE id=?", (campaign_id,))
        self.commit()

    def campaign_get_batches(self, campaign_id):
        """Get all batches in a campaign."""
        rows = self.execute("""
            SELECT * FROM batches WHERE campaign_id=? ORDER BY day_offset, created_at
        """, (campaign_id,)).fetchall()
        return [dict(r) for r in rows]

    def campaign_get_pipeline(self, campaign_id):
        """Get full pipeline status for a campaign."""
        campaign = self.campaign_get(campaign_id)
        if not campaign:
            return None

        batches = self.campaign_get_batches(campaign_id)
        pipeline = []
        for b in batches:
            counts = self.batch_count_by_status(b["id"])
            total = sum(counts.values())
            sent = counts.get("sent", 0)
            pipeline.append({
                "batch_id": b["id"],
                "name": b["name"],
                "day": b["day_offset"],
                "status": b["status"],
                "total": total,
                "sent": sent,
                "scheduled_at": b.get("scheduled_at")
            })

        return {
            "campaign": campaign,
            "pipeline": pipeline,
            "total_days": len(pipeline),
            "completed_days": sum(1 for p in pipeline if p["status"] == "completed"),
            "active_days": sum(1 for p in pipeline if p["status"] in ["running", "scheduled"])
        }

    def get_next_batch_in_sequence(self, batch_id):
        """Get the next batch in a campaign sequence."""
        batch = self.batch_get(batch_id)
        if not batch:
            return None

        campaign_id = batch.get("campaign_id")
        if not campaign_id:
            return None

        current_day = batch.get("day_offset", 1)
        rows = self.execute("""
            SELECT * FROM batches 
            WHERE campaign_id=? AND day_offset > ? AND status='draft'
            ORDER BY day_offset LIMIT 1
        """, (campaign_id, current_day)).fetchall()

        return dict(rows[0]) if rows else None


    def get_scheduled_batches(self):
        """Get all batches that are scheduled (ready to run if time passed)."""
        rows = self.execute("""
            SELECT * FROM batches 
            WHERE status='scheduled' 
            ORDER BY scheduled_at
        """).fetchall()
        return [dict(r) for r in rows]

    def assign_sequence_to_batch(self, batch_id, sequence_id):
        """Update a batch and its recipients to a new sequence_id."""
        cur_batch = self.execute("UPDATE batches SET sequence_id=? WHERE id=?", (sequence_id, batch_id))
        cur_recipients = self.execute("""
            UPDATE recipients SET sequence_id=?
            WHERE id IN (SELECT recipient_id FROM batch_recipients WHERE batch_id=?)
        """, (sequence_id, batch_id))
        self.commit()
        return cur_batch.rowcount + cur_recipients.rowcount

    # -- REPLIES --
    def get_replies_with_drafts(self, filter_status=None, filter_sentiment=None, search=None):
        """Get replies joined with recipient info, with optional filters."""
        sql = """
            SELECT r.*, rec.name, rec.email, rec.org
            FROM replies r
            JOIN recipients rec ON r.recipient_id = rec.id
            WHERE 1=1
        """
        params = []
        if filter_status:
            sql += " AND r.status = ?"
            params.append(filter_status)
        if filter_sentiment:
            sql += " AND r.sentiment = ?"
            params.append(filter_sentiment)
        if search:
            sql += " AND (rec.email LIKE ? OR r.subject LIKE ?)"
            like = f"%{search}%"
            params.extend([like, like])
        sql += " ORDER BY r.received_at DESC"
        rows = self.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def mark_reply_handled(self, reply_id):
        """Mark a reply as handled."""
        self.execute("UPDATE replies SET status='handled' WHERE id=?", (reply_id,))
        self.commit()
        return True

    # -- DASHBOARD SUMMARY --
    def get_dashboard_summary(self):
        summary = {"sequences": {}, "global": {}}

        for seq_id in ["school", "csr", "csr-wsl-5", "leads"]:
            seq = {}
            seq["recipients"] = self.recipient_count(seq_id)
            seq["pool_count"] = self.get_pool_count(seq_id)

            tmpl_rows = self.execute("SELECT day, source, locked FROM templates WHERE sequence_id=?", (seq_id,)).fetchall()
            seq["templates"] = {r[0]: {"source": r[1], "locked": bool(r[2])} for r in tmpl_rows}
            seq["templates_total"] = len(tmpl_rows)
            seq["templates_locked"] = sum(1 for t in tmpl_rows if t[2])

            pipeline = self.get_pipeline(seq_id)
            if pipeline:
                p = pipeline[0]
                seq["pipeline"] = {
                    "total": p["total_recipients"],
                    "drafted": p["drafted"],
                    "sent": p["sent"],
                    "bounced": p["bounced"],
                    "replied": p["replied"]
                }
            else:
                seq["pipeline"] = {"total": 0, "drafted": 0, "sent": 0, "bounced": 0, "replied": 0}

            seq["day_wise"] = self.get_day_wise_pipeline(seq_id)
            seq["batches"] = self.batch_get_all(seq_id)

            summary["sequences"][seq_id] = seq

        summary["global"] = {
            "total_recipients": self.recipient_count(),
            "blacklist_count": self.execute("SELECT COUNT(*) FROM blacklist").fetchone()[0],
            "pending_replies": self.execute("SELECT COUNT(*) FROM replies WHERE status='pending'").fetchone()[0],
            "drafted_replies": self.execute("SELECT COUNT(*) FROM replies WHERE status='drafted'").fetchone()[0],
            "active_batches": self.execute("SELECT COUNT(*) FROM batches WHERE status IN ('scheduled','running')").fetchone()[0]
        }

        return summary

    def get_ab_test_results(self, sequence_id, day):
        """Return A/B test open rates for a template."""
        rows = self.execute("""
            SELECT s.ab_variant, COUNT(*) as sent, COUNT(s.opened_at) as opened
            FROM sends s
            JOIN recipients r ON s.recipient_id = r.id
            WHERE r.sequence_id = ? AND s.day = ? AND s.ab_variant IS NOT NULL AND s.status = 'sent'
            GROUP BY s.ab_variant
        """, (sequence_id, day)).fetchall()
        results = {}
        for variant, sent, opened in rows:
            sent = sent or 0
            opened = opened or 0
            results[variant] = {
                "sent": sent,
                "opened": opened,
                "open_rate": round(opened / sent * 100, 1) if sent else 0
            }
        return results

    def get_recent_activity(self, batch_id=None, limit=10):
        """Get recent activity log entries."""
        try:
            # Ensure table exists
            self.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id INTEGER,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            if batch_id:
                rows = self.execute(
                    "SELECT * FROM activity_log WHERE batch_id = ? ORDER BY created_at DESC LIMIT ?",
                    (batch_id, limit)
                ).fetchall()
            else:
                rows = self.execute(
                    "SELECT * FROM activity_log ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"Activity log error: {e}")
            return []

