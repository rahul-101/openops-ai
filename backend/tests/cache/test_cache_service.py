import time

from app.infrastructure.cache.cache_service import (
    CacheService,
    InMemoryCacheService,
)
from app.infrastructure.cache.redis_cache import (
    RedisCacheService,
)


class TestCacheServiceContract:

    def test_get_missing_returns_none(self):

        cache = InMemoryCacheService()

        assert cache.get("missing") is None

    def test_set_and_get_round_trip(self):

        cache = InMemoryCacheService()

        cache.set("key", {"value": 42})

        assert cache.get("key") == {"value": 42}

    def test_overwrite_replaces_value(self):

        cache = InMemoryCacheService()

        cache.set("key", "first")

        cache.set("key", "second")

        assert cache.get("key") == "second"

    def test_delete_removes_key(self):

        cache = InMemoryCacheService()

        cache.set("key", "value")

        cache.delete("key")

        assert cache.get("key") is None

    def test_exists(self):

        cache = InMemoryCacheService()

        assert cache.exists("key") is False

        cache.set("key", "value")

        assert cache.exists("key") is True

    def test_clear_wipes_all(self):

        cache = InMemoryCacheService()

        cache.set("a", 1)

        cache.set("b", 2)

        cache.clear()

        assert cache.size() == 0

    def test_size(self):

        cache = InMemoryCacheService()

        cache.set("a", 1)

        cache.set("b", 2)

        assert cache.size() == 2


class TestInMemoryCacheTtl:

    def test_ttl_expiry(self):

        cache = InMemoryCacheService()

        cache.set("key", "value", ttl_seconds=1)

        assert cache.get("key") == "value"

        time.sleep(1.2)

        assert cache.get("key") is None

    def test_ttl_short(self):

        cache = InMemoryCacheService()

        cache.set("key", "value", ttl_seconds=0)

        time.sleep(0.05)

        assert cache.get("key") is None

    def test_no_ttl_never_expires(self):

        cache = InMemoryCacheService()

        cache.set("key", "value")

        assert cache.get("key") == "value"


class TestInMemoryCacheEviction:

    def test_max_entries_evicts_oldest(self):

        cache = InMemoryCacheService(max_entries=2)

        cache.set("a", 1)

        cache.set("b", 2)

        cache.set("c", 3)

        assert cache.size() == 2

        assert cache.get("a") is None

    def test_existing_key_does_not_evict(self):

        cache = InMemoryCacheService(max_entries=2)

        cache.set("a", 1)

        cache.set("b", 2)

        cache.set("a", 10)

        assert cache.size() == 2

        assert cache.get("a") == 10


class FakeRedis:
    """Minimal redis-like client for testing RedisCacheService."""

    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value, ex=None):
        self.data[key] = value
        return True

    def delete(self, key):
        self.data.pop(key, None)
        return 1

    def exists(self, key):
        return 1 if key in self.data else 0

    def flushdb(self):
        self.data.clear()

    def dbsize(self):
        return len(self.data)


class TestRedisCacheService:

    def test_set_and_get_round_trip(self):

        client = FakeRedis()

        cache = RedisCacheService(client=client)

        cache.set("key", {"value": 1})

        assert cache.get("key") == {"value": 1}

    def test_missing_returns_none(self):

        cache = RedisCacheService(client=FakeRedis())

        assert cache.get("missing") is None

    def test_delete(self):

        client = FakeRedis()

        cache = RedisCacheService(client=client)

        cache.set("key", "value")

        cache.delete("key")

        assert cache.get("key") is None

    def test_exists(self):

        cache = RedisCacheService(client=FakeRedis())

        cache.set("key", "value")

        assert cache.exists("key") is True

        cache.delete("key")

        assert cache.exists("key") is False

    def test_clear(self):

        client = FakeRedis()

        cache = RedisCacheService(client=client)

        cache.set("a", 1)

        cache.set("b", 2)

        cache.clear()

        assert cache.size() == 0

    def test_fallback_when_no_client(self):

        cache = RedisCacheService(client=None)

        cache.set("key", "value")

        assert cache.get("key") == "value"

        assert cache.exists("key") is True

    def test_fallback_can_be_injected(self):

        fallback = InMemoryCacheService()

        cache = RedisCacheService(
            client=None,
            fallback=fallback,
        )

        cache.set("key", "value")

        assert fallback.get("key") == "value"

    def test_implements_interface(self):

        assert issubclass(RedisCacheService, CacheService)
