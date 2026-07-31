from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProviderStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


@dataclass
class ProviderHealth:
    """
    Runtime health information for an AI provider.
    """

    provider: str

    status: ProviderStatus = ProviderStatus.HEALTHY

    consecutive_failures: int = 0

    consecutive_successes: int = 0

    last_failure: datetime | None = None

    last_success: datetime |None = None

    last_error: str | None = None

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    # Earliest time at which an unhealthy provider
    # may be retried.
    retry_after: datetime | None = None