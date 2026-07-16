"""state.py — persist window state, last page, theme, and desktop settings."""

import json
import threading
from pathlib import Path
from typing import Any, Dict

STATE_PATH = Path(__file__).resolve().parent / "state.json"
DEFAULTS: Dict[str, Any] = {
    "window": {
        "width": 1400,
        "height": 900,
        "x": None,
        "y": None,
        "maximized": False,
    },
    "page": "dashboard",
    "theme": "light",
    "sidebar_collapsed": False,
    "desktop": {
        "minimize_to_tray": True,
        "start_on_boot": False,
        "notifications": True,
    },
}

_lock = threading.Lock()


def load_state(path: Path = STATE_PATH) -> Dict[str, Any]:
    with _lock:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                merged = _deep_merge(DEFAULTS.copy(), loaded)
                return merged
            except Exception:
                pass
        return DEFAULTS.copy()


def save_state(state: Dict[str, Any], path: Path = STATE_PATH) -> None:
    with _lock:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"[State] Failed to save state: {e}")


def update_state(updates: Dict[str, Any], path: Path = STATE_PATH) -> Dict[str, Any]:
    state = load_state(path)
    state = _deep_merge(state, updates)
    save_state(state, path)
    return state


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            base[key] = _deep_merge(base[key], value)
        else:
            base[key] = value
    return base
