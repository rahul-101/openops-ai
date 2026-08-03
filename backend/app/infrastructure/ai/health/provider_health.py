from dataclasses import dataclass, field
from datetime import datetime

from app.infrastructure.ai.health.circuit_state import (
    CircuitState,
)


class ProviderStatus(str):
    """
    Logical provider health.
    """

    HEALTHY = "healthy"

    UNHEALTHY = "unhealthy"


@dataclass
class ProviderHealth:
    """
    Runtime health information for an AI provider.

    Health indicates whether the provider is considered
    healthy.

    Circuit State determines whether requests may be
    routed to the provider.
    """

    provider: str

    # ==========================================================
    # Health
    # ==========================================================

    status: str = ProviderStatus.HEALTHY

    # ==========================================================
    # Circuit Breaker
    # ==========================================================

    circuit_state: CircuitState = (
        CircuitState.CLOSED
    )

    opened_at: datetime | None = None

    last_state_change: datetime | None = None

    half_open_attempts: int = 0

    # ==========================================================
    # Failure Tracking
    # ==========================================================

    consecutive_failures: int = 0

    consecutive_successes: int = 0

    # ==========================================================
    # Runtime Information
    # ==========================================================

    last_failure: datetime | None = None

    last_success: datetime | None = None

    retry_after: datetime | None = None

    last_error: str | None = None

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )
