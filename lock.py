"""lock.py — single-instance guard for the Raj desktop app.

Tries to bind a well-known localhost port. If another Raj process already holds
it, we consider the app already running and exit (or focus the existing window).
"""

import socket

LOCK_HOST = "127.0.0.1"
LOCK_PORT = 55555


class SingleInstanceLock:
    """Hold a single-instance lock via a TCP socket."""

    def __init__(self, host: str = LOCK_HOST, port: int = LOCK_PORT):
        self.host = host
        self.port = port
        self._sock = None

    def acquire(self) -> bool:
        """Try to acquire the lock. Return True if acquired, False if held."""
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Do NOT use SO_REUSEADDR — we want a true lock.
            self._sock.bind((self.host, self.port))
            self._sock.listen(1)
            return True
        except socket.error:
            if self._sock:
                try:
                    self._sock.close()
                except Exception:
                    pass
                self._sock = None
            return False

    def release(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None


def is_already_running(host: str = LOCK_HOST, port: int = LOCK_PORT) -> bool:
    """Convenience check without holding the lock long-term."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.close()
        return False
    except socket.error:
        return True
