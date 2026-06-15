from plyer import notification


def notify(title, message, timeout=5):
    """Show a desktop notification. Silently ignored if plyer fails."""
    try:
        notification.notify(title=title, message=message, timeout=timeout)
    except Exception:
        pass
