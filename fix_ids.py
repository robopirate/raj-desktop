"""
fix_ids.py -- Fix broken foreign key links after SQLite->PostgreSQL migration
Matches old SQLite recipient IDs with new PostgreSQL IDs by email address
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# Paths
SQLITE_PATH = "campaign_data.db"
DATABASE_URL = os.environ.get('DATABASE_URL', 
    'postgresql://raj_db_user:zA7jx4vquYM7Uwkr62RkydIZAhId6Jp3@dpg-d8ersh3bc2fs73cru1n0-a.singapore-postgres.render.com/raj_db')

def fix_ids():
    print("="*60)
    print("FIXING BROKEN FOREIGN KEY LINKS")
    print("="*60)

    # Connect to SQLite (desktop)
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_cur = sqlite_conn.cursor()

    # Connect to PostgreSQL (cloud)
    pg_conn = psycopg2.connect(DATABASE_URL)
    pg_cur = pg_conn.cursor()

    # Step 1: Build email -> old_id map from SQLite
    print("\n[1/4] Reading SQLite recipients...")
    sqlite_cur.execute("SELECT id, email FROM recipients")
    old_map = {}  # email -> old_id
    for row in sqlite_cur.fetchall():
        old_id, email = row
        old_map[email.lower().strip()] = old_id
    print(f"   Found {len(old_map)} recipients in SQLite")

    # Step 2: Build email -> new_id map from PostgreSQL
    print("\n[2/4] Reading PostgreSQL recipients...")
    pg_cur.execute("SELECT id, email FROM recipients")
    new_map = {}  # email -> new_id
    for row in pg_cur.fetchall():
        new_id, email = row
        new_map[email.lower().strip()] = new_id
    print(f"   Found {len(new_map)} recipients in PostgreSQL")

    # Step 3: Create old_id -> new_id translation table
    print("\n[3/4] Building ID translation map...")
    translation = {}  # old_id -> new_id
    matched = 0
    unmatched = 0
    for email, old_id in old_map.items():
        if email in new_map:
            translation[old_id] = new_map[email]
            matched += 1
        else:
            unmatched += 1
    print(f"   Matched: {matched}, Unmatched: {unmatched}")

    if matched == 0:
        print("\n❌ ERROR: No emails matched! Cannot fix IDs.")
        return

    # Step 4: Fix sends table
    print("\n[4/4] Fixing sends table...")
    pg_cur.execute("SELECT id, recipient_id FROM sends")
    sends = pg_cur.fetchall()
    fixed = 0
    skipped = 0
    for send_id, old_recipient_id in sends:
        if old_recipient_id in translation:
            pg_cur.execute("UPDATE sends SET recipient_id = %s WHERE id = %s", 
                          (translation[old_recipient_id], send_id))
            fixed += 1
        else:
            skipped += 1
    pg_conn.commit()
    print(f"   Fixed: {fixed}, Skipped: {skipped}")

    # Step 5: Fix batch_recipients table
    print("\n[5/4] Fixing batch_recipients table...")
    pg_cur.execute("SELECT batch_id, recipient_id FROM batch_recipients")
    batch_recs = pg_cur.fetchall()
    fixed_br = 0
    skipped_br = 0
    for batch_id, old_recipient_id in batch_recs:
        if old_recipient_id in translation:
            pg_cur.execute("UPDATE batch_recipients SET recipient_id = %s WHERE batch_id = %s AND recipient_id = %s", 
                          (translation[old_recipient_id], batch_id, old_recipient_id))
            fixed_br += 1
        else:
            skipped_br += 1
    pg_conn.commit()
    print(f"   Fixed: {fixed_br}, Skipped: {skipped_br}")

    # Cleanup
    sqlite_conn.close()
    pg_conn.close()

    print("\n" + "="*60)
    print("✅ ID FIX COMPLETE")
    print("="*60)
    print("\nRefresh your dashboard: https://raj-web-app.onrender.com")
    print("Batches should now show real recipient counts.")

if __name__ == '__main__':
    if not os.path.exists(SQLITE_PATH):
        print(f"❌ ERROR: {SQLITE_PATH} not found in this folder!")
        print("   Make sure you're running this from your desktop app folder.")
        exit(1)

    fix_ids()
