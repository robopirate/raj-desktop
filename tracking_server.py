"""
tracking_server.py — Lightweight HTTP server for email open/click tracking.
Runs in a background thread, serves 1x1 pixel and link redirects.
No Flask dependency — uses Python's built-in http.server.
"""

import base64
import json
import sqlite3
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# 1x1 transparent GIF (43 bytes)
TRANSPARENT_GIF = bytes([
    0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00, 0x01, 0x00,
    0x80, 0x00, 0x00, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x2c,
    0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x02,
    0x02, 0x44, 0x01, 0x00, 0x3b
])


def _encode_token(recipient_id, batch_id, send_id):
    """Encode tracking token as base64 JSON."""
    data = json.dumps({"r": recipient_id, "b": batch_id, "s": send_id})
    return base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")


def _decode_token(token):
    """Decode tracking token. Returns (recipient_id, batch_id, send_id) or None."""
    try:
        # Add padding back
        padding = 4 - len(token) % 4
        if padding != 4:
            token += "=" * padding
        data = json.loads(base64.urlsafe_b64decode(token.encode()))
        return data.get("r"), data.get("b"), data.get("s")
    except Exception:
        return None


def make_tracking_urls(base_url, recipient_id, batch_id, send_id):
    """Generate tracking URLs for a recipient."""
    token = _encode_token(recipient_id, batch_id, send_id)
    open_url = f"{base_url}/track/open?token={token}"
    click_base = f"{base_url}/track/click?token={token}&url="
    return open_url, click_base


def inject_tracking_pixel(html_body, open_url):
    """Append a 1x1 tracking pixel to HTML body before closing </body> or at end."""
    pixel = f'<img src="{open_url}" width="1" height="1" alt="" style="display:block;border:0;">'
    if "</body>" in html_body.lower():
        # Insert before closing body
        idx = html_body.lower().rfind("</body>")
        return html_body[:idx] + pixel + html_body[idx:]
    else:
        return html_body + pixel


def wrap_links(html_body, click_base):
    """Wrap all <a href="..."> links with tracking redirect."""
    import re

    def _replace_link(match):
        original_url = match.group(1)
        # Don't wrap mailto, tel, anchor links, or already-wrapped links
        if any(original_url.startswith(p) for p in ["mailto:", "tel:", "#", "javascript:"]):
            return match.group(0)
        if "/track/click?" in original_url:
            return match.group(0)
        # URL-encode the target URL
        from urllib.parse import quote
        tracked_url = click_base + quote(original_url, safe="")
        return f'href="{tracked_url}"'

    # Match href="..." in <a> tags
    return re.sub(r'href="([^"]+)"', _replace_link, html_body)


class TrackingHandler(BaseHTTPRequestHandler):
    """HTTP request handler for tracking opens and clicks."""

    db_path = None  # Set by TrackingServer

    def log_message(self, format, *args):
        # Suppress default logging — too noisy
        pass

    def _record(self, event_type, recipient_id, batch_id, send_id, url=None, user_agent=None, ip=None):
        """Record engagement event via a fresh SQLite connection."""
        if not self.db_path:
            return
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                INSERT INTO engagement_events (recipient_id, batch_id, send_id, event_type, url, user_agent, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (recipient_id, batch_id, send_id, event_type, url, user_agent, ip))
            # Update sends table for quick aggregation
            if send_id:
                if event_type == "open":
                    conn.execute("UPDATE sends SET opened_at=COALESCE(opened_at, CURRENT_TIMESTAMP) WHERE id=?", (send_id,))
                elif event_type == "click":
                    conn.execute("UPDATE sends SET clicked_at=COALESCE(clicked_at, CURRENT_TIMESTAMP) WHERE id=?", (send_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Tracking] Record error: {e}")

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        path = parsed.path

        user_agent = self.headers.get("User-Agent", "")
        ip = self.client_address[0]

        if path == "/track/open":
            token = qs.get("token", [""])[0]
            decoded = _decode_token(token)
            if decoded:
                r, b, s = decoded
                self._record("open", r, b, s, user_agent=user_agent, ip=ip)
            self.send_response(200)
            self.send_header("Content-Type", "image/gif")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(TRANSPARENT_GIF)
            return

        if path == "/track/click":
            token = qs.get("token", [""])[0]
            url = qs.get("url", [""])[0]
            decoded = _decode_token(token)
            if decoded:
                r, b, s = decoded
                self._record("click", r, b, s, url=url, user_agent=user_agent, ip=ip)
            # Redirect to target URL
            self.send_response(302)
            self.send_header("Location", url or "/")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.end_headers()
            return

        # Health check
        if path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
            return

        self.send_response(404)
        self.end_headers()


class TrackingServer:
    """Background HTTP server for email tracking."""

    def __init__(self, db_path, port=0):
        """port=0 means auto-assign (os picks free port)."""
        self.db_path = db_path
        self.port = port
        self.base_url = None
        self._server = None
        self._thread = None

    def start(self):
        TrackingHandler.db_path = self.db_path
        self._server = HTTPServer(("0.0.0.0", self.port), TrackingHandler)
        # If port was 0, get the assigned port
        actual_port = self._server.server_address[1]
        self.port = actual_port
        # Use 127.0.0.1 for local testing; replace with public IP/LAN IP for external tracking
        self.base_url = f"http://127.0.0.1:{actual_port}"
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()
        print(f"[Tracking] Server started on {self.base_url}")
        return self.base_url

    def _serve(self):
        try:
            self._server.serve_forever()
        except Exception as e:
            print(f"[Tracking] Server error: {e}")

    def stop(self):
        if self._server:
            self._server.shutdown()
            print("[Tracking] Server stopped")

    def get_tracking_urls(self, recipient_id, batch_id, send_id):
        """Convenience: generate tracking URLs for a recipient."""
        if not self.base_url:
            return None, None
        return make_tracking_urls(self.base_url, recipient_id, batch_id, send_id)

    def inject_tracking(self, html_body, recipient_id, batch_id, send_id):
        """Inject tracking pixel and wrap links in HTML body."""
        open_url, click_base = self.get_tracking_urls(recipient_id, batch_id, send_id)
        if not open_url:
            return html_body
        body = inject_tracking_pixel(html_body, open_url)
        body = wrap_links(body, click_base)
        return body
