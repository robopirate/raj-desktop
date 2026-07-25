"""
backup_db.py — Nightly database backup.

Copies the live campaign DB (local app-data dir, outside OneDrive) into
the project folder's backups/ directory — which IS OneDrive-synced, so
every backup is also an offsite copy. Keeps the last 14 days.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

from db import DB_PATH

BACKUP_DIR = Path(__file__).parent / "backups"
KEEP_DAYS = 14


def backup_now(db_path=None) -> Path:
    """Create a consistent backup using SQLite's online backup API."""
    src_path = str(db_path or DB_PATH)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    dest = BACKUP_DIR / f"campaign_data-{stamp}.db"

    src = sqlite3.connect(f"file:{src_path}?mode=ro", uri=True)
    dst = sqlite3.connect(str(dest))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()

    # Prune old backups
    cutoff = datetime.now() - timedelta(days=KEEP_DAYS)
    for old in BACKUP_DIR.glob("campaign_data-*.db"):
        try:
            stamp_part = old.stem.replace("campaign_data-", "")[:8]
            if datetime.strptime(stamp_part, "%Y%m%d") < cutoff:
                old.unlink()
        except Exception:
            pass
    return dest


if __name__ == "__main__":
    out = backup_now()
    size_kb = out.stat().st_size // 1024
    print(f"Backup written: {out} ({size_kb} KB)")
