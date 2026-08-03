"""
Distributed caching layer.

Provides a unified CacheService contract with in-memory and
Redis-backed implementations, semantic (embedding-keyed) caching
for AI responses, version-aware prompt caching, and deterministic
cache key generation.
"""

from app.infrastructure.cache.cache_key_builder import (
    CacheKeyBuilder,
)
from app.infrastructure.cache.cache_service import (
    CacheService,
    InMemoryCacheService,
)
from app.infrastructure.cache.prompt_cache import (
    PromptCache,
)
from app.infrastructure.cache.redis_cache import (
    RedisCacheService,
)
from app.infrastructure.cache.semantic_cache import (
    SemanticCache,
)

__all__ = [
    "CacheKeyBuilder",
    "CacheService",
    "InMemoryCacheService",
    "PromptCache",
    "RedisCacheService",
    "SemanticCache",
]
