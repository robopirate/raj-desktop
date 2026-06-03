"""
Fix batch_recipients after SQLite → PostgreSQL migration.
Fast batch insert version with progress printing.
"""
import sqlite3
import psycopg2
import os
import sys

DB_URL = os.environ.get('DATABASE_URL')
if not DB_URL:
    print("ERROR: Set DATABASE_URL environment variable")
    sys.exit(1)

SQLITE_PATH = 'campaign_data.db'
if not os.path.exists(SQLITE_PATH):
    paths = ['campaign_data.db', './campaign_data.db', '../campaign_data.db']
    for p in paths:
        if os.path.exists(p):
            SQLITE_PATH = p
            break
    else:
        print("ERROR: campaign_data.db not found")
        sys.exit(1)

print(f"SQLite: {SQLITE_PATH}")
print(f"PostgreSQL: {DB_URL[:50]}...")
print("=" * 60)

# Step 1: Read SQLite data
sqlite_conn = sqlite3.connect(SQLITE_PATH)
sqlite_cur = sqlite_conn.cursor()

sqlite_cur.execute("SELECT id, name FROM batches")
sqlite_batches = {row[0]: row[1] for row in sqlite_cur.fetchall()}
print(f"[1/5] SQLite batches: {len(sqlite_batches)}")

sqlite_cur.execute("SELECT id, email FROM recipients")
sqlite_recipients = {row[0]: row[1] for row in sqlite_cur.fetchall()}
print(f"[2/5] SQLite recipients: {len(sqlite_recipients)}")

sqlite_cur.execute("SELECT batch_id, recipient_id FROM batch_recipients")
sqlite_br = sqlite_cur.fetchall()
print(f"[3/5] SQLite batch_recipients: {len(sqlite_br)}")

# Step 2: Read PostgreSQL data
pg_conn = psycopg2.connect(DB_URL)
pg_cur = pg_conn.cursor()

pg_cur.execute("SELECT id, name FROM batches")
pg_batches = {row[1]: row[0] for row in pg_cur.fetchall()}
print(f"[4/5] PostgreSQL batches: {len(pg_batches)}")

pg_cur.execute("SELECT id, email FROM recipients")
pg_recipients = {row[1]: row[0] for row in pg_cur.fetchall()}
print(f"[5/5] PostgreSQL recipients: {len(pg_recipients)}")

# Step 3: Build maps
batch_translation = {}
for old_id, name in sqlite_batches.items():
    if name in pg_batches:
        batch_translation[old_id] = pg_batches[name]

recipient_translation = {}
for old_id, email in sqlite_recipients.items():
    if email in pg_recipients:
        recipient_translation[old_id] = pg_recipients[email]

print(f"\nBatch translations: {len(batch_translation)}")
print(f"Recipient translations: {len(recipient_translation)}")

# Step 4: Delete old rows
print(f"\n[DELETE] Clearing old batch_recipients...")
pg_cur.execute("DELETE FROM batch_recipients")
pg_conn.commit()
print("  ✅ Deleted")

# Step 5: Build insert list (batch insert for speed)
print(f"[INSERT] Building insert list...")
inserts = []
for old_batch_id, old_recipient_id in sqlite_br:
    new_batch_id = batch_translation.get(old_batch_id)
    new_recipient_id = recipient_translation.get(old_recipient_id)
    if new_batch_id and new_recipient_id:
        inserts.append((new_batch_id, new_recipient_id))

print(f"  → {len(inserts)} rows to insert")

# Batch insert in chunks of 100
chunk_size = 100
inserted = 0
for i in range(0, len(inserts), chunk_size):
    chunk = inserts[i:i+chunk_size]
    try:
        pg_cur.executemany(
            "INSERT INTO batch_recipients (batch_id, recipient_id) VALUES (%s, %s)",
            chunk
        )
        pg_conn.commit()
        inserted += len(chunk)
        if inserted % 500 == 0:
            print(f"  → Inserted {inserted}/{len(inserts)}...")
    except Exception as e:
        print(f"  ⚠️ Chunk error: {e}")
        pg_conn.rollback()

print(f"  ✅ Total inserted: {inserted}")

# Step 6: Fix sends table
print(f"\n[FIX] sends table batch_id...")
pg_cur.execute("SELECT id, batch_id FROM sends WHERE batch_id IS NOT NULL")
sends_rows = pg_cur.fetchall()
sends_fixed = 0
for send_id, old_batch_id in sends_rows:
    new_batch_id = batch_translation.get(old_batch_id)
    if new_batch_id:
        pg_cur.execute(
            "UPDATE sends SET batch_id = %s WHERE id = %s",
            (new_batch_id, send_id)
        )
        sends_fixed += 1
pg_conn.commit()
print(f"  ✅ sends Fixed: {sends_fixed}")

# Verify
print(f"\n[VERIFY] Batch recipient counts:")
pg_cur.execute("""
    SELECT b.name, COUNT(br.batch_id) as cnt
    FROM batches b
    LEFT JOIN batch_recipients br ON b.id = br.batch_id
    GROUP BY b.id, b.name
    ORDER BY cnt DESC
    LIMIT 15
""")
for row in pg_cur.fetchall():
    print(f"  {row[0]}: {row[1]} recipients")

pg_cur.close()
pg_conn.close()
sqlite_conn.close()

print("\n" + "=" * 60)
print("✅ BATCH ID FIX COMPLETE")
print("Refresh: https://raj-web-app.onrender.com")
