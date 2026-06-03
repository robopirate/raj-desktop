"""
blacklist_cleanup.py — Safe Blacklist Cleanup Script
Removes ONLY wrongly blacklisted emails from last 30 days.
Keeps your original dead_emails_blacklist.txt entries safe.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "campaign_data.db"
BLACKLIST_FILE = Path(__file__).parent / "dead_emails_blacklist.txt"

def safe_cleanup():
    """
    Safe cleanup rules:
    1. Load original dead_emails_blacklist.txt (these are REAL dead emails — NEVER remove)
    2. Find entries added to DB in last 30 days
    3. Only remove those that are NOT in dead_emails_blacklist.txt
    4. Keep everything else
    """

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Step 1: Load original dead emails (THESE STAY)
    original_dead = set()
    if BLACKLIST_FILE.exists():
        with open(BLACKLIST_FILE, 'r') as f:
            for line in f:
                email = line.strip().lower()
                if email and "@" in email:
                    original_dead.add(email)
        print(f"✅ Loaded {len(original_dead)} original dead emails (PROTECTED)")
    else:
        print("⚠️ dead_emails_blacklist.txt not found — no protection possible")
        return

    # Step 2: Find entries added in last 30 days
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

    recent_entries = conn.execute(
        "SELECT id, email, reason, added_at FROM blacklist WHERE added_at > ?",
        (thirty_days_ago,)
    ).fetchall()

    print(f"\n📊 Found {len(recent_entries)} entries added in last 30 days")

    # Step 3: Categorize
    to_remove = []  # Wrongly blacklisted (not in original_dead)
    to_keep = []    # Protected (in original_dead or added earlier)

    for entry in recent_entries:
        email = entry["email"].lower().strip()
        if email in original_dead:
            to_keep.append(entry)
        else:
            to_remove.append(entry)

    print(f"\n🗑️  To REMOVE (wrongly blacklisted): {len(to_remove)}")
    print(f"🔒 To KEEP (protected): {len(to_keep)}")

    # Step 4: Show what will be removed
    if to_remove:
        print("\n⚠️  These will be REMOVED from blacklist:")
        for i, entry in enumerate(to_remove[:20], 1):
            print(f"   {i}. {entry['email']} (reason: {entry['reason'][:40]})")
        if len(to_remove) > 20:
            print(f"   ... and {len(to_remove) - 20} more")

    # Step 5: Confirm with user
    if not to_remove:
        print("\n✅ Nothing to clean! All recent entries are protected.")
        conn.close()
        return

    print("\n" + "="*60)
    print("SAFE CLEANUP SUMMARY")
    print("="*60)
    print(f"Original dead emails (protected): {len(original_dead)}")
    print(f"Recent entries found: {len(recent_entries)}")
    print(f"Will REMOVE: {len(to_remove)} (wrongly blacklisted)")
    print(f"Will KEEP: {len(to_keep)} (protected originals)")
    print("\nThis is SAFE — your original dead_emails_blacklist.txt entries are protected.")

    # Step 6: Execute removal
    removed_count = 0
    for entry in to_remove:
        conn.execute("DELETE FROM blacklist WHERE id=?", (entry["id"],))
        removed_count += 1

    conn.commit()
    conn.close()

    print(f"\n✅ Cleanup complete! Removed {removed_count} wrongly blacklisted emails.")
    print(f"🔒 {len(to_keep)} original dead emails remain protected.")
    print("\nYou can now restart Raj with the fixed engine.py!")

if __name__ == "__main__":
    print("="*60)
    print("  SAFE BLACKLIST CLEANUP")
    print("  Only removes wrongly blacklisted emails from last 30 days")
    print("  Your dead_emails_blacklist.txt entries are PROTECTED")
    print("="*60)
    print()
    safe_cleanup()
    input("\nPress Enter to exit...")
