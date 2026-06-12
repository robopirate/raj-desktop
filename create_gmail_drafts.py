"""
create_gmail_drafts.py — Auto-create 5 CSR email drafts in Gmail for Raj sync
Run this to create the 5 CSR EMAIL drafts in your Gmail inbox. Then Raj can sync them.
"""

import sys
import os

# Add current directory to path so we can import gmail.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail import GmailClient
from pathlib import Path

# Read the 5 HTML draft files
DRAFT_FILES = [
    ("CSR EMAIL 1", "CSR_EMAIL_1_DRAFT.html"),
    ("CSR EMAIL 2", "CSR_EMAIL_2_DRAFT.html"),
    ("CSR EMAIL 3", "CSR_EMAIL_3_DRAFT.html"),
    ("CSR EMAIL 4", "CSR_EMAIL_4_DRAFT.html"),
    ("CSR EMAIL 5", "CSR_EMAIL_5_DRAFT.html"),
]

TO_EMAIL = "om@robopirate.in"  # Change if needed

def main():
    print("=" * 60)
    print("  Creating 5 CSR Email Drafts in Gmail")
    print("  Subjects: CSR EMAIL 1 → CSR EMAIL 5")
    print("=" * 60)
    print()

    # Check if HTML files exist
    missing = []
    for _, filename in DRAFT_FILES:
        if not Path(filename).exists():
            missing.append(filename)
    if missing:
        print(f"ERROR: Missing HTML files: {missing}")
        print("Make sure these files are in the same folder as this script.")
        return

    # Authenticate Gmail
    print("[1/2] Connecting to Gmail...")
    try:
        gmail = GmailClient()
        print("  ✓ Gmail connected")
    except FileNotFoundError:
        print("\nERROR: credentials.json not found!")
        print("   1. Go to https://console.cloud.google.com")
        print("   2. Create project -> Enable Gmail API")
        print("   3. Create OAuth 2.0 credentials (Desktop app)")
        print("   4. Download JSON and save as 'credentials.json' in this folder")
        return
    except Exception as e:
        print(f"\nERROR Gmail: {e}")
        return

    # Create drafts
    print(f"[2/2] Creating drafts to: {TO_EMAIL}")
    print()
    created = []
    failed = []

    for subject, filename in DRAFT_FILES:
        html_body = Path(filename).read_text(encoding="utf-8")
        try:
            draft = gmail.draft_email(TO_EMAIL, subject, html_body)
            draft_id = draft.get('id', 'unknown')
            print(f"  ✓ Created: {subject} (Draft ID: {draft_id})")
            created.append((subject, draft_id))
        except Exception as e:
            print(f"  ✗ FAILED: {subject} — {e}")
            failed.append((subject, str(e)))

    print()
    print("=" * 60)
    print(f"  DONE: {len(created)}/5 drafts created")
    print("=" * 60)

    if created:
        print("\nCreated successfully:")
        for subj, draft_id in created:
            print(f"  • {subj}")

    if failed:
        print("\nFailed:")
        for subj, err in failed:
            print(f"  • {subj} — {err}")

    print(f"\nNext steps:")
    print(f"  1. Open Gmail and check your Drafts folder")
    print(f"  2. In Raj, go to Templates tab → 'Sync from Gmail'")
    print(f"  3. Raj will auto-detect these 5 drafts and load them into the CSR sequence")
    print(f"  4. IMPORTANT: Do NOT send these drafts — they are templates for Raj to use")

    print(f"\nIf you see auth prompts, approve them. The token will be saved for future use.")

if __name__ == "__main__":
    main()
