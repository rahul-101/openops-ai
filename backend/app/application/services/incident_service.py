"""
Business logic for Incident management.
"""

from datetime import UTC, datetime

from app.application.dto.requests.incident_request import (
    UpdateIncidentRequest,
)
from app.domain.entities.incident import Incident
from app.domain.repositories.incident_repository import (
    IncidentRepository,
)


class IncidentService:
    """Business logic for managing incidents."""

    def __init__(
        self,
        repository: IncidentRepository,
    ) -> None:
        self._repository = repository

    def create_incident(
        self,
        incident: Incident,
    ) -> Incident:
        return self._repository.create(incident)

    def get_incident(
        self,
        incident_id: str,
    ) -> Incident:
        return self._repository.get(incident_id)

    def list_incidents(
        self,
    ) -> list[Incident]:
        return self._repository.list()

    def update_incident(
        self,
        incident_id: str,
        request: UpdateIncidentRequest,
    ) -> Incident:

        existing = self._repository.get(incident_id)

        updated = existing.model_copy(
            update={
                "title": request.title,
                "description": request.description,
                "severity": request.severity,
                "status": request.status,
                "source": request.source,
                "updated_at": datetime.now(UTC),
            }
        )

        return self._repository.update(updated)

    def delete_incident(
        self,
        incident_id: str,
    ) -> None:
        self._repository.delete(incident_id)