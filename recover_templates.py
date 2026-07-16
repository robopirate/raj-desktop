#!/usr/bin/env python3
"""
recover_templates.py — one-shot recovery helper for Raj Desktop

1. Authenticates Gmail (opens browser if needed).
2. Lists existing Gmail drafts and subjects.
3. Runs engine.sync_templates() to pull real drafts into the DB.
4. Imports the local csr-wsl-5 templates from CSR_5YEAR_PCM_TEMPLATES.py
   (only overwrites placeholder/generated rows, never locked real drafts).
5. Locks every real template so it won't be overwritten by AI generation.

Run from the project root:
    .venv\\Scripts\\python recover_templates.py
"""

import os
import re
import sys

# Ensure project root is on path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from db import Database
from gmail import GmailClient
from engine import CampaignEngine


def summarize_drafts(engine: CampaignEngine):
    print("\n=== Gmail drafts ===")
    try:
        drafts = engine.gmail.list_drafts()
        print(f"Found {len(drafts)} draft(s)")
        for d in drafts:
            try:
                full = engine.gmail.get_draft_full(d["id"])
                subj = (full.get("subject", "") or "")[:80]
                print(f"  - {subj!r} (id={d['id']})")
            except Exception as e:
                print(f"  - (could not read draft {d['id']}: {e})")
    except Exception as e:
        print(f"Could not list drafts: {e}")


def import_csr_5year_local(engine: CampaignEngine):
    """Import csr-wsl-5 templates from CSR_5YEAR_PCM_TEMPLATES.py."""
    try:
        import CSR_5YEAR_PCM_TEMPLATES as local
    except Exception as e:
        print(f"Could not import CSR_5YEAR_PCM_TEMPLATES.py: {e}")
        return

    seq_id = "csr-wsl-5"
    day_map = {
        1: (local.CSR_5YEAR_D1_SUBJECT, local.CSR_5YEAR_D1_HTML),
        3: (local.CSR_5YEAR_D3_SUBJECT, local.CSR_5YEAR_D3_HTML),
        5: (local.CSR_5YEAR_D5_SUBJECT, local.CSR_5YEAR_D5_HTML),
        7: (local.CSR_5YEAR_D7_SUBJECT, local.CSR_5YEAR_D7_HTML),
        10: (local.CSR_5YEAR_D10_SUBJECT, local.CSR_5YEAR_D10_HTML),
    }

    imported = 0
    skipped = 0
    for day, (subject, html) in day_map.items():
        existing = engine.db.template_get(seq_id, day)
        # Never overwrite a locked, non-empty real template.
        if existing and existing.get("locked") and existing.get("html_body") and len(existing["html_body"]) > 50:
            skipped += 1
            print(f"  csr-wsl-5 day {day}: locked real draft kept")
            continue
        engine.db.template_put(
            sequence_id=seq_id,
            day=day,
            subject=subject,
            html_body=html,
            text_body=None,
            source="local",
            format="html"
        )
        imported += 1
        print(f"  csr-wsl-5 day {day}: imported from local file")
    print(f"Imported {imported} csr-wsl-5 day(s), skipped {skipped}")


def lock_real_templates(engine: CampaignEngine):
    """Lock any template that came from a real source and has real content."""
    real_sources = {"synced", "manual", "local"}
    rows = engine.db.execute(
        "SELECT sequence_id, day, source, html_body, locked FROM templates"
    ).fetchall()
    locked = 0
    for seq_id, day, source, html_body, is_locked in rows:
        if is_locked:
            continue
        body = html_body or ""
        if source in real_sources and len(body) > 50:
            engine.db.template_lock(seq_id, day)
            locked += 1
            print(f"  locked {seq_id} day {day} (source={source})")
    print(f"Locked {locked} real template(s)")


def print_summary(engine: CampaignEngine):
    print("\n=== Template summary ===")
    rows = engine.db.execute(
        "SELECT sequence_id, day, source, locked, length(html_body) as body_len FROM templates ORDER BY sequence_id, day"
    ).fetchall()
    for seq_id, day, source, is_locked, body_len in rows:
        print(f"  {seq_id:12s} day {day:2d}  source={source:8s}  locked={bool(is_locked)}  len={body_len or 0}")


def main():
    print("Raj template recovery")
    print("=" * 50)

    db = Database()
    gmail = GmailClient()
    engine = CampaignEngine(db, gmail)

    print("\nGmail auth: opening browser if needed...")
    try:
        engine.gmail.authenticate()
        print("Gmail authenticated.")
    except Exception as e:
        print(f"Gmail auth failed: {e}")
        return

    summarize_drafts(engine)

    print("\n=== Syncing templates from Gmail drafts ===")
    try:
        engine.sync_templates()
        print("Sync complete.")
    except Exception as e:
        print(f"Sync failed: {e}")

    print("\n=== Importing local csr-wsl-5 templates ===")
    import_csr_5year_local(engine)

    print("\n=== Locking real templates ===")
    lock_real_templates(engine)

    print_summary(engine)
    print("\nRecovery finished. Restart Raj Desktop to pick up changes.")


if __name__ == "__main__":
    main()
