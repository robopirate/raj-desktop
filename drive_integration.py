"""
drive_integration.py — Google Drive for Raj v4.0
File attachments for templates, link validation.
"""

import os
import pickle
import threading
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.file']

class DriveManager:
    def __init__(self, credentials_path=None, token_path=None):
        self.credentials_path = credentials_path or str(Path(__file__).parent / "credentials.json")
        self.token_path = token_path or str(Path(__file__).parent / "drive_token.pickle")
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
            print("[Drive] Connected to Google Drive")
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
            self.service = build('drive', 'v3', credentials=creds)
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
                self.service = build('drive', 'v3', credentials=creds)
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
            raise FileNotFoundError(f"[Drive] credentials.json not found at {self.credentials_path}")

        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
        with open(self.token_path, 'wb') as token:
            pickle.dump(creds, token)
        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self, folder_id=None, query=None, page_size=100):
        """List files in Drive."""
        if not self.service:
            return []

        q = query or ""
        if folder_id:
            q += f"'{folder_id}' in parents" if not q else f" and '{folder_id}' in parents"

        results = self.service.files().list(
            q=q, pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType, webViewLink, modifiedTime)").execute()

        return results.get('files', [])

    def get_file_url(self, file_id):
        """Get direct download/view URL for a file."""
        if not self.service:
            return None

        try:
            file = self.service.files().get(fileId=file_id, fields='id, name, webViewLink, webContentLink').execute()
            return {
                'id': file['id'],
                'name': file['name'],
                'view_url': file.get('webViewLink', ''),
                'download_url': file.get('webContentLink', '')
            }
        except:
            return None

    def validate_link(self, file_id):
        """Check if a Drive file link is still valid."""
        if not self.service:
            return False

        try:
            self.service.files().get(fileId=file_id, fields='id').execute()
            return True
        except:
            return False

    def upload_file(self, filepath, filename=None, folder_id=None):
        """Upload a file to Drive."""
        if not self.service:
            return None

        try:
            name = filename or os.path.basename(filepath)
            file_metadata = {'name': name}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            media = MediaFileUpload(filepath, resumable=True)
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

            return {
                'id': file['id'],
                'name': name,
                'url': file.get('webViewLink', '')
            }
        except Exception as e:
            print(f"[Drive] Upload failed: {e}")
            return None
