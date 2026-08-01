from app.infrastructure.ai.metrics.provider_metrics import (
    ProviderMetrics,
)
from app.infrastructure.ai.registry.provider_metadata_registry import (
    ProviderMetadataRegistry,
)
from app.infrastructure.ai.routing.provider_score import (
    ProviderScore,
)


class ProviderScorer:
    """
    Calculates an adaptive routing score for an AI provider.

    Lower scores are better.

    The scoring model combines multiple weighted
    characteristics of a provider.

    Cost and priority are read from the
    ProviderMetadataRegistry, making routing decisions
    cost-aware without hardcoded provider data.

    Future versions can easily incorporate:

    - Region
    - Context window
    - Model capability
    - GPU utilization
    - User preferences

    without changing the routing policy.
    """

    # ==========================================================
    # Default Weights
    # ==========================================================

    LATENCY_WEIGHT = 0.40

    RELIABILITY_WEIGHT = 0.35

    COST_WEIGHT = 0.15

    PRIORITY_WEIGHT = 0.10

    # ==========================================================
    # Fallbacks
    #
    # Used when a provider has no registered metadata.
    # High values push unknown providers to the back.
    # ==========================================================

    DEFAULT_COST_SCORE = 5.0

    DEFAULT_PRIORITY_SCORE = 99.0

    # ==========================================================
    # Cost Normalization
    #
    # Reference blended cost (USD per 1K tokens) used to
    # normalize provider cost into a comparable score range.
    # ==========================================================

    COST_REFERENCE_PER_1K_TOKENS = 0.01

    def __init__(
        self,
        metadata_registry: ProviderMetadataRegistry,
    ) -> None:

        self.metadata_registry = metadata_registry

    def calculate(
        self,
        metrics: ProviderMetrics,
    ) -> ProviderScore:
        """
        Calculates the adaptive routing score
        for a provider.
        """

        # ------------------------------------------------------
        # Latency
        # ------------------------------------------------------

        latency_score = (
            metrics.average_response_time_ms
            / 1000
        )

        # ------------------------------------------------------
        # Reliability
        #
        # Failure rate contributes directly.
        # ------------------------------------------------------

        reliability_score = (
            metrics.failure_rate
            / 100
        )

        # ------------------------------------------------------
        # Cost (metadata-driven)
        # ------------------------------------------------------

        cost_score = self._calculate_cost_score(
            metrics.provider,
        )

        # ------------------------------------------------------
        # Priority (metadata-driven)
        # ------------------------------------------------------

        priority_score = self._calculate_priority_score(
            metrics.provider,
        )

        # ------------------------------------------------------
        # Weighted Score
        # ------------------------------------------------------

        overall_score = (

            latency_score
            * self.LATENCY_WEIGHT

            +

            reliability_score
            * self.RELIABILITY_WEIGHT

            +

            cost_score
            * self.COST_WEIGHT

            +

            priority_score
            * self.PRIORITY_WEIGHT

        )

        return ProviderScore(
            provider=metrics.provider,

            latency_score=latency_score,

            reliability_score=reliability_score,

            cost_score=cost_score,

            priority_score=priority_score,

            overall_score=overall_score,
        )

    # ==========================================================
    # Internal Scoring Helpers
    # ==========================================================

    def _calculate_cost_score(
        self,
        provider: str,
    ) -> float:
        """
        Derives a relative cost score from provider metadata.

        The blended per-token cost is normalized against a
        reference cost so that providers remain comparable
        regardless of absolute pricing.
        """

        if not self.metadata_registry.exists(provider):
            return self.DEFAULT_COST_SCORE

        metadata = self.metadata_registry.get(provider)

        return (
            metadata.blended_cost_per_1k_tokens()
            / self.COST_REFERENCE_PER_1K_TOKENS
        )

    def _calculate_priority_score(
        self,
        provider: str,
    ) -> float:
        """
        Derives the priority score from provider metadata.

        Lower number = higher priority.
        """

        if not self.metadata_registry.exists(provider):
            return self.DEFAULT_PRIORITY_SCORE

        return float(
            self.metadata_registry.get(provider).priority
        )
