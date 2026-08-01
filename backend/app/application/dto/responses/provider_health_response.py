from datetime import datetime

from pydantic import BaseModel


class ProviderHealthResponse(BaseModel):
    """
    Health information exposed by the monitoring API.
    """

    provider: str

    status: str

    circuit_state: str

    consecutive_failures: int

    consecutive_successes: int

    last_success: datetime | None = None

    last_failure: datetime | None = None

    retry_after: datetime | None = None

    last_error: str | None = None

    updated_at: datetime