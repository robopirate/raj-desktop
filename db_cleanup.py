"""
db_cleanup.py — One-time fix for incorrect batch statuses
Run this once to clean up your database.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "campaign_data.db"

def cleanup_batch_statuses():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    print("=" * 50)
    print("  DATABASE CLEANUP")
    print("=" * 50)

    # Find all batches marked "completed" but not all emails sent
    rows = conn.execute("""
        SELECT b.id, b.name, b.status, b.sequence_id, b.day_offset,
               COUNT(br.recipient_id) as total,
               SUM(CASE WHEN br.status = 'sent' THEN 1 ELSE 0 END) as sent
        FROM batches b
        LEFT JOIN batch_recipients br ON b.id = br.batch_id
        WHERE b.status = 'completed'
        GROUP BY b.id
    """).fetchall()

    fixed = 0
    for row in rows:
        batch_id = row['id']
        name = row['name']
        total = row['total'] or 0
        sent = row['sent'] or 0

        if sent < total:
            print(f"  FIXING: {name} (ID:{batch_id}) — status=completed but {sent}/{total} sent")
            conn.execute("UPDATE batches SET status='draft' WHERE id=?", (batch_id,))
            fixed += 1
        else:
            print(f"  OK: {name} — {sent}/{total} sent ✓")

    conn.commit()
    conn.close()

    print(f"\n  Fixed {fixed} batches")
    print("  Restart Raj to see clean statuses")
    print("=" * 50)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    cleanup_batch_statuses()
