"""
Simple in-memory cache with TTL expiration.

For a lightweight project like this, Redis would be overkill.
A dict + timestamp-based expiry gives us <10ms reads and keeps
the data fresh enough for a dashboard that polls every 30 seconds.
"""

import time
import threading
from typing import Any, Callable, Optional


class MemoryCache:
    """Thread-safe dict cache where each key expires after `ttl_seconds`."""

    def __init__(self):
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Return cached value if it exists and hasn't expired; otherwise None."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: float) -> None:
        """Store a value that lives for `ttl` seconds."""
        with self._lock:
            self._store[key] = (time.monotonic() + ttl, value)

    def get_or_fetch(self, key: str, ttl: float, fetcher: Callable[[], Any]) -> Any:
        """
        Return cached value if valid, otherwise call `fetcher`, cache the
        result, and return it.
        """
        cached = self.get(key)
        if cached is not None:
            return cached
        fresh = fetcher()
        self.set(key, fresh, ttl)
        return fresh

    def invalidate(self, key: Optional[str] = None) -> None:
        """Drop a single key or, if key is None, clear the entire cache."""
        with self._lock:
            if key is None:
                self._store.clear()
            else:
                self._store.pop(key, None)


# Singleton used by the router + scheduler
cache = MemoryCache()
