from app.infrastructure.ai.metrics.provider_metrics import (
    ProviderMetrics,
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

    Future versions can easily incorporate:

    - Token cost
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
    # Provider Cost
    #
    # Relative cost score.
    # Lower is cheaper.
    # ==========================================================

    PROVIDER_COST = {
        "gemini": 1.0,
        "openrouter": 2.0,
    }

    # ==========================================================
    # Priority Score
    #
    # Lower number = higher priority.
    # ==========================================================

    PROVIDER_PRIORITY = {
        "gemini": 1.0,
        "openrouter": 2.0,
    }

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
        # Cost
        # ------------------------------------------------------

        cost_score = self.PROVIDER_COST.get(
            metrics.provider,
            5.0,
        )

        # ------------------------------------------------------
        # Priority
        # ------------------------------------------------------

        priority_score = self.PROVIDER_PRIORITY.get(
            metrics.provider,
            99.0,
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