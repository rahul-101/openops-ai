from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)

from app.infrastructure.ai.metrics.provider_metrics_service import (
    ProviderMetricsService,
)

from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)


class ProviderBootstrap:
    """
    Registers all AI providers with Health & Metrics services
    during application startup.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        health_service: ProviderHealthService,
        metrics_service: ProviderMetricsService,
    ) -> None:

        self.registry = registry
        self.health_service = health_service
        self.metrics_service = metrics_service

    def run(self) -> None:

        for provider_name in self.registry.list():

            self.health_service.register_provider(
                provider_name
            )

            self.metrics_service.register_provider(
                provider_name
            )
