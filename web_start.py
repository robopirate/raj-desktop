"""
web_start.py — Entry point for the new Raj web UI.
Starts the Flask dev server and opens the local URL in the default browser.
"""

import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "web"))

from web.app import app

HOST = "127.0.0.1"
PORT = 5555
URL = f"http://{HOST}:{PORT}"


def open_browser():
    time.sleep(1.2)
    print(f"[WebStart] Opening browser: {URL}")
    webbrowser.open(URL)


if __name__ == "__main__":
    print("=" * 50)
    print("  Raj — Web Command Center")
    print(f"  {URL}")
    print("=" * 50)

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
