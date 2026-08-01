from __future__ import annotations

from datetime import datetime
from threading import Lock

from app.infrastructure.ai.metrics.provider_metrics import (
    ProviderMetrics,
)


class ProviderMetricsService:
    """
    Tracks runtime metrics for all registered AI providers.

    Metrics collected by this service are intended for:

    - Observability
    - Dashboards
    - Performance analysis
    - Cost-aware routing
    - Future intelligent routing decisions

    This service is intentionally stateful and lives in memory.
    """

    def __init__(self):

        self._providers: dict[str, ProviderMetrics] = {}

        self._lock = Lock()


    # ==========================================================
    # Provider Registration
    # ==========================================================

    def register_provider(
        self,
        provider_name: str,
    ) -> None:

        with self._lock:

            if provider_name not in self._providers:

                self._providers[
                    provider_name
                ] = ProviderMetrics(
                    provider=provider_name,
                )


    # ==========================================================
    # Successful Request
    # ==========================================================

    def mark_success(
        self,
        provider_name: str,
        response_time_ms: float,
    ) -> None:

        with self._lock:

            provider = self._providers[
                provider_name
            ]

            provider.total_requests += 1

            provider.successful_requests += 1

            provider.total_response_time_ms += (
                response_time_ms
            )

            provider.last_response_time_ms = (
                response_time_ms
            )

            provider.average_response_time_ms = (
                provider.total_response_time_ms
                /
                provider.successful_requests
            )

            provider.updated_at = datetime.utcnow()

            provider.last_error = None


    # ==========================================================
    # Failed Request
    # ==========================================================

    def mark_failure(
        self,
        provider_name: str,
        response_time_ms: float,
        error: Exception,
    ) -> None:

        with self._lock:

            provider = self._providers[
                provider_name
            ]

            provider.total_requests += 1

            provider.failed_requests += 1

            provider.last_response_time_ms = (
                response_time_ms
            )

            provider.last_error = str(error)

            provider.updated_at = datetime.utcnow()


    # ==========================================================
    # Accessors
    # ==========================================================

    def get_metrics(
        self,
        provider_name: str,
    ) -> ProviderMetrics:

        return self._providers[
            provider_name
        ]


    def get_all(
        self,
    ) -> list[ProviderMetrics]:

        return list(
            self._providers.values()
        )