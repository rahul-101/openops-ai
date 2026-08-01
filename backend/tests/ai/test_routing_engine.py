from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)

from app.infrastructure.ai.metrics.provider_metrics_service import (
    ProviderMetricsService,
)

from app.infrastructure.ai.registry.provider_metadata import (
    ProviderCapability,
    ProviderMetadata,
)

from app.infrastructure.ai.registry.provider_metadata_registry import (
    ProviderMetadataRegistry,
)

from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)

from app.infrastructure.ai.routing.provider_scorer import (
    ProviderScorer,
)

from app.infrastructure.ai.routing.routing_engine import (
    RoutingEngine,
)


def create_engine() -> RoutingEngine:

    registry = ProviderRegistry()

    registry.register(
        "gemini",
        object(),
    )

    registry.register(
        "openrouter",
        object(),
    )

    metadata = ProviderMetadataRegistry()

    metadata.register(
        ProviderMetadata(
            name="gemini",
            display_name="Gemini",
            model="gemini",
            priority=1,
            input_cost_per_1k_tokens=0.1,
            output_cost_per_1k_tokens=0.2,
            max_context_tokens=1_000_000,
            capabilities=frozenset(
                {
                    ProviderCapability.TEXT_GENERATION,
                }
            ),
        )
    )

    metadata.register(
        ProviderMetadata(
            name="openrouter",
            display_name="OpenRouter",
            model="deepseek",
            priority=2,
            input_cost_per_1k_tokens=1,
            output_cost_per_1k_tokens=2,
            max_context_tokens=8192,
            capabilities=frozenset(
                {
                    ProviderCapability.TEXT_GENERATION,
                }
            ),
        )
    )

    health = ProviderHealthService()

    metrics = ProviderMetricsService()

    scorer = ProviderScorer(
        metadata_registry=metadata,
    )

    for provider in registry.list():

        health.register_provider(
            provider,
        )

        metrics.register_provider(
            provider,
        )

    return RoutingEngine(
        registry=registry,
        health_service=health,
        metrics_service=metrics,
        scorer=scorer,
    )


# ==========================================================
# Default Ranking
# ==========================================================


def test_rank_default():

    engine = create_engine()

    ranked = engine.rank_providers()

    assert ranked == [
        "gemini",
        "openrouter",
    ]


# ==========================================================
# Skip Unhealthy Provider
# ==========================================================


def test_skip_unhealthy_provider():

    engine = create_engine()

    for _ in range(
        engine.health_service.FAILURE_THRESHOLD
    ):

        engine.health_service.mark_failure(
            "gemini",
            Exception("Failure"),
        )

    ranked = engine.rank_providers()

    assert ranked == [
        "openrouter",
    ]


# ==========================================================
# Better Latency Wins
# ==========================================================


def test_latency_affects_ranking():

    engine = create_engine()

    engine.metrics_service.mark_success(
        "gemini",
        100,
    )

    engine.metrics_service.mark_success(
        "openrouter",
        800,
    )

    ranked = engine.rank_providers()

    assert ranked[0] == "gemini"


# ==========================================================
# Failure Rate Affects Ranking
# ==========================================================


def test_failure_rate_affects_ranking():

    engine = create_engine()

    for _ in range(20):

        engine.metrics_service.mark_success(
            "gemini",
            100,
        )

    for _ in range(10):

        engine.metrics_service.mark_success(
            "openrouter",
            100,
        )

    for _ in range(10):

        engine.metrics_service.mark_failure(
            "openrouter",
            100,
            Exception("Failure"),
        )

    ranked = engine.rank_providers()

    assert ranked[0] == "gemini"


# ==========================================================
# Empty Registry
# ==========================================================


def test_empty_registry():

    registry = ProviderRegistry()

    metadata = ProviderMetadataRegistry()

    scorer = ProviderScorer(
        metadata_registry=metadata,
    )

    health = ProviderHealthService()

    metrics = ProviderMetricsService()

    engine = RoutingEngine(
        registry=registry,
        health_service=health,
        metrics_service=metrics,
        scorer=scorer,
    )

    assert engine.rank_providers() == []