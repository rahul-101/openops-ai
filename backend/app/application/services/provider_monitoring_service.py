from app.application.dto.responses.provider_health_response import (
    ProviderHealthResponse,
)

from app.application.dto.responses.provider_metrics_response import (
    ProviderMetricsResponse,
)

from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)

from app.infrastructure.ai.metrics.provider_metrics_service import (
    ProviderMetricsService,
)


class ProviderMonitoringService:
    """
    Application service responsible for exposing AI provider
    health and runtime metrics.

    Converts infrastructure models into API response DTOs.
    """

    def __init__(
        self,
        health_service: ProviderHealthService,
        metrics_service: ProviderMetricsService,
    ) -> None:

        self.health_service = health_service
        self.metrics_service = metrics_service


    # ======================================================
    # Provider Health
    # ======================================================

    def get_provider_health(
        self,
    ) -> list[ProviderHealthResponse]:

        providers = []

        for health in self.health_service.get_all():

            providers.append(
                ProviderHealthResponse(
                    provider=health.provider,
                    status=health.status,
                    circuit_state=(
                        health.circuit_state.value
                    ),
                    consecutive_failures=(
                        health.consecutive_failures
                    ),
                    consecutive_successes=(
                        health.consecutive_successes
                    ),
                    last_success=health.last_success,
                    last_failure=health.last_failure,
                    retry_after=health.retry_after,
                    last_error=health.last_error,
                    updated_at=health.updated_at,
                )
            )

        return providers


    # ======================================================
    # Provider Metrics
    # ======================================================

    def get_provider_metrics(
        self,
    ) -> list[ProviderMetricsResponse]:

        providers = []

        for metrics in self.metrics_service.get_all():

            providers.append(
                ProviderMetricsResponse(
                    provider=metrics.provider,

                    total_requests=(
                        metrics.total_requests
                    ),

                    successful_requests=(
                        metrics.successful_requests
                    ),

                    failed_requests=(
                        metrics.failed_requests
                    ),

                    success_rate=(
                        metrics.success_rate
                    ),

                    failure_rate=(
                        metrics.failure_rate
                    ),

                    average_response_time_ms=(
                        metrics.average_response_time_ms
                    ),

                    last_response_time_ms=(
                        metrics.last_response_time_ms
                    ),

                    last_error=(
                        metrics.last_error
                    ),

                    updated_at=(
                        metrics.updated_at.isoformat()
                    ),
                )
            )

        return providers
