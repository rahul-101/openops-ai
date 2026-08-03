"""
Response DTOs for Incident APIs.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.entities.incident import (
    IncidentSeverity,
    IncidentStatus,
)


class IncidentResponse(BaseModel):
    """
    DTO returned to API clients.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    source: str
    created_at: datetime
    updated_at: datetime
