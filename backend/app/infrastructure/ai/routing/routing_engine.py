from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)
from app.infrastructure.ai.metrics.provider_metrics_service import (
    ProviderMetricsService,
)
from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)
from app.infrastructure.ai.routing.provider_scorer import (
    ProviderScorer,
)


class RoutingEngine:
    """
    Intelligent routing engine responsible for ranking providers.

    Responsibilities
    ----------------
    - Read all registered providers
    - Skip unhealthy providers
    - Read provider metrics
    - Calculate provider scores
    - Return providers ordered by score
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        health_service: ProviderHealthService,
        metrics_service: ProviderMetricsService,
        scorer: ProviderScorer,
    ) -> None:

        self.registry = registry
        self.health_service = health_service
        self.metrics_service = metrics_service
        self.scorer = scorer

    def rank_providers(
        self,
    ) -> list[str]:
        """
        Returns providers ordered by their routing score.

        Lower score means better provider.
        """

        provider_scores = []

        for provider_name in self.registry.list():

            # =====================================================
            # Skip unhealthy providers
            # =====================================================

            if not self.health_service.is_healthy(
                provider_name,
            ):
                continue

            metrics = self.metrics_service.get_metrics(
                provider_name,
            )

            score = self.scorer.calculate(
                metrics,
            )

            provider_scores.append(score)

        provider_scores.sort(
            key=lambda provider: provider.overall_score
        )

        return [
            provider.provider
            for provider in provider_scores
        ]