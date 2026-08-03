"""
Business logic for Incident management.
"""

from datetime import UTC, datetime

from app.application.dto.requests.incident_request import UpdateIncidentRequest
from app.domain.entities.incident import Incident
from app.domain.models.incident_query import IncidentQuery
from app.domain.models.page import Page
from app.domain.repositories.incident_repository import IncidentRepository


class IncidentService:
    """Business logic for managing incidents."""

    def __init__(self, repository: IncidentRepository) -> None:
        self._repository = repository

    def create_incident(self, incident: Incident) -> Incident:
        """Create a new incident."""
        return self._repository.create(incident)

    def get_incident(self, incident_id: str) -> Incident:
        """Retrieve an incident by its ID."""
        return self._repository.get(incident_id)

    def list_incidents(
        self,
        query: IncidentQuery | None = None,
    ) -> Page[Incident]:
        """Return paginated incidents."""

        query = query or IncidentQuery()
        return self._repository.list(query)

    def update_incident(
        self,
        incident_id: str,
        request: UpdateIncidentRequest,
    ) -> Incident:
        """Update an existing incident."""

        existing = self._repository.get(incident_id)

        update_data = request.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(UTC)

        updated = existing.model_copy(update=update_data)

        return self._repository.update(updated)

    def delete_incident(
        self,
        incident_id: str,
    ) -> None:
        """Delete an incident."""
        self._repository.delete(incident_id)
