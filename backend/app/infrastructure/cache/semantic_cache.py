import hashlib
import json

from app.infrastructure.cache.cache_key_builder import (
    CacheKeyBuilder,
)
from app.infrastructure.cache.cache_service import (
    CacheService,
)


class SemanticCache:
    """
    Embedding-keyed cache for AI responses.

    Stores responses keyed by a hash of the input embedding
    plus a similarity threshold bucket, so semantically similar
    queries can reuse cached results without re-invoking the
    model.
    """

    def __init__(
        self,
        cache: CacheService,
        similarity_threshold: float = 0.9,
        max_entries: int = 1000,
    ) -> None:

        self._cache = cache

        self._similarity_threshold = similarity_threshold

        self._entries: dict[str, list[float]] = {}

        self._max_entries = max_entries

    def get(
        self,
        query: str,
        embedding: list[float],
    ) -> object | None:
        """
        Returns a cached result when a stored embedding is
        similar enough to the query embedding.
        """

        bucket = self._bucket()

        key = CacheKeyBuilder.semantic_key(
            embedding_hash=self._hash(embedding),
            threshold_bucket=bucket,
        )

        cached = self._cache.get(key)

        if cached is not None:
            return cached

        return self._find_similar(
            embedding,
            bucket,
        )

    def set(
        self,
        query: str,
        embedding: list[float],
        result: object,
    ) -> str:
        """
        Stores a result under the query's embedding.
        """

        key = CacheKeyBuilder.semantic_key(
            embedding_hash=self._hash(embedding),
            threshold_bucket=self._bucket(),
        )

        self._cache.set(key, result)

        self._entries[key] = embedding

        self._trim()

        return key

    def size(self) -> int:

        return len(self._entries)

    def clear(self) -> None:

        self._cache.clear()

        self._entries.clear()

    # ==========================================================
    # Helpers
    # ==========================================================

    def _find_similar(
        self,
        embedding: list[float],
        bucket: float,
    ) -> object | None:

        for key, stored in self._entries.items():

            if self._similarity(embedding, stored) >= bucket:

                return self._cache.get(key)

        return None

    @staticmethod
    def _similarity(
        first: list[float],
        second: list[float],
    ) -> float:

        if not first or len(first) != len(second):
            return 0.0

        dot = sum(
            a * b
            for a, b in zip(first, second)
        )

        norm_a = sum(a * a for a in first) ** 0.5

        norm_b = sum(b * b for b in second) ** 0.5

        if not norm_a or not norm_b:
            return 0.0

        return dot / (norm_a * norm_b)

    def _bucket(self) -> float:

        return round(
            self._similarity_threshold,
            2,
        )

    @staticmethod
    def _hash(
        embedding: list[float],
    ) -> str:

        raw = json.dumps(
            embedding,
            sort_keys=True,
        )

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()[:16]

    def _trim(self) -> None:

        if len(self._entries) <= self._max_entries:
            return

        overflow = (
            len(self._entries) - self._max_entries
        )

        for key in list(self._entries)[:overflow]:
            self._entries.pop(key, None)

            self._cache.delete(key)
