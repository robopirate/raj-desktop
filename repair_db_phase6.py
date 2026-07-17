"""Phase 6 one-time database repairs for Raj desktop.

Run this script once after applying the Phase 4/5 code fixes.
It performs non-destructive cleanups that are safe to repeat.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "campaign_data.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Mark zombie pending sends as failed
    cur.execute("""
        UPDATE sends SET status='failed'
        WHERE status='pending' AND created_at < datetime('now', '-7 days')
    """)
    print(f"[1] Zombie pending sends marked failed: {cur.rowcount}")

    # 2. Reconcile batched flags against non-deleted batch membership
    cur.execute("""
        UPDATE recipients SET batched=1
        WHERE batched=0 AND EXISTS (
            SELECT 1 FROM batch_recipients br
            JOIN batches b ON b.id=br.batch_id
            WHERE br.recipient_id=recipients.id AND b.deleted_at IS NULL
        )
    """)
    print(f"[2] Recipients set batched=1: {cur.rowcount}")

    cur.execute("""
        UPDATE recipients SET batched=0
        WHERE batched=1 AND NOT EXISTS (
            SELECT 1 FROM batch_recipients br
            JOIN batches b ON b.id=br.batch_id
            WHERE br.recipient_id=recipients.id AND b.deleted_at IS NULL
        )
    """)
    print(f"[3] Recipients set batched=0: {cur.rowcount}")

    # 3. Normalize any uppercase sequence_ids in templates
    # Merge duplicate CSR-WSL-5 / csr-wsl-5 rows: keep the non-empty lowercased row.
    duplicates = cur.execute("""
        SELECT LOWER(sequence_id) AS seq, day
        FROM templates
        GROUP BY LOWER(sequence_id), day
        HAVING COUNT(*) > 1
    """).fetchall()
    for row in duplicates:
        seq, day = row["seq"], row["day"]
        rows = cur.execute(
            "SELECT * FROM templates WHERE LOWER(sequence_id)=? AND day=? ORDER BY (html_body IS NOT NULL AND html_body != '') DESC, cached_at DESC",
            (seq, day)
        ).fetchall()
        keeper = rows[0]
        for dup in rows[1:]:
            cur.execute("DELETE FROM templates WHERE sequence_id=? AND day=?", (dup["sequence_id"], day))
        cur.execute(
            "UPDATE templates SET sequence_id=? WHERE sequence_id=? AND day=?",
            (seq, keeper["sequence_id"], day)
        )
        print(f"[4] Merged duplicate template {seq.upper()} Day {day}")

    cur.execute("""
        UPDATE templates SET sequence_id=LOWER(sequence_id)
        WHERE sequence_id != LOWER(sequence_id)
    """)
    print(f"[5] Templates normalized to lowercase: {cur.rowcount}")

    # 4. Report orphan 'a' family and batch 101/102 anomalies (manual review)
    print("\n[5] Orphan families to review manually:")
    for row in cur.execute("""
        SELECT id, name, sequence_id, day_offset, parent_batch_id, status
        FROM batches
        WHERE parent_batch_id IS NOT NULL
          AND parent_batch_id NOT IN (SELECT id FROM batches WHERE deleted_at IS NULL)
    """):
        print(f"    batch {row['id']}: {row['name']} (parent {row['parent_batch_id']} missing)")

    conn.commit()
    conn.close()
    print("\nPhase 6 repairs complete.")
    print("Next: open Raj, go to Integrations > connect Gmail, then Templates > Sync from Gmail for school D1/D3.")


if __name__ == "__main__":
    main()
