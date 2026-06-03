import sqlite3, csv, json
from pathlib import Path

DB = Path(__file__).parent / "campaign_data.db"
EXPORT_DIR = Path(__file__).parent / "export"
EXPORT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row

tables = ["recipients", "batches", "batch_recipients", "templates", "blacklist", "sends", "replies"]
for table in tables:
    try:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        if rows:
            with open(EXPORT_DIR / f"{table}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(rows[0].keys())
                writer.writerows([list(r) for r in rows])
            print(f"✅ Exported {table}: {len(rows)} rows")
        else:
            print(f"⚠️ {table}: empty")
    except Exception as e:
        print(f"❌ {table}: {e}")

print(f"\nDone! CSV files saved in: {EXPORT_DIR}")
input("Press Enter to exit...")
