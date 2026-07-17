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

    # Prepare export directories
    export_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export", "emails")
    for seq_id in seq_ids:
        os.makedirs(os.path.join(export_root, seq_id), exist_ok=True)

    # Descriptive file names per sequence/day
    file_names = {
        "school": {
            1: "01_Introduction",
            3: "02_NEP_Positioning",
            5: "03_VeerBaji_CaseStudy",
            7: "04_85Plus_Principals",
            10: "05_FinalCall",
        },
        "csr-wsl-5": {
            1: "01_5Year_Model",
            3: "02_Full_Academic_Year",
            5: "03_Trainer_Story",
            7: "04_Math_Breakdown",
            10: "05_Final_Call",
        },
    }

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

            # Export HTML and plain text files
            export_dir = os.path.join(export_root, seq_id)
            filename_base = file_names.get(seq_id, {}).get(day, f"D{day}")
            html_path = os.path.join(export_dir, f"{filename_base}.html")
            txt_path = os.path.join(export_dir, f"{filename_base}.txt")

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(template["html_body"])

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Subject: {template['subject']}\n\n")
                f.write(template.get("text_body", ""))

            print(f"  EXPORTED: {seq_id} {filename_base}.html + .txt")

    print(f"\nDone. Regenerated {total} templates. Skipped {skipped_locked} locked templates.")
    print(f"Exported files are in: {export_root}")


if __name__ == "__main__":
    main()
