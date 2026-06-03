"""
db_check.py -- Check database contents after sync
"""

import os
import psycopg2

DATABASE_URL = "postgresql://raj_db_user:zA7jx4vquYM7Uwkr62RkydIZAhId6Jp3@dpg-d8ersh3bc2fs73cru1n0-a.singapore-postgres.render.com/raj_db"

def check_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print("="*60)
    print("DATABASE DIAGNOSTIC")
    print("="*60)

    # Check recipients
    cur.execute("SELECT COUNT(*) FROM recipients")
    print(f"Recipients total: {cur.fetchone()[0]}")

    cur.execute("SELECT sequence_id, COUNT(*) FROM recipients GROUP BY sequence_id")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check sends
    cur.execute("SELECT COUNT(*) FROM sends")
    print(f"\nSends total: {cur.fetchone()[0]}")

    cur.execute("SELECT status, COUNT(*) FROM sends GROUP BY status")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check if sends have recipient_ids that exist in recipients
    cur.execute("""
        SELECT COUNT(*) FROM sends s
        WHERE s.recipient_id IN (SELECT id FROM recipients)
    """)
    print(f"  Sends with valid recipient_id: {cur.fetchone()[0]}")

    cur.execute("""
        SELECT COUNT(*) FROM sends s
        WHERE s.recipient_id NOT IN (SELECT id FROM recipients)
    """)
    print(f"  Sends with INVALID recipient_id: {cur.fetchone()[0]}")

    # Check batch_recipients
    cur.execute("SELECT COUNT(*) FROM batch_recipients")
    print(f"\nBatch_recipients total: {cur.fetchone()[0]}")

    cur.execute("SELECT status, COUNT(*) FROM batch_recipients GROUP BY status")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check batches
    cur.execute("SELECT COUNT(*) FROM batches")
    print(f"\nBatches total: {cur.fetchone()[0]}")

    cur.execute("SELECT status, COUNT(*) FROM batches GROUP BY status")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check blacklist
    cur.execute("SELECT COUNT(*) FROM blacklist")
    print(f"\nBlacklist total: {cur.fetchone()[0]}")

    # Check templates
    cur.execute("SELECT COUNT(*) FROM templates")
    print(f"\nTemplates total: {cur.fetchone()[0]}")

    cur.execute("SELECT sequence_id, COUNT(*) FROM templates GROUP BY sequence_id")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Check replies
    cur.execute("SELECT COUNT(*) FROM replies")
    print(f"\nReplies total: {cur.fetchone()[0]}")

    conn.close()
    print("\n" + "="*60)

if __name__ == '__main__':
    check_db()
