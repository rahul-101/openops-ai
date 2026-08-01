from unittest.mock import AsyncMock

import pytest

from app.application.dto.requests.incident_request import (
    IncidentRequest,
)
from app.application.dto.responses.ai_response import (
    AIResponse,
)
from app.infrastructure.ai.exceptions import (
    NonRetryableProviderError,
    RetryableProviderError,
)
from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)
from app.infrastructure.ai.metrics.provider_metrics_service import (
    ProviderMetricsService,
)
from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)
from app.infrastructure.ai.router.ai_router import (
    AIRouter,
)
from app.infrastructure.ai.routing.routing_policy import (
    RoutingPolicy,
)


class FakeRoutingPolicy(RoutingPolicy):

    def get_provider_priority(
        self,
    ) -> list[str]:

        return [
            "gemini",
            "openrouter",
        ]


def create_ai_response(
    provider: str,
) -> AIResponse:

    return AIResponse(
        summary="summary",
        severity="High",
        category="Database",
        probable_cause="Timeout",
        recommendation="Restart",
        confidence=0.95,
        provider=provider,
        model="model",
    )


@pytest.fixture
def router():

    registry = ProviderRegistry()

    gemini = AsyncMock()

    openrouter = AsyncMock()

    registry.register(
        "gemini",
        gemini,
    )

    registry.register(
        "openrouter",
        openrouter,
    )

    health = ProviderHealthService()

    metrics = ProviderMetricsService()

    policy = FakeRoutingPolicy()

    router = AIRouter(
        registry=registry,
        routing_policy=policy,
        health_service=health,
        metrics_service=metrics,
    )

    return (
        router,
        gemini,
        openrouter,
        health,
        metrics,
    )


@pytest.fixture
def incident():

    return IncidentRequest(
        title="DB Issue",
        description="Database timeout",
        severity="High",
    )


# ==========================================================
# Primary Provider Success
# ==========================================================


@pytest.mark.asyncio
async def test_primary_provider_success(
    router,
    incident,
):

    router_obj, gemini, _, _, _ = router

    gemini.analyze_incident.return_value = (
        create_ai_response(
            "gemini",
        )
    )

    response = await router_obj.analyze_incident(
        incident,
        "prompt",
    )

    assert response.provider == "gemini"

    gemini.analyze_incident.assert_awaited_once()


# ==========================================================
# Failover
# ==========================================================


@pytest.mark.asyncio
async def test_failover_to_second_provider(
    router,
    incident,
):

    (
        router_obj,
        gemini,
        openrouter,
        _,
        _,
    ) = router

    gemini.analyze_incident.side_effect = (
        RetryableProviderError(
            "timeout",
        )
    )

    openrouter.analyze_incident.return_value = (
        create_ai_response(
            "openrouter",
        )
    )

    response = await router_obj.analyze_incident(
        incident,
        "prompt",
    )

    assert (
        response.provider
        == "openrouter"
    )


# ==========================================================
# Non Retryable
# ==========================================================


@pytest.mark.asyncio
async def test_non_retryable_exception(
    router,
    incident,
):

    (
        router_obj,
        gemini,
        _,
        _,
        _,
    ) = router

    gemini.analyze_incident.side_effect = (
        NonRetryableProviderError(
            "invalid",
        )
    )

    with pytest.raises(
        NonRetryableProviderError,
    ):

        await router_obj.analyze_incident(
            incident,
            "prompt",
        )


# ==========================================================
# Open Circuit
# ==========================================================


@pytest.mark.asyncio
async def test_skip_open_circuit(
    router,
    incident,
):

    (
        router_obj,
        gemini,
        openrouter,
        health,
        _,
    ) = router

    for _ in range(
        health.FAILURE_THRESHOLD
    ):

        health.mark_failure(
            "gemini",
            Exception("Failure"),
        )

    openrouter.analyze_incident.return_value = (
        create_ai_response(
            "openrouter",
        )
    )

    response = await router_obj.analyze_incident(
        incident,
        "prompt",
    )

    assert (
        response.provider
        == "openrouter"
    )

    gemini.analyze_incident.assert_not_called()


# ==========================================================
# Metrics Updated
# ==========================================================


@pytest.mark.asyncio
async def test_metrics_updated_after_success(
    router,
    incident,
):

    (
        router_obj,
        gemini,
        _,
        _,
        metrics,
    ) = router

    gemini.analyze_incident.return_value = (
        create_ai_response(
            "gemini",
        )
    )

    await router_obj.analyze_incident(
        incident,
        "prompt",
    )

    provider_metrics = (
        metrics.get_metrics(
            "gemini",
        )
    )

    assert (
        provider_metrics.total_requests
        == 1
    )

    assert (
        provider_metrics.successful_requests
        == 1
    )


# ==========================================================
# Health Updated
# ==========================================================


@pytest.mark.asyncio
async def test_health_updated_after_success(
    router,
    incident,
):

    (
        router_obj,
        gemini,
        _,
        health,
        _,
    ) = router

    gemini.analyze_incident.return_value = (
        create_ai_response(
            "gemini",
        )
    )

    await router_obj.analyze_incident(
        incident,
        "prompt",
    )

    provider = health.get_health(
        "gemini",
    )

    assert (
        provider.consecutive_successes
        == 1
    )

    assert (
        provider.consecutive_failures
        == 0
    )