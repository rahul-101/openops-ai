from app.infrastructure.cache.cache_service import (
    InMemoryCacheService,
)
from app.infrastructure.cache.prompt_cache import (
    PromptCache,
)


class TestPromptCache:

    def test_set_and_get_round_trip(self):

        cache = PromptCache(
            cache=InMemoryCacheService(),
        )

        cache.set("triage", "prompt text", {"rendered": True})

        assert cache.get("triage", "prompt text") == {
            "rendered": True,
        }

    def test_versioned_keys_are_distinct(self):

        cache = PromptCache(
            cache=InMemoryCacheService(),
        )

        cache.set("triage", "text", "v1-result", version="v1")

        cache.set("triage", "text", "v2-result", version="v2")

        assert cache.get("triage", "text", version="v1") == "v1-result"

        assert cache.get("triage", "text", version="v2") == "v2-result"

    def test_text_change_invalidates(self):

        cache = PromptCache(
            cache=InMemoryCacheService(),
        )

        cache.set("triage", "old text", "old-result")

        assert cache.get("triage", "new text") is None

    def test_missing_returns_none(self):

        cache = PromptCache(
            cache=InMemoryCacheService(),
        )

        assert cache.get("unknown", "text") is None

    def test_set_returns_key(self):

        cache = PromptCache(
            cache=InMemoryCacheService(),
        )

        key = cache.set("triage", "text", "result")

        assert isinstance(key, str)

        assert len(key) == 64

    def test_invalidate_is_noop(self):

        cache = PromptCache(
            cache=InMemoryCacheService(),
        )

        cache.invalidate("triage")

        assert cache.get("triage", "text") is None
