"""
tray_icon.py -- System tray icon for Raj
Runs in background, auto-starts with Windows, right-click menu
"""

import os
import sys
import threading
import webbrowser
from pathlib import Path

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    print("pystray or Pillow not installed. Run: pip install pystray Pillow")
    sys.exit(1)

class RajTrayIcon:
    def __init__(self, engine=None, app=None):
        self.engine = engine
        self.app = app
        self.icon = None
        self._stop_event = threading.Event()

    def _create_image(self):
        """Create a simple Raj icon (teal circle with R)."""
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), '#0a0f0f')
        dc = ImageDraw.Draw(image)
        # Teal circle
        dc.ellipse([4, 4, 60, 60], fill='#0D9B8A', outline='#0BC5B0', width=2)
        # White R
        dc.text((22, 18), "R", fill='white', font=None)
        return image

    def _on_open(self, icon, item):
        """Open full Raj window."""
        if self.app:
            self.app.after(0, self.app.deiconify)
            self.app.after(0, self.app.lift)

    def _on_status(self, icon, item):
        """Show quick status notification."""
        if self.engine:
            running = "Running" if self.engine.is_running() else "Stopped"
            paused = "Paused" if self.engine.is_paused() else "Active"
            # pystray doesn't have native notifications, but we can open a mini window
            # For now, just print to console
            print(f"Raj Status: {running} | {paused}")

    def _on_gmail(self, icon, item):
        """Open Gmail."""
        webbrowser.open("https://mail.google.com")

    def _on_brief(self, icon, item):
        """Send morning brief now."""
        if self.engine:
            brief = self.engine.morning_brief()
            print(brief)

    def _on_deep_scan(self, icon, item):
        """Run deep scan."""
        if self.engine:
            count = self.engine.scan_bounces(days_back=15)
            print(f"Deep scan complete: {count} addresses blacklisted")

    def _on_exit(self, icon, item):
        """Exit Raj completely."""
        if self.app:
            self.app.after(0, self.app.quit)
        self._stop_event.set()
        icon.stop()

    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem("📊 Open Raj", self._on_open),
            pystray.MenuItem("📧 Open Gmail", self._on_gmail),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🔄 Deep Scan (15 days)", self._on_deep_scan),
            pystray.MenuItem("📋 Morning Brief", self._on_brief),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Exit", self._on_exit),
        )

    def start(self):
        """Start tray icon in background thread."""
        def run_tray():
            self.icon = pystray.Icon(
                "raj_tray",
                self._create_image(),
                "Raj — Email Command Center",
                self._build_menu()
            )
            self.icon.run()

        thread = threading.Thread(target=run_tray, daemon=True)
        thread.start()
        print("[Tray] System tray icon active")

    def stop(self):
        """Stop tray icon."""
        if self.icon:
            self.icon.stop()


def add_to_startup():
    """Add Raj to Windows startup."""
    import winreg
    try:
        # Path to START.bat
        bat_path = Path(__file__).parent / "START.bat"
        if not bat_path.exists():
            print(f"[Startup] START.bat not found at {bat_path}")
            return False

        # Registry key for current user startup
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)

        # Use cmd /c to run the batch file hidden
        cmd = f'cmd /c start /min "" "{bat_path}"'
        winreg.SetValueEx(key, "RajEmailCommandCenter", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)

        print("[Startup] Raj added to Windows startup. Will auto-launch on boot.")
        return True
    except Exception as e:
        print(f"[Startup] Failed to add to startup: {e}")
        return False


def remove_from_startup():
    """Remove Raj from Windows startup."""
    import winreg
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "RajEmailCommandCenter")
        winreg.CloseKey(key)
        print("[Startup] Raj removed from Windows startup.")
        return True
    except Exception as e:
        print(f"[Startup] Failed to remove: {e}")
        return False


if __name__ == "__main__":
    # Test tray icon standalone
    tray = RajTrayIcon()
    tray.start()
    input("Press Enter to stop tray icon...")
    tray.stop()
