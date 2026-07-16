"""autostart.py — add/remove Raj from Windows startup using a temporary VBS helper.

Avoids a dependency on pywin32/winshell by calling the Windows Script Host runtime
that ships with Windows.
"""

import os
import subprocess
import tempfile
from pathlib import Path


def _startup_dir() -> Path:
    return Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _shortcut_path() -> Path:
    return _startup_dir() / "Raj.lnk"


def _default_target() -> Path:
    root = Path(__file__).resolve().parent
    desktop = root / "desktop.py"
    if desktop.exists():
        return desktop
    return root / "web_start.py"


def is_autostart_enabled() -> bool:
    return _shortcut_path().exists()


def _create_shortcut_vbs(target: Path, shortcut: Path, icon: Path) -> str:
    """Return VBS source that creates a Windows shortcut."""
    return f"""Set WshShell = WScript.CreateObject("WScript.Shell")
Set lnk = WshShell.CreateShortcut("{shortcut}")
lnk.TargetPath = "{target}"
lnk.WorkingDirectory = "{target.parent}"
lnk.IconLocation = "{icon},0"
lnk.Save
"""


def add_to_startup(target: Path = None) -> bool:
    """Create a Windows shortcut in the user's Startup folder."""
    target = target or _default_target()
    if not target or not target.exists():
        print("[Autostart] Target script not found, cannot add to startup.")
        return False

    try:
        _startup_dir().mkdir(parents=True, exist_ok=True)
        shortcut = _shortcut_path()
        icon = target.parent / "assets" / "icon.ico"
        if not icon.exists():
            icon = target.parent / "assets" / "icon.png"

        vbs = _create_shortcut_vbs(target.resolve(), shortcut.resolve(), icon.resolve() if icon.exists() else target.resolve())
        with tempfile.NamedTemporaryFile("w", suffix=".vbs", delete=False, encoding="utf-8") as f:
            f.write(vbs)
            vbs_path = f.name

        result = subprocess.run(
            ["cscript", "//nologo", vbs_path],
            capture_output=True,
            text=True,
            check=False,
        )
        os.unlink(vbs_path)
        if result.returncode != 0:
            print(f"[Autostart] VBS error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"[Autostart] Failed to add shortcut: {e}")
        return False


def remove_from_startup() -> bool:
    """Remove the Windows startup shortcut."""
    shortcut = _shortcut_path()
    if shortcut.exists():
        try:
            shortcut.unlink()
            return True
        except Exception as e:
            print(f"[Autostart] Failed to remove shortcut: {e}")
    return False
