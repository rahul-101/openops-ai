"""
Domain model for Incident.
"""

from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class Incident(BaseModel):
    """
    Domain model representing an incident.
    """

    model_config = ConfigDict(
        use_enum_values=False,
    )

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str

    description: str

    severity: IncidentSeverity

    status: IncidentStatus = IncidentStatus.OPEN

    source: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
