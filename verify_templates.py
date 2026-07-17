"""
verify_templates.py
Check that the rewritten SCHOOL and CSR-WSL-5 templates meet the quality checklist.
"""
import os
import re
import sys
import sqlite3
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import SEQUENCES

EXPECTED_ASSETS = {
    "school": {
        1: {"brochure", "video_wsl", "video_abp", "video_ig"},
        3: {"video_abp", "video_ig"},
        5: {"report_vbv", "video_star", "folder_vbv", "video_ig"},
        7: {"profile", "video_abp", "video_star", "video_ig"},
        10: {"plans", "video_ig"},
    },
    "csr-wsl-5": {
        1: {"report_vbv", "brochure", "video_ig"},
        3: {"report_vbv", "video_abp", "video_star", "video_ig"},
        5: {"video_wsl", "video_ig"},
        7: {"brochure", "video_ig"},
        10: {"profile", "video_ig"},
    },
}

REQUIRED_PLACEHOLDERS = {
    "school": ["{{SCHOOL_NAME}}", "{{PRINCIPAL_NAME}}"],
    "csr-wsl-5": ["{{COMPANY_NAME}}", "{{CSR_HEAD_NAME}}"],
}

# Map each placeholder to the days it must appear in (subject+body).
# Based on original template usage: not every placeholder needs to be in every email.
PLACEHOLDER_REQUIRED_DAYS = {
    "school": {
        "{{SCHOOL_NAME}}": [1, 3, 5, 7, 10],
        "{{PRINCIPAL_NAME}}": [5, 10],
    },
    "csr-wsl-5": {
        "{{COMPANY_NAME}}": [1, 7],
        "{{CSR_HEAD_NAME}}": [3, 5, 10],
    },
}

BANNED_PHRASES = [
    "Omkar",
    "hope you're doing well",
    "just following up",
    "checking in",
    "gentle reminder",
    "circling back",
    "We deliver, and we always deliver",
    "We don't let people down",
]

ADDRESS_SNIPPET = "Baner - Mahalunge Rd"
SIGNATURE_SNIPPET = "Baban Jadhav"


def get_templates():
    conn = sqlite3.connect("campaign_data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT sequence_id, day, subject, html_body, text_body FROM templates WHERE sequence_id IN ('school', 'csr-wsl-5')"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def normalize_sentences(text: str) -> list:
    # Strip HTML footer to avoid false positives on shared address/signature
    text = re.sub(r'<div class="footer".*?</div>', ' ', text, flags=re.DOTALL)
    # Strip HTML tags
    t = re.sub(r"<[^>]+>", " ", text)
    # Replace newlines with spaces
    t = t.replace("\n", " ")
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    # Split on sentence boundaries
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]
    return sentences


def main():
    rows = get_templates()
    errors = []
    warnings = []
    found_days = defaultdict(set)
    all_sentences_by_seq = defaultdict(list)

    for row in rows:
        seq = row["sequence_id"]
        day = row["day"]
        found_days[seq].add(day)
        subject = row["subject"] or ""
        html = row["html_body"] or ""
        text = row["text_body"] or ""
        combined = f"{subject}\n{html}\n{text}"

        # Check banned phrases
        for phrase in BANNED_PHRASES:
            if phrase.lower() in combined.lower():
                errors.append(f"[{seq} day {day}] Banned phrase found: '{phrase}'")

        # Check signature and address
        if SIGNATURE_SNIPPET not in combined:
            errors.append(f"[{seq} day {day}] Missing signature: '{SIGNATURE_SNIPPET}'")
        if ADDRESS_SNIPPET not in combined:
            errors.append(f"[{seq} day {day}] Missing address: '{ADDRESS_SNIPPET}'")

        # Check placeholders
        required = PLACEHOLDER_REQUIRED_DAYS.get(seq, {})
        for ph, days in required.items():
            if day in days and ph not in subject and ph not in html and ph not in text:
                errors.append(f"[{seq} day {day}] Missing placeholder: {ph}")

        # Check assets/URLs
        expected = EXPECTED_ASSETS.get(seq, {}).get(day, set())
        for asset_key in expected:
            url = SEQUENCES[seq]["assets"][day].get(asset_key, "")
            if url and url not in combined:
                errors.append(f"[{seq} day {day}] Missing asset URL '{asset_key}': {url}")

        # Collect sentences for intra-sequence repetition check
        sentences = normalize_sentences(html)
        for s in sentences:
            if len(s) > 15:  # ignore very short fragments
                all_sentences_by_seq[(seq, day)].append(s.lower())

    # Ensure all days present
    for seq in ["school", "csr-wsl-5"]:
        expected_days = set(SEQUENCES[seq]["days"])
        missing = expected_days - found_days[seq]
        if missing:
            errors.append(f"[{seq}] Missing template days: {sorted(missing)}")

    # Check for repeated sentences within each sequence
    for seq in ["school", "csr-wsl-5"]:
        sentence_counts = defaultdict(list)
        for day in SEQUENCES[seq]["days"]:
            for s in all_sentences_by_seq.get((seq, day), []):
                sentence_counts[s].append(day)
        for s, days in sentence_counts.items():
            if len(days) > 1:
                warnings.append(f"[{seq}] Repeated sentence across days {days}: {s[:120]}")

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("No errors found.")

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("No warnings.")

    print(f"\nVerified {len(rows)} templates.")
    return len(errors) == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
