import pytest

from app.infrastructure.ai.metrics.provider_metrics import (
    ProviderMetrics,
)

from app.infrastructure.ai.registry.provider_metadata import (
    ProviderCapability,
    ProviderMetadata,
)

from app.infrastructure.ai.registry.provider_metadata_registry import (
    ProviderMetadataRegistry,
)

from app.infrastructure.ai.routing.provider_scorer import (
    ProviderScorer,
)


@pytest.fixture
def metadata_registry() -> ProviderMetadataRegistry:

    registry = ProviderMetadataRegistry()

    registry.register(
        ProviderMetadata(
            name="gemini",
            display_name="Gemini",
            model="gemini-2.5-flash",
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

    registry.register(
        ProviderMetadata(
            name="openrouter",
            display_name="OpenRouter",
            model="deepseek-chat",
            priority=2,
            input_cost_per_1k_tokens=1.0,
            output_cost_per_1k_tokens=1.5,
            max_context_tokens=8192,
            capabilities=frozenset(
                {
                    ProviderCapability.TEXT_GENERATION,
                }
            ),
        )
    )

    return registry


@pytest.fixture
def scorer(
    metadata_registry: ProviderMetadataRegistry,
) -> ProviderScorer:

    return ProviderScorer(
        metadata_registry=metadata_registry,
    )


# ==========================================================
# Basic Score
# ==========================================================


def test_calculate_score(
    scorer: ProviderScorer,
):

    metrics = ProviderMetrics(
        provider="gemini",
        total_requests=100,
        successful_requests=99,
        failed_requests=1,
        average_response_time_ms=400,
        last_response_time_ms=420,
    )

    score = scorer.calculate(metrics)

    assert score.provider == "gemini"

    assert score.overall_score > 0


# ==========================================================
# Better Latency
# ==========================================================


def test_lower_latency_produces_lower_score(
    scorer: ProviderScorer,
):

    fast = ProviderMetrics(
        provider="gemini",
        average_response_time_ms=200,
    )

    slow = ProviderMetrics(
        provider="gemini",
        average_response_time_ms=1200,
    )

    fast_score = scorer.calculate(
        fast,
    )

    slow_score = scorer.calculate(
        slow,
    )

    assert (
        fast_score.overall_score
        <
        slow_score.overall_score
    )


# ==========================================================
# Failure Rate
# ==========================================================


def test_failure_rate_affects_score(
    scorer: ProviderScorer,
):

    healthy = ProviderMetrics(
        provider="gemini",
        total_requests=100,
        successful_requests=99,
        failed_requests=1,
    )

    unhealthy = ProviderMetrics(
        provider="gemini",
        total_requests=100,
        successful_requests=40,
        failed_requests=60,
    )

    healthy_score = scorer.calculate(
        healthy,
    )

    unhealthy_score = scorer.calculate(
        unhealthy,
    )

    assert (
        healthy_score.overall_score
        <
        unhealthy_score.overall_score
    )


# ==========================================================
# Provider Cost
# ==========================================================


def test_cost_affects_score(
    scorer: ProviderScorer,
):

    gemini = ProviderMetrics(
        provider="gemini",
    )

    openrouter = ProviderMetrics(
        provider="openrouter",
    )

    gemini_score = scorer.calculate(
        gemini,
    )

    openrouter_score = scorer.calculate(
        openrouter,
    )

    assert (
        gemini_score.cost_score
        <
        openrouter_score.cost_score
    )


# ==========================================================
# Priority
# ==========================================================


def test_priority_affects_score(
    scorer: ProviderScorer,
):

    gemini = ProviderMetrics(
        provider="gemini",
    )

    openrouter = ProviderMetrics(
        provider="openrouter",
    )

    gemini_score = scorer.calculate(
        gemini,
    )

    openrouter_score = scorer.calculate(
        openrouter,
    )

    assert (
        gemini_score.priority_score
        <
        openrouter_score.priority_score
    )


# ==========================================================
# Metadata
# ==========================================================


def test_provider_metadata_loaded(
    metadata_registry: ProviderMetadataRegistry,
):

    metadata = metadata_registry.get(
        "gemini",
    )

    assert metadata.name == "gemini"

    assert metadata.priority == 1

    assert (
        metadata.max_context_tokens
        == 1_000_000
    )


# ==========================================================
# Unknown Provider
# ==========================================================


def test_unknown_provider_score(
    scorer: ProviderScorer,
):

    metrics = ProviderMetrics(
        provider="unknown",
    )

    score = scorer.calculate(
        metrics,
    )

    assert score.provider == "unknown"

    assert score.overall_score > 0
