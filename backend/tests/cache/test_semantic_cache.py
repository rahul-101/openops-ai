from app.infrastructure.cache.cache_key_builder import (
    CacheKeyBuilder,
)
from app.infrastructure.cache.cache_service import (
    InMemoryCacheService,
)
from app.infrastructure.cache.semantic_cache import (
    SemanticCache,
)


class TestSemanticCache:

    def test_set_and_get_same_embedding(self):

        cache = SemanticCache(
            cache=InMemoryCacheService(),
        )

        cache.set("query", [1.0, 0.0, 0.0], "result")

        assert cache.get("query", [1.0, 0.0, 0.0]) == "result"

    def test_similar_embedding_hits_cache(self):

        cache = SemanticCache(
            cache=InMemoryCacheService(),
            similarity_threshold=0.9,
        )

        cache.set(
            "query",
            [1.0, 0.0, 0.0],
            "result",
        )

        assert cache.get("query", [0.99, 0.1, 0.0]) == "result"

    def test_dissimilar_embedding_misses(self):

        cache = SemanticCache(
            cache=InMemoryCacheService(),
            similarity_threshold=0.9,
        )

        cache.set(
            "query",
            [1.0, 0.0, 0.0],
            "result",
        )

        assert cache.get("query", [0.0, 1.0, 0.0]) is None

    def test_missing_key_returns_none(self):

        cache = SemanticCache(
            cache=InMemoryCacheService(),
        )

        assert cache.get("nothing", [1.0, 0.0]) is None

    def test_size_tracks_entries(self):

        cache = SemanticCache(
            cache=InMemoryCacheService(),
        )

        cache.set("a", [1.0, 0.0], "a-result")

        cache.set("b", [0.0, 1.0], "b-result")

        assert cache.size() == 2

    def test_clear(self):

        cache = SemanticCache(
            cache=InMemoryCacheService(),
        )

        cache.set("a", [1.0, 0.0], "a-result")

        cache.clear()

        assert cache.size() == 0

        assert cache.get("a", [1.0, 0.0]) is None

    def test_max_entries_trims(self):

        cache = SemanticCache(
            cache=InMemoryCacheService(),
            max_entries=2,
        )

        cache.set("a", [1.0, 0.0], "a-result")

        cache.set("b", [0.0, 1.0], "b-result")

        cache.set("c", [0.0, 0.0, 1.0], "c-result")

        assert cache.size() <= 2

    def test_cosine_similarity(self):

        assert SemanticCache._similarity(
            [1.0, 0.0],
            [1.0, 0.0],
        ) == 1.0

        assert SemanticCache._similarity(
            [1.0, 0.0],
            [0.0, 1.0],
        ) == 0.0

    def test_similarity_zero_for_empty(self):

        assert SemanticCache._similarity([], [1.0]) == 0.0


class TestCacheKeyBuilder:

    def test_deterministic(self):

        first = CacheKeyBuilder.build("ns", "seg", a=1)

        second = CacheKeyBuilder.build("ns", "seg", a=1)

        assert first == second

    def test_different_inputs_different_keys(self):

        assert CacheKeyBuilder.build("ns", a=1) != CacheKeyBuilder.build(
            "ns",
            a=2,
        )

    def test_prompt_key(self):

        key = CacheKeyBuilder.prompt_key(
            "triage",
            "prompt body",
            version="v1",
        )

        assert isinstance(key, str)

        assert len(key) == 64

    def test_ai_response_key(self):

        key = CacheKeyBuilder.ai_response_key(
            "gemini-2.0-flash",
            "analyze this incident",
        )

        assert isinstance(key, str)

        assert len(key) == 64

    def test_semantic_key(self):

        key = CacheKeyBuilder.semantic_key(
            "abc123",
            threshold_bucket=0.9,
        )

        assert isinstance(key, str)

        assert len(key) == 64
