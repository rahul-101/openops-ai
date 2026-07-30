from pydantic import BaseModel, Field


class GeminiResponse(BaseModel):
    """
    Validated response returned by Gemini before mapping to AIResponse.
    """

    summary: str = Field(
        ...,
        description="Short summary of the incident",
    )

    severity: str = Field(
        ...,
        description="Severity level",
    )

    category: str = Field(
        ...,
        description="Incident category",
    )

    probable_cause: str = Field(
        ...,
        description="Most likely root cause",
    )

    recommendation: str = Field(
        ...,
        description="Recommended remediation",
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1",
    )