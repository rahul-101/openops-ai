from time import perf_counter

from app.application.dto.requests.incident_request import IncidentRequest
from app.application.dto.responses.ai_response import AIResponse
from app.application.interfaces.ai_service import AIService

from app.core.logging import logger
from app.core.request_context import request_id_ctx

from app.infrastructure.ai.exceptions import (
    NonRetryableProviderError,
    RetryableProviderError,
)

from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)

# ==========================================================
# NEW: Metrics
# ==========================================================
from app.infrastructure.ai.metrics.provider_metrics_service import (
    ProviderMetricsService,
)

from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)

from app.infrastructure.ai.routing.routing_policy import (
    RoutingPolicy,
)


class AIRouter(AIService):
    """
    Routes AI requests using the configured routing policy.

    Supports:

    - Intelligent provider failover
    - Provider health monitoring
    - Provider metrics collection
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        routing_policy: RoutingPolicy,
        health_service: ProviderHealthService,

        # ==========================================================
        # NEW: Metrics Service
        # ==========================================================
        metrics_service: ProviderMetricsService,
    ) -> None:

        self.registry = registry
        self.routing_policy = routing_policy
        self.health_service = health_service
        self.metrics_service = metrics_service

        # ==========================================================
        # Register providers with Health & Metrics
        # ==========================================================

        for provider_name in registry.list():

            self.health_service.register_provider(
                provider_name
            )

            self.metrics_service.register_provider(
                provider_name
            )

    async def analyze_incident(
        self,
        request: IncidentRequest,
        prompt: str,
    ) -> AIResponse:

        log = logger.bind(
            request_id=request_id_ctx.get(),
        )

        providers = (
            self.routing_policy.get_provider_priority()
        )

        last_exception = None

        for provider_name in providers:

            # ------------------------------------------------------
            # Skip unhealthy providers
            # ------------------------------------------------------

            if not self.health_service.is_healthy(
                provider_name
            ):

                log.warning(
                    "Skipping unhealthy AI provider.",
                    provider=provider_name,
                )

                continue

            provider = self.registry.get(
                provider_name
            )

            log.info(
                "Trying AI provider",
                provider=provider_name,
            )

            # ======================================================
            # NEW: Measure Provider Latency
            # ======================================================

            start_time = perf_counter()

            try:

                response = await provider.analyze_incident(
                    request=request,
                    prompt=prompt,
                )

                elapsed_ms = (
                    perf_counter() - start_time
                ) * 1000

                self.health_service.mark_success(
                    provider_name
                )

                self.metrics_service.mark_success(
                    provider_name=provider_name,
                    response_time_ms=elapsed_ms,
                )

                log.info(
                    "AI provider succeeded",
                    provider=provider_name,
                    response_time_ms=round(
                        elapsed_ms,
                        2,
                    ),
                )

                return response

            except RetryableProviderError as ex:

                elapsed_ms = (
                    perf_counter() - start_time
                ) * 1000

                last_exception = ex

                self.health_service.mark_failure(
                    provider_name,
                    ex,
                )

                self.metrics_service.mark_failure(
                    provider_name=provider_name,
                    response_time_ms=elapsed_ms,
                    error=ex,
                )

                log.warning(
                    "Retryable provider failure. Trying next provider.",
                    provider=provider_name,
                    error=str(ex),
                    response_time_ms=round(
                        elapsed_ms,
                        2,
                    ),
                )

                continue

            except NonRetryableProviderError as ex:

                elapsed_ms = (
                    perf_counter() - start_time
                ) * 1000

                self.health_service.mark_failure(
                    provider_name,
                    ex,
                )

                self.metrics_service.mark_failure(
                    provider_name=provider_name,
                    response_time_ms=elapsed_ms,
                    error=ex,
                )

                log.error(
                    "Non-retryable provider failure.",
                    provider=provider_name,
                    error=str(ex),
                    response_time_ms=round(
                        elapsed_ms,
                        2,
                    ),
                )

                raise

        log.error(
            "All AI providers failed.",
        )

        raise RuntimeError(
            "All registered AI providers failed to process the request."
        ) from last_exception