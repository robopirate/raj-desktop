"""
regenerate_templates.py
Force-regenerate SCHOOL and CSR-WSL-5 templates after a copy rewrite.
Skips locked templates as a safety guard.
"""
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import CampaignEngine, SEQUENCES
from db import Database
from gmail import GmailClient


def main():
    db = Database()
    gmail = GmailClient()
    engine = CampaignEngine(db, gmail)
    seq_ids = ["school", "csr-wsl-5"]
    total = 0
    skipped_locked = 0

    for seq_id in seq_ids:
        for day in SEQUENCES.get(seq_id, {}).get("days", []):
            if engine.is_template_locked(seq_id, day):
                print(f"SKIP (locked): {seq_id} day {day}")
                skipped_locked += 1
                continue

            template = engine.generate_template(seq_id, day)
            if "error" in template:
                print(f"ERROR: {seq_id} day {day}: {template['error']}")
                continue

            engine.db.template_put(
                seq_id,
                day,
                template["subject"],
                template["html_body"],
                "generated",
                text_body=template.get("text_body"),
                format=template.get("format", "html"),
            )
            print(f"REGENERATED: {seq_id} day {day}")
            total += 1

    print(f"\nDone. Regenerated {total} templates. Skipped {skipped_locked} locked templates.")


if __name__ == "__main__":
    main()
