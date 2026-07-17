"""
calendar_integration.py — Google Calendar for Raj v4.0
Schedule meetings from positive replies.
"""

import os
import pickle
import threading
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarManager:
    def __init__(self, credentials_path=None, token_path=None):
        self.credentials_path = credentials_path or str(Path(__file__).parent / "credentials.json")
        self.token_path = token_path or str(Path(__file__).parent / "calendar_token.pickle")
        self.service = None
        # Try silent auth on startup; fail quietly so app can open
        try:
            self._authenticate(silent=True)
        except Exception:
            pass

    def is_connected(self):
        return self.service is not None

    def authenticate(self, callback=None):
        """Run full interactive OAuth. Calls callback(success, error) on completion."""
        try:
            self._authenticate(silent=False)
            print("[Calendar] Connected to Google Calendar")
            if callback:
                callback(True, None)
        except Exception as e:
            if callback:
                callback(False, str(e))
            else:
                raise

    def _authenticate(self, silent=False):
        creds = None
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
            except Exception:
                creds = None
                if os.path.exists(self.token_path):
                    os.remove(self.token_path)

        def _scopes_match(c):
            return set(getattr(c, 'scopes', [])) >= set(SCOPES)

        if creds and creds.valid and _scopes_match(creds):
            self.service = build('calendar', 'v3', credentials=creds)
            return

        if creds and creds.expired and creds.refresh_token:
            try:
                refresh_result = [None]

                def _refresh():
                    try:
                        creds.refresh(Request())
                        refresh_result[0] = True
                    except Exception as e:
                        refresh_result[0] = e

                t = threading.Thread(target=_refresh, daemon=True)
                t.start()
                t.join(timeout=15)
                if t.is_alive() or isinstance(refresh_result[0], Exception):
                    raise Exception("Token refresh timed out" if t.is_alive() else str(refresh_result[0]))
                if not _scopes_match(creds):
                    raise Exception("Token scopes mismatch")
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
                self.service = build('calendar', 'v3', credentials=creds)
                return
            except Exception:
                if silent:
                    raise
                creds = None
                if os.path.exists(self.token_path):
                    os.remove(self.token_path)

        if silent:
            raise Exception("Silent auth failed: no valid token")
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"[Calendar] credentials.json not found at {self.credentials_path}")

        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
        with open(self.token_path, 'wb') as token:
            pickle.dump(creds, token)
        self.service = build('calendar', 'v3', credentials=creds)

    def create_meeting(self, recipient_email, recipient_name, subject, duration_minutes=30, 
                      days_from_now=2, time_hour=10, time_minute=0, description=""):
        """Create a calendar event and send invite."""
        if not self.service:
            return None, "Calendar not connected"

        try:
            start_time = datetime.now() + timedelta(days=days_from_now)
            start_time = start_time.replace(hour=time_hour, minute=time_minute, second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=duration_minutes)

            event = {
                'summary': f'Meeting: {subject}',
                'description': description or f'Meeting with {recipient_name} regarding {subject}',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'attendees': [
                    {'email': recipient_email},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 1440},  # 1 day before
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }

            event = self.service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()

            return {
                'event_id': event['id'],
                'calendar_link': event.get('htmlLink', ''),
                'scheduled_at': start_time.isoformat(),
                'status': 'sent'
            }, None

        except Exception as e:
            return None, str(e)

    def list_upcoming(self, max_results=10):
        """List upcoming meetings."""
        if not self.service:
            return []

        now = datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(
            calendarId='primary', timeMin=now, maxResults=max_results,
            singleEvents=True, orderBy='startTime').execute()

        return events_result.get('items', [])

    def cancel_event(self, event_id):
        """Cancel a meeting."""
        if not self.service:
            return False

        try:
            self.service.events().delete(calendarId='primary', eventId=event_id, sendUpdates='all').execute()
            return True
        except:
            return False
