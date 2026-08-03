from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderScore:
    """
    Represents the routing score calculated for a provider.

    Lower scores indicate a better provider.

    The score is composed of multiple weighted factors
    such as latency, reliability, cost, and configured
    priority.
    """

    provider: str

    # ==========================================================
    # Individual Factors
    # ==========================================================

    latency_score: float

    reliability_score: float

    cost_score: float

    priority_score: float

    # ==========================================================
    # Final Weighted Score
    # ==========================================================

    overall_score: float
