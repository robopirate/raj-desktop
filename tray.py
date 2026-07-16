"""tray.py — system tray icon for Raj desktop app."""

import threading
from pathlib import Path
from typing import Callable

import pystray
from PIL import Image

ICON_PATH = Path(__file__).resolve().parent / "assets" / "icon.png"


class TrayManager:
    """Manages the system tray icon and menu."""

    def __init__(
        self,
        on_show: Callable[[], None],
        on_pause_toggle: Callable[[], None],
        on_exit: Callable[[], None],
    ):
        self.on_show = on_show
        self.on_pause_toggle = on_pause_toggle
        self.on_exit = on_exit
        self._icon = None
        self._engine_paused = False
        self._thread = None

    def start(self) -> None:
        image = self._load_image()
        menu = pystray.Menu(
            pystray.MenuItem("Show Raj", self._show),
            pystray.MenuItem(self._pause_label, self._pause_toggle),
            pystray.MenuItem("Exit", self._exit),
        )
        self._icon = pystray.Icon("raj", image, "Raj Command Center", menu)
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def set_paused(self, paused: bool) -> None:
        self._engine_paused = paused
        if self._icon:
            self._icon.update_menu()

    def _load_image(self) -> Image.Image:
        if ICON_PATH.exists():
            return Image.open(ICON_PATH)
        # Fallback: tiny teal square
        img = Image.new("RGBA", (32, 32), (13, 148, 136, 255))
        return img

    def _pause_label(self, menu_item):
        return "Resume Engine" if self._engine_paused else "Pause Engine"

    def _show(self, icon, item):
        self.on_show()

    def _pause_toggle(self, icon, item):
        self.on_pause_toggle()

    def _exit(self, icon, item):
        self.on_exit()
