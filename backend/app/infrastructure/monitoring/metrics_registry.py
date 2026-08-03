from prometheus_client import CollectorRegistry, generate_latest

from app.infrastructure.ai.health.circuit_state import (
    CircuitState,
)

from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)

from app.infrastructure.ai.registry.provider_metadata_registry import (
    ProviderMetadataRegistry,
)

from app.infrastructure.monitoring.prometheus_metrics import (
    PrometheusMetrics,
)


class MetricsRegistry:
    """
    Registers Prometheus metrics into a dedicated collector
    registry and exposes recording helpers.

    Recording helpers are called by the AIRouter after each
    provider attempt. Circuit breaker state is refreshed from
    the ProviderHealthService before each scrape.
    """

    def __init__(
        self,
        prometheus_metrics: PrometheusMetrics | None = None,
        metadata_registry: ProviderMetadataRegistry | None = None,
    ) -> None:

        self.registry = CollectorRegistry()

        self.metrics = prometheus_metrics or PrometheusMetrics(
            registry=self.registry,
        )

        self.metadata_registry = metadata_registry

    # ==========================================================
    # Recording Helpers
    # ==========================================================

    def record_request(
        self,
        provider: str,
    ) -> None:

        self.metrics.ai_requests_total.labels(
            provider=provider,
        ).inc()

    def record_success(
        self,
        provider: str,
        latency_s: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float | None = None,
    ) -> None:

        self.record_request(provider)

        self.metrics.ai_provider_successes_total.labels(
            provider=provider,
        ).inc()

        self.metrics.ai_provider_latency_seconds.labels(
            provider=provider,
        ).observe(latency_s)

        if input_tokens:
            self.metrics.ai_provider_input_tokens_total.labels(
                provider=provider,
            ).inc(input_tokens)

        if output_tokens:
            self.metrics.ai_provider_output_tokens_total.labels(
                provider=provider,
            ).inc(output_tokens)

        if cost_usd is None:
            cost_usd = self._estimate_cost(
                provider,
                input_tokens,
                output_tokens,
            )

        if cost_usd:
            self.metrics.ai_provider_cost_usd_total.labels(
                provider=provider,
            ).inc(cost_usd)

    def record_failure(
        self,
        provider: str,
        latency_s: float,
    ) -> None:

        self.record_request(provider)

        self.metrics.ai_provider_failures_total.labels(
            provider=provider,
        ).inc()

        self.metrics.ai_provider_latency_seconds.labels(
            provider=provider,
        ).observe(latency_s)

    def update_circuit_state(
        self,
        provider: str,
        state: CircuitState,
    ) -> None:

        self.metrics.ai_provider_circuit_state.labels(
            provider=provider,
        ).set(self._circuit_state_value(state))

    def sync_provider_health(
        self,
        health_service: ProviderHealthService,
    ) -> None:

        for health in health_service.get_all():

            self.update_circuit_state(
                health.provider,
                health.circuit_state,
            )

    # ==========================================================
    # Cost Estimation
    # ==========================================================

    def _estimate_cost(
        self,
        provider: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float | None:

        if self.metadata_registry is None:
            return None

        if not self.metadata_registry.exists(provider):
            return None

        metadata = self.metadata_registry.get(provider)

        return metadata.estimated_cost(
            input_tokens,
            output_tokens,
        )

    # ==========================================================
    # Exposition
    # ==========================================================

    def render(self) -> bytes:

        return generate_latest(self.registry)

    @staticmethod
    def _circuit_state_value(
        state: CircuitState,
    ) -> int:

        mapping = {
            CircuitState.CLOSED: 0,
            CircuitState.HALF_OPEN: 1,
            CircuitState.OPEN: 2,
        }

        return mapping.get(state, 0)
