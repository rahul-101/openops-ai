import time
from abc import ABC, abstractmethod
from threading import Lock


class CacheService(ABC):
    """
    Contract for a key/value cache.

    Implementations may be in-memory, Redis-backed, or any
    other store. Keys are strings; values are arbitrary
    JSON-serialisable objects.
    """

    @abstractmethod
    def get(
        self,
        key: str,
    ) -> object | None:
        raise NotImplementedError

    @abstractmethod
    def set(
        self,
        key: str,
        value: object,
        ttl_seconds: int | None = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        key: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(
        self,
        key: str,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def size(self) -> int:
        raise NotImplementedError


class InMemoryCacheService(CacheService):
    """
    Thread-safe, TTL-aware in-memory cache.

    Used as the default when no external cache (e.g. Redis)
    is configured, and as a safe fallback during failures.
    """

    def __init__(
        self,
        max_entries: int | None = None,
    ) -> None:

        self._entries: dict[str, tuple[object, float | None]] = {}

        self._lock = Lock()

        self._max_entries = max_entries

    def get(
        self,
        key: str,
    ) -> object | None:

        with self._lock:

            entry = self._entries.get(key)

            if entry is None:
                return None

            value, expires_at = entry

            if expires_at is not None and time.monotonic() > expires_at:

                self._entries.pop(key, None)

                return None

            return value

    def set(
        self,
        key: str,
        value: object,
        ttl_seconds: int | None = None,
    ) -> None:

        expires_at = (
            time.monotonic() + ttl_seconds
            if ttl_seconds is not None
            else None
        )

        with self._lock:

            if (
                self._max_entries is not None
                and key not in self._entries
                and len(self._entries) >= self._max_entries
            ):

                self._evict_oldest()

            self._entries[key] = (value, expires_at)

    def delete(
        self,
        key: str,
    ) -> None:

        with self._lock:
            self._entries.pop(key, None)

    def exists(
        self,
        key: str,
    ) -> bool:

        return self.get(key) is not None

    def clear(self) -> None:

        with self._lock:
            self._entries.clear()

    def size(self) -> int:

        with self._lock:
            return len(self._entries)

    # ==========================================================
    # Helpers
    # ==========================================================

    def _evict_oldest(self) -> None:

        if not self._entries:
            return

        oldest_key = min(
            self._entries,
            key=lambda key: self._entries[key][1]
            if self._entries[key][1] is not None
            else float("inf"),
        )

        self._entries.pop(oldest_key, None)
