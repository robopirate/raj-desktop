"""
migrate_unified_pool.py — one-time migration to a single generic pool.

- Merges duplicate recipient rows by email.
- Sets sequence_id='leads' for all recipients.
- Backfills sub_pool from old sequence_id where sub_pool was empty.
- Drops UNIQUE(sequence_id, email) and adds UNIQUE(email).

Run with: python migrate_unified_pool.py [path/to/campaign_data.db]
If no path is given, uses the live DB resolved by db.py.
"""

import sqlite3
import sys
from pathlib import Path


def migrate(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print(f"[MIGRATE] Opening {db_path}")

    # 1. Merge duplicate recipients by email
    dups = cursor.execute("""
        SELECT email, COUNT(*) as cnt, GROUP_CONCAT(id) as ids,
               GROUP_CONCAT(DISTINCT sequence_id) as seqs
        FROM recipients
        GROUP BY email
        HAVING cnt > 1
    """).fetchall()
    print(f"[MIGRATE] Found {len(dups)} duplicate emails")

    for row in dups:
        email = row["email"]
        ids = [int(x) for x in row["ids"].split(",")]
        print(f"[MIGRATE]  Merging {email} ids={ids}")

        # Pick canonical: the one with the most sends, else lowest id
        counts = cursor.execute("""
            SELECT recipient_id, COUNT(*) as cnt FROM sends
            WHERE recipient_id IN ({}) GROUP BY recipient_id
        """.format(",".join("?" * len(ids))), ids).fetchall()
        count_map = {r["recipient_id"]: r["cnt"] for r in counts}
        canonical = max(ids, key=lambda i: (count_map.get(i, 0), -i))
        duplicates = [i for i in ids if i != canonical]
        print(f"[MIGRATE]   canonical={canonical}, duplicates={duplicates}")

        for dup in duplicates:
            # Update sends
            cursor.execute("UPDATE sends SET recipient_id=? WHERE recipient_id=?", (canonical, dup))
            # Update engagement_events
            cursor.execute("UPDATE engagement_events SET recipient_id=? WHERE recipient_id=?", (canonical, dup))
            # Update replies
            cursor.execute("UPDATE replies SET recipient_id=? WHERE recipient_id=?", (canonical, dup))
            # Update pending_resumes
            cursor.execute("UPDATE pending_resumes SET recipient_id=? WHERE recipient_id=?", (canonical, dup))
            # Merge batch_recipients: if (batch_id, canonical) exists, delete duplicate; else re-link
            br_rows = cursor.execute(
                "SELECT batch_id FROM batch_recipients WHERE recipient_id=?", (dup,)
            ).fetchall()
            for br in br_rows:
                batch_id = br["batch_id"]
                exists = cursor.execute(
                    "SELECT 1 FROM batch_recipients WHERE batch_id=? AND recipient_id=?",
                    (batch_id, canonical)
                ).fetchone()
                if exists:
                    cursor.execute(
                        "DELETE FROM batch_recipients WHERE batch_id=? AND recipient_id=?",
                        (batch_id, dup)
                    )
                else:
                    cursor.execute(
                        "UPDATE batch_recipients SET recipient_id=? WHERE batch_id=? AND recipient_id=?",
                        (canonical, batch_id, dup)
                    )
            # Delete duplicate recipient
            cursor.execute("DELETE FROM recipients WHERE id=?", (dup,))

    # 2. Backfill sub_pool from old sequence_id, then set all to 'leads'
    cursor.execute("""
        UPDATE recipients
        SET sub_pool = COALESCE(NULLIF(TRIM(sub_pool), ''), sequence_id)
        WHERE sequence_id != 'leads'
    """)
    backfilled = cursor.execute("SELECT changes()").fetchone()[0]
    print(f"[MIGRATE] Backfilled sub_pool for {backfilled} leads")

    cursor.execute("UPDATE recipients SET sequence_id='leads'")
    migrated = cursor.execute("SELECT changes()").fetchone()[0]
    print(f"[MIGRATE] Migrated {migrated} leads to sequence_id='leads'")

    # 3. Recreate recipients table with UNIQUE(email) instead of UNIQUE(sequence_id, email)
    conn.commit()
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("""
        CREATE TABLE recipients_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sequence_id TEXT,
            email TEXT NOT NULL UNIQUE,
            name TEXT,
            org TEXT,
            extra_json TEXT,
            sub_pool TEXT DEFAULT '',
            import_status TEXT DEFAULT 'pending',
            import_error TEXT,
            batched INTEGER DEFAULT 0,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print(f"[MIGRATE] batched=1 before recreate: {cursor.execute('SELECT COUNT(*) FROM recipients WHERE batched=1').fetchone()[0]}")
    cursor.execute("""
        INSERT INTO recipients_new
            (id, sequence_id, email, name, org, extra_json, sub_pool, import_status, import_error, batched, imported_at)
        SELECT id, sequence_id, email, name, org, extra_json, sub_pool, import_status, import_error, batched, imported_at
        FROM recipients
    """)
    cursor.execute("DROP TABLE recipients")
    cursor.execute("ALTER TABLE recipients_new RENAME TO recipients")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_recipients_sequence ON recipients(sequence_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_recipients_sub_pool ON recipients(sub_pool)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_recipients_batched ON recipients(batched)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_recipients_email ON recipients(email)")
    cursor.execute("PRAGMA foreign_keys = ON")
    print("[MIGRATE] Recreated recipients table with UNIQUE(email)")

    conn.commit()

    # 4. Verify
    total = cursor.execute("SELECT COUNT(*) FROM recipients").fetchone()[0]
    dup_check = cursor.execute("""
        SELECT email, COUNT(*) FROM recipients GROUP BY email HAVING COUNT(*) > 1
    """).fetchall()
    seqs = cursor.execute("SELECT DISTINCT sequence_id FROM recipients").fetchall()
    sub_pools = cursor.execute("SELECT sub_pool, COUNT(*) FROM recipients GROUP BY sub_pool").fetchall()
    batched_1 = cursor.execute("SELECT COUNT(*) FROM recipients WHERE batched=1").fetchone()[0]
    print(f"\n[MIGRATE] Total recipients: {total}")
    print(f"[MIGRATE] Remaining duplicates: {len(dup_check)}")
    print(f"[MIGRATE] sequence_ids: {[r[0] for r in seqs]}")
    print(f"[MIGRATE] batched=1: {batched_1}")
    print("[MIGRATE] sub_pools:")
    for r in sub_pools:
        print(f"   {r[0] or '(empty)'}: {r[1]}")

    conn.close()
    print("[MIGRATE] Done.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        from db import DB_PATH
        path = DB_PATH
    migrate(path)
