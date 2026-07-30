from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    """
    Standard response returned by every AI provider.
    """

    summary: str = Field(
        ...,
        description="Short summary of the incident"
    )

    severity: str = Field(
        ...,
        description="Severity level"
    )

    category: str = Field(
        ...,
        description="Incident category"
    )

    probable_cause: str = Field(
        ...,
        description="Most likely root cause"
    )

    recommendation: str = Field(
        ...,
        description="Recommended remediation"
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score"
    )

    provider: str = Field(
        ...,
        description="Provider that generated the response"
    )

    model: str = Field(
        ...,
        description="Model name"
    )

    input_tokens: int = Field(
        default=0,
        ge=0,
        description="Input token count"
    )

    output_tokens: int = Field(
        default=0,
        ge=0,
        description="Output token count"
    )

    processing_time_ms: float = Field(
        default=0,
        ge=0,
        description="Execution time"
    )