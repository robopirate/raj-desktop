"""desktop.py — native desktop entry point for Raj.

Launches Flask in a background thread, wraps the web UI in a pywebview window,
and provides system-tray integration, single-instance guard, and state persistence.
"""

import ctypes
import os
import sys
import threading
import time
from pathlib import Path

import requests
import webview

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "web"))

from autostart import add_to_startup, is_autostart_enabled, remove_from_startup
from lock import SingleInstanceLock
from notifications import notify_error
from state import load_state, save_state, update_state
from tray import TrayManager
from web.app import _engine

HOST = "127.0.0.1"
PORT = 5555
URL = f"http://{HOST}:{PORT}"
HEALTH_URL = f"{URL}/api/health"

_shutdown_requested = threading.Event()
_exit_requested = threading.Event()


def _message_box(title: str, message: str) -> None:
    """Show a native Windows message box."""
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x0)
    except Exception:
        print(f"{title}: {message}")


def _wait_for_server(timeout: float = 15.0) -> bool:
    """Wait until the Flask server is responding to health checks."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(HEALTH_URL, timeout=1)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def _start_flask() -> None:
    """Run the Flask dev server in a daemon thread."""
    from web.app import app

    def run():
        try:
            app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
        finally:
            _shutdown_requested.set()

    threading.Thread(target=run, daemon=True).start()


def _set_autostart(enabled: bool) -> bool:
    """Toggle Windows startup shortcut."""
    target = PROJECT_ROOT / "desktop.py"
    if enabled:
        return add_to_startup(target)
    return remove_from_startup()


class RajDesktop:
    def __init__(self):
        self.state = load_state()
        self.window = None
        self.tray = None
        self._monitor_thread = None
        self._geometry_dirty = False

    def run(self) -> None:
        # Single-instance guard
        lock = SingleInstanceLock()
        if not lock.acquire():
            _message_box("Raj already running", "Raj is already running. Check the system tray.")
            sys.exit(0)

        # Sync autostart shortcut with state preference
        try:
            if self.state["desktop"].get("start_on_boot") and not is_autostart_enabled():
                _set_autostart(True)
            elif not self.state["desktop"].get("start_on_boot") and is_autostart_enabled():
                _set_autostart(False)
        except Exception as e:
            print(f"[Desktop] Autostart sync warning: {e}")

        # Start Flask
        _start_flask()
        if not _wait_for_server(timeout=15):
            _message_box("Raj failed to start", "The Raj backend did not start. Check the logs.")
            sys.exit(1)

        # Auto-start engine if requested
        if self.state.get("desktop", {}).get("engine_autostart"):
            try:
                if _engine and not _engine.is_running():
                    _engine.start()
                    print("[Desktop] Engine auto-started")
            except Exception as e:
                print(f"[Desktop] Engine autostart warning: {e}")

        # Create window
        win_cfg = self.state.get("window", {})
        self.window = webview.create_window(
            title="Raj — RoboPirate Command Center",
            url=URL,
            width=win_cfg.get("width", 1400),
            height=win_cfg.get("height", 900),
            x=win_cfg.get("x", 100),
            y=win_cfg.get("y", 50),
            min_size=(1000, 700),
            text_select=True,
            confirm_close=False,
        )

        # Wire events
        self.window.events.closing += self._on_closing
        self.window.events.closed += self._on_closed
        self.window.events.resized += self._on_resized
        self.window.events.moved += self._on_moved

        # Start tray
        self.tray = TrayManager(
            on_show=self._show_window,
            on_pause_toggle=self._toggle_pause,
            on_exit=self._exit_app,
        )
        self.tray.start()

        # Background monitors
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        # Block on the webview event loop
        try:
            webview.start()
        finally:
            lock.release()
            self.tray.stop()
            self._save_geometry_if_dirty()

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_closing(self):
        """Return False to keep running in tray; True to close."""
        self._save_geometry_if_dirty()
        if self.state.get("desktop", {}).get("minimize_to_tray", True):
            try:
                self.window.hide()
            except Exception:
                pass
            return False
        self._exit_app()
        return True

    def _on_closed(self):
        _exit_requested.set()

    def _on_resized(self, width, height):
        self.state["window"]["width"] = width
        self.state["window"]["height"] = height
        self._geometry_dirty = True

    def _on_moved(self, x, y):
        self.state["window"]["x"] = x
        self.state["window"]["y"] = y
        self._geometry_dirty = True

    # ── Tray callbacks ────────────────────────────────────────────────────────

    def _show_window(self):
        if self.window:
            try:
                self.window.show()
                self.window.restore()  # in case minimized
            except Exception:
                pass

    def _toggle_pause(self):
        try:
            if _engine is None:
                return
            if getattr(_engine, "_paused", False):
                _engine.resume()
            else:
                _engine.pause()
            time.sleep(0.1)
            self._update_tray_pause_state()
        except Exception as e:
            notify_error(f"Could not toggle engine: {e}")

    def _exit_app(self):
        self._save_geometry_if_dirty()
        _shutdown_requested.set()
        try:
            if self.window:
                self.window.destroy()
        except Exception:
            pass
        try:
            self.tray.stop()
        except Exception:
            pass
        _exit_requested.set()

    # ── Background loop ───────────────────────────────────────────────────────

    def _monitor_loop(self):
        """Poll engine status for tray label and watch for shutdown signal."""
        while not _exit_requested.is_set():
            try:
                if _shutdown_requested.is_set():
                    self._exit_app()
                    break
                self._update_tray_pause_state()
                _exit_requested.wait(5)
            except Exception as e:
                print(f"[Desktop] Monitor loop error: {e}")
                time.sleep(5)

    def _update_tray_pause_state(self):
        if self.tray and _engine:
            try:
                self.tray.set_paused(bool(getattr(_engine, "_paused", False)))
            except Exception:
                pass

    # ── State helpers ─────────────────────────────────────────────────────────

    def _save_geometry_if_dirty(self):
        if self._geometry_dirty:
            save_state(self.state)
            self._geometry_dirty = False


if __name__ == "__main__":
    RajDesktop().run()
