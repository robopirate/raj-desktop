"""
main.py — Raj Agent v4.0 Entry Point
Batch system, Calendar/Drive integration, Dashboard pipeline
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import Database
from gmail import GmailClient
from engine import CampaignEngine
from raj_brain import RajBrain
from raj_chat import RajChatApp
from raj_guard import RajGuard

try:
    from smart_importer import SmartImporter
    print("[OK] Smart Importer loaded")
except ImportError:
    print("[Warning] smart_importer.py not found. Smart import features disabled.")

try:
    from tray_icon import RajTrayIcon, add_to_startup, remove_from_startup
    TRAY_AVAILABLE = True
except ImportError:
    print("[Warning] pystray/Pillow not installed. System tray icon disabled.")
    print("          Run: pip install pystray Pillow")
    TRAY_AVAILABLE = False
    RajTrayIcon = None
    add_to_startup = lambda: False
    remove_from_startup = lambda: False

def main():
    print("=" * 50)
    print("  Raj — Email Command Center v4.0")
    print("  Dashboard | Batches | Pipeline | Calendar | Drive")
    print("=" * 50)

    db = Database()

    print("\n[1/3] Connecting to Gmail...")
    try:
        gmail = GmailClient()
        print("OK Gmail connected")
    except FileNotFoundError:
        print("\nERROR: credentials.json not found!")
        print("   1. Go to https://console.cloud.google.com")
        print("   2. Create project -> Enable Gmail API")
        print("   3. Create OAuth 2.0 credentials (Desktop app)")
        print("   4. Download JSON and save as 'credentials.json' in this folder")
        input("\nPress Enter to exit...")
        return
    except Exception as e:
        print(f"ERROR Gmail: {e}")
        input("\nPress Enter to exit...")
        return

    print("[2/3] Starting engine...")
    engine = CampaignEngine(db, gmail)

    brief_email = db.get_meta("brief_email")
    if brief_email:
        engine.brief_email = brief_email
    ollama_url = db.get_meta("ollama_url")
    if ollama_url:
        engine.ollama_url = ollama_url

    engine.start()  # Start the engine loop
    print("OK Engine ready")
    print("   Calendar:", "✅" if engine.calendar else "❌")
    print("   Drive:", "✅" if engine.drive else "❌")

    print("[3/3] Initializing Raj...")
    brain = RajBrain(engine, ollama_url=engine.ollama_url)
    print("OK Raj v4.0 is online")

    guard = RajGuard(os.path.dirname(__file__))
    guard.start()

    print("\nREADY! Dashboard opening...")
    print("   📊 Dashboard shows live pipeline")
    print("   🚀 Batches tab for campaign management")
    print("   Type 'help' to see commands\n")

    app = RajChatApp(engine, brain)

    tray = None
    if TRAY_AVAILABLE:
        tray = RajTrayIcon(engine, app)
        tray.start()
    else:
        print("[Tray] System tray icon not available")

    app.mainloop()

    if tray:
        tray.stop()
    if 'guard' in locals():
        guard.stop()
    engine.stop()
    print("\nRaj signing off. Goodbye, sir.")

if __name__ == "__main__":
    main()
