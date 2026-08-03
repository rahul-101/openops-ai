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

from app.infrastructure.ai.metrics.provider_metrics_service import (
    ProviderMetricsService,
)

from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)

from app.infrastructure.ai.routing.routing_policy import (
    RoutingPolicy,
)

from app.infrastructure.monitoring.metrics_registry import (
    MetricsRegistry,
)

from app.infrastructure.cache.semantic_cache import (
    SemanticCache,
)
from app.infrastructure.tracing.tracer import (
    Tracer,
)


class AIRouter(AIService):
    """
    Routes AI requests using the configured routing policy.

    Supports:

    - Intelligent provider failover
    - Provider health monitoring
    - Circuit Breaker
    - Provider metrics collection
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        routing_policy: RoutingPolicy,
        health_service: ProviderHealthService,
        metrics_service: ProviderMetricsService,
        metrics_registry: MetricsRegistry | None = None,
        cache: SemanticCache | None = None,
        tracer: Tracer | None = None,
    ) -> None:

        self.registry = registry
        self.routing_policy = routing_policy
        self.health_service = health_service
        self.metrics_service = metrics_service
        self.metrics_registry = metrics_registry
        self.cache = cache
        self.tracer = tracer

        #
        # Register providers with Health & Metrics
        #

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

        if self.tracer is not None:

            with self.tracer.span(
                "ai.analyze_incident",
                {
                    "request_id": request_id_ctx.get() or "",
                    "title": request.title,
                },
            ) as span:

                return await self._analyze(
                    request,
                    prompt,
                    log,
                    span,
                )

        return await self._analyze(
            request,
            prompt,
            log,
            None,
        )

    async def _analyze(
        self,
        request: IncidentRequest,
        prompt: str,
        log,
        span,
    ) -> AIResponse:

        if self.cache is not None:

            cached = self.cache.get(
                request.title,
                self._embedding_for(request),
            )

            if cached is not None:

                log.info(
                    "AI response served from cache.",
                    request_id=request_id_ctx.get(),
                )

                if span is not None:
                    span.add_event("cache.hit")

                return AIResponse(
                    summary=cached["summary"],
                    severity=cached["severity"],
                    category=cached["category"],
                    probable_cause=cached["probable_cause"],
                    recommendation=cached["recommendation"],
                    confidence=cached["confidence"],
                    provider=cached["provider"],
                    model=cached["model"],
                    input_tokens=cached["input_tokens"],
                    output_tokens=cached["output_tokens"],
                    processing_time_ms=cached["processing_time_ms"],
                )

        providers = (
            self.routing_policy.get_provider_priority()
        )

        last_exception = None

        for provider_name in providers:

            health = self.health_service.get_health(
                provider_name
            )

            #
            # Circuit Breaker / Health Check
            #

            if not self.health_service.is_healthy(
                provider_name
            ):

                log.warning(
                    "Skipping AI provider.",
                    provider=provider_name,
                    health_status=health.status,
                    circuit_state=health.circuit_state.value,
                    retry_after=(
                        health.retry_after.isoformat()
                        if health.retry_after
                        else None
                    ),
                )

                continue

            provider = self.registry.get(
                provider_name
            )

            log.info(
                "Trying AI provider",
                provider=provider_name,
                circuit_state=health.circuit_state.value,
            )

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

                if self.metrics_registry is not None:

                    self.metrics_registry.record_success(
                        provider=provider_name,
                        latency_s=elapsed_ms / 1000,
                        input_tokens=response.input_tokens,
                        output_tokens=response.output_tokens,
                    )

                updated_health = (
                    self.health_service.get_health(
                        provider_name
                    )
                )

                log.info(
                    "AI provider succeeded",
                    provider=provider_name,
                    response_time_ms=round(
                        elapsed_ms,
                        2,
                    ),
                    circuit_state=updated_health.circuit_state.value,
                )

                if self.cache is not None:

                    self.cache.set(
                        request.title,
                        self._embedding_for(request),
                        {
                            "summary": response.summary,
                            "severity": response.severity,
                            "category": response.category,
                            "probable_cause": response.probable_cause,
                            "recommendation": response.recommendation,
                            "confidence": response.confidence,
                            "provider": response.provider,
                            "model": response.model,
                            "input_tokens": response.input_tokens,
                            "output_tokens": response.output_tokens,
                            "processing_time_ms": response.processing_time_ms,
                        },
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

                if self.metrics_registry is not None:

                    self.metrics_registry.record_failure(
                        provider=provider_name,
                        latency_s=elapsed_ms / 1000,
                    )

                updated_health = (
                    self.health_service.get_health(
                        provider_name
                    )
                )

                log.warning(
                    "Retryable provider failure. Trying next provider.",
                    provider=provider_name,
                    error=str(ex),
                    response_time_ms=round(
                        elapsed_ms,
                        2,
                    ),
                    circuit_state=updated_health.circuit_state.value,
                    consecutive_failures=updated_health.consecutive_failures,
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

                if self.metrics_registry is not None:

                    self.metrics_registry.record_failure(
                        provider=provider_name,
                        latency_s=elapsed_ms / 1000,
                    )

                updated_health = (
                    self.health_service.get_health(
                        provider_name
                    )
                )

                log.error(
                    "Non-retryable provider failure.",
                    provider=provider_name,
                    error=str(ex),
                    response_time_ms=round(
                        elapsed_ms,
                        2,
                    ),
                    circuit_state=updated_health.circuit_state.value,
                    consecutive_failures=updated_health.consecutive_failures,
                )

                raise

        log.error(
            "All AI providers failed.",
        )

        raise RuntimeError(
            "All registered AI providers failed to process the request."
        ) from last_exception

    @staticmethod
    def _embedding_for(
        request: IncidentRequest,
    ) -> list[float]:
        """
        Produces a lightweight, deterministic signature vector
        for the request used as a semantic-cache lookup key.
        """

        raw = f"{request.title} {request.description}".strip()

        vector = [0.0] * 32

        for token in raw.lower().split():

            index = sum(ord(char) for char in token) % 32

            vector[index] += 1.0

        norm = sum(value * value for value in vector) ** 0.5 or 1.0

        return [value / norm for value in vector]
