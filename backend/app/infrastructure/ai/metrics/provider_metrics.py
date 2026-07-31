from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProviderMetrics:
    """
    Runtime metrics collected for an AI provider.

    These metrics are used for monitoring,
    dashboards, cost-aware routing,
    and future intelligent routing decisions.
    """

    provider: str

    # ==========================================================
    # NEW: Request Metrics
    # ==========================================================

    total_requests: int = 0

    successful_requests: int = 0

    failed_requests: int = 0

    # ==========================================================
    # NEW: Latency Metrics
    # ==========================================================

    total_response_time_ms: float = 0.0

    average_response_time_ms: float = 0.0

    last_response_time_ms: float | None = None

    # ==========================================================
    # NEW: Error Metrics
    # ==========================================================

    last_error: str | None = None

    # ==========================================================
    # NEW: Audit Information
    # ==========================================================

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    # ==========================================================
    # NEW: Derived Metrics
    # ==========================================================

    @property
    def success_rate(self) -> float:
        """
        Returns success percentage.

        Example:
            8 successes / 10 requests = 80%
        """

        if self.total_requests == 0:
            return 100.0

        return (
            self.successful_requests
            / self.total_requests
        ) * 100

    @property
    def failure_rate(self) -> float:
        """
        Returns failure percentage.
        """

        return 100.0 - self.success_rate