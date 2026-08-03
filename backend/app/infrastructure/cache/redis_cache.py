import json

from app.infrastructure.cache.cache_service import (
    CacheService,
    InMemoryCacheService,
)


class RedisCacheService(CacheService):
    """
    Redis-backed cache implementation.

    Requires the `redis` package. Falls back to an in-memory
    cache when Redis is unavailable (connection errors) so the
    application keeps functioning during cache outages.
    """

    def __init__(
        self,
        client=None,
        fallback: CacheService | None = None,
    ) -> None:

        self._client = client

        self._fallback = fallback or InMemoryCacheService()

    # ==========================================================
    # Primary (Redis) / Fallback (memory)
    # ==========================================================

    def _available(self) -> bool:

        return self._client is not None

    def get(
        self,
        key: str,
    ) -> object | None:

        if not self._available():
            return self._fallback.get(key)

        try:

            value = self._client.get(key)

            if value is None:
                return None

            return json.loads(value)

        except Exception:
            return self._fallback.get(key)

    def set(
        self,
        key: str,
        value: object,
        ttl_seconds: int | None = None,
    ) -> None:

        if not self._available():

            self._fallback.set(
                key,
                value,
                ttl_seconds=ttl_seconds,
            )

            return

        try:

            payload = json.dumps(value, default=str)

            if ttl_seconds is not None:
                self._client.set(
                    key,
                    payload,
                    ex=ttl_seconds,
                )
            else:
                self._client.set(key, payload)

        except Exception:

            self._fallback.set(
                key,
                value,
                ttl_seconds=ttl_seconds,
            )

    def delete(
        self,
        key: str,
    ) -> None:

        if not self._available():

            self._fallback.delete(key)

            return

        try:
            self._client.delete(key)
        except Exception:
            self._fallback.delete(key)

    def exists(
        self,
        key: str,
    ) -> bool:

        if not self._available():
            return self._fallback.exists(key)

        try:

            return bool(self._client.exists(key))

        except Exception:
            return self._fallback.exists(key)

    def clear(self) -> None:

        if not self._available():

            self._fallback.clear()

            return

        try:
            self._client.flushdb()
        except Exception:
            self._fallback.clear()

    def size(self) -> int:

        if not self._available():
            return self._fallback.size()

        try:

            return int(self._client.dbsize() or 0)

        except Exception:
            return self._fallback.size()
