"""
Fix batches with 0 recipients by checking which ones are missing links.
Run this on desktop to see which batches need fixing.
"""
import psycopg2
import os

DB_URL = os.environ.get('DATABASE_URL')
if not DB_URL:
    print("ERROR: Set DATABASE_URL")
    exit(1)

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Get all batches with their recipient counts
cur.execute("""
    SELECT b.id, b.name, b.status, COUNT(br.recipient_id) as cnt
    FROM batches b
    LEFT JOIN batch_recipients br ON b.id = br.batch_id
    GROUP BY b.id
    ORDER BY cnt DESC
""")

print("BATCHES WITH RECIPIENTS:")
print("-" * 60)
for row in cur.fetchall():
    batch_id, name, status, cnt = row
    if cnt > 0:
        print(f"  ✅ {name}: {cnt} recipients")
    else:
        print(f"  ❌ {name}: {cnt} recipients (MISSING)")

# Check if these batches exist in the old SQLite but not linked
cur.execute("""
    SELECT b.id, b.name 
    FROM batches b
    WHERE b.id NOT IN (SELECT DISTINCT batch_id FROM batch_recipients)
""")

print("\nBATCHES WITH NO LINKS AT ALL:")
print("-" * 60)
for row in cur.fetchall():
    print(f"  ❌ {row[1]} (ID: {row[0]})")

cur.close()
conn.close()
