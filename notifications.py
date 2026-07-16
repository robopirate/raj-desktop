"""notifications.py — desktop toast notifications for Raj events.

Uses `plyer` (already in requirements.txt) so notifications work on Windows,
macOS, and Linux without extra dependencies.
"""

from plyer import notification
from pathlib import Path

ICON_PATH = Path(__file__).resolve().parent / "assets" / "icon.ico"
if not ICON_PATH.exists():
    ICON_PATH = Path(__file__).resolve().parent / "assets" / "icon.png"


def notify(title: str, message: str, timeout: int = 8) -> None:
    """Show a desktop toast notification."""
    try:
        kwargs = {
            "title": title,
            "message": message,
            "timeout": timeout,
        }
        if ICON_PATH.exists():
            kwargs["app_icon"] = str(ICON_PATH)
        notification.notify(**kwargs)
    except Exception as e:
        print(f"[Notify] Could not show notification: {e}")


def notify_batch_complete(batch_name: str, sent: int, replied: int) -> None:
    notify(
        "Raj — Campaign Complete",
        f"{batch_name}: {sent} sent, {replied} replied",
    )


def notify_new_reply(sender: str, snippet: str) -> None:
    notify(
        "Raj — New Reply",
        f"From {sender}: {snippet[:80]}",
    )


def notify_auth_expired(service: str) -> None:
    notify(
        "Raj — Connection Lost",
        f"{service} authentication expired. Reconnect in Settings.",
        timeout=12,
    )


def notify_error(message: str) -> None:
    notify(
        "Raj — Error",
        message,
        timeout=10,
    )
