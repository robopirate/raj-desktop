#!/usr/bin/env python3
"""Clean up Raj scheduled drafts from Gmail.
Run: python cleanup_drafts.py"""

import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def get_gmail_service():
    creds = None
    try:
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
    except FileNotFoundError:
        print("No token.pickle found. Run the main app first to authenticate.")
        return None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Credentials expired. Run the main app first.")
            return None
    return build('gmail', 'v1', credentials=creds)

def cleanup_raj_drafts():
    service = get_gmail_service()
    if not service:
        return

    print("Fetching drafts...")
    deleted = 0
    skipped = 0
    page_token = None

    while True:
        result = service.users().drafts().list(userId='me', pageToken=page_token).execute()
        drafts = result.get('drafts', [])
        if not drafts:
            break

        for d in drafts:
            try:
                meta = service.users().drafts().get(userId='me', id=d['id'], format='metadata').execute()
                msg = meta.get('message', {})
                subject = ''
                for h in msg.get('payload', {}).get('headers', []):
                    if h['name'].lower() == 'subject':
                        subject = h['value']
                        break

                if '[RAJ-SCHEDULE:' in subject:
                    service.users().drafts().delete(userId='me', id=d['id']).execute()
                    deleted += 1
                    print(f"  Deleted: {subject[:60]}")
                else:
                    skipped += 1
            except Exception as e:
                print(f"  Error processing draft {d['id']}: {e}")

        page_token = result.get('nextPageToken')
        if not page_token:
            break

    print(f"\nDone! Deleted {deleted} Raj drafts. Skipped {skipped} non-Raj drafts.")

if __name__ == '__main__':
    cleanup_raj_drafts()
