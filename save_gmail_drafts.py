"""
save_gmail_drafts.py
Save the rewritten SCHOOL and CSR-WSL-5 templates as Gmail drafts so they can be
reviewed, shared, and shown before any campaign sends.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import CampaignEngine, SEQUENCES
from db import Database
from gmail import GmailClient


def main():
    db = Database()
    gmail = GmailClient()
    engine = CampaignEngine(db, gmail)

    if not gmail.is_connected():
        print("Token not valid for silent auth. Trying interactive OAuth...")
        try:
            gmail.authenticate()
        except Exception as e:
            print(f"Gmail OAuth failed: {e}")
            print("Please run desktop.py, connect Gmail, then re-run this script.")
            return

    if not gmail.is_connected():
        print("Gmail still not connected after OAuth attempt. Aborting.")
        return

    seq_ids = ["school", "csr-wsl-5"]
    total = 0

    for seq_id in seq_ids:
        for day in SEQUENCES[seq_id]["days"]:
            ok = engine.save_generated_template(seq_id, day, create_draft=True)
            if ok:
                print(f"Saved Gmail draft: {seq_id} day {day}")
                total += 1
            else:
                print(f"Failed to save draft: {seq_id} day {day}")

    print(f"\nDone. Saved {total} Gmail drafts.")


if __name__ == "__main__":
    main()
