from pydantic import BaseModel


class ProviderMetricsResponse(BaseModel):
    """
    Provider metrics exposed by the monitoring API.
    """

    provider: str

    total_requests: int

    successful_requests: int

    failed_requests: int

    success_rate: float

    failure_rate: float

    average_response_time_ms: float

    last_response_time_ms: float | None = None

    last_error: str | None = None

    updated_at: str