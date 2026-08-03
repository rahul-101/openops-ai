from app.infrastructure.cache.cache_key_builder import (
    CacheKeyBuilder,
)
from app.infrastructure.cache.cache_service import (
    CacheService,
)


class PromptCache:
    """
    Version-aware cache for resolved prompts.

    Keys are derived from the prompt name, version and the
    raw prompt text so that edits invalidate the cache
    automatically.
    """

    def __init__(
        self,
        cache: CacheService,
        default_ttl_seconds: int = 3600,
    ) -> None:

        self._cache = cache

        self._default_ttl_seconds = default_ttl_seconds

    def get(
        self,
        prompt_name: str,
        prompt_text: str,
        version: str | None = None,
    ) -> object | None:

        key = CacheKeyBuilder.prompt_key(
            prompt_name,
            prompt_text,
            version=version,
        )

        return self._cache.get(key)

    def set(
        self,
        prompt_name: str,
        prompt_text: str,
        rendered: object,
        version: str | None = None,
        ttl_seconds: int | None = None,
    ) -> str:

        key = CacheKeyBuilder.prompt_key(
            prompt_name,
            prompt_text,
            version=version,
        )

        self._cache.set(
            key,
            rendered,
            ttl_seconds=(
                ttl_seconds
                if ttl_seconds is not None
                else self._default_ttl_seconds
            ),
        )

        return key

    def invalidate(
        self,
        prompt_name: str,
        version: str | None = None,
    ) -> None:
        """
        Best-effort invalidation. Because keys are content
        hashed, exact-match removal is not possible without
        scanning; callers should instead rely on prompt-text
        changes producing new keys.
        """

        return None
