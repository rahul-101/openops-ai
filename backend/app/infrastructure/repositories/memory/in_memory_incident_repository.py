"""
In-memory implementation of the IncidentRepository.
"""

from app.core.exceptions import ResourceNotFoundException
from app.domain.entities.incident import Incident
from app.domain.repositories.incident_repository import IncidentRepository


class InMemoryIncidentRepository(IncidentRepository):
    """In-memory implementation of the Incident repository."""

    def __init__(self) -> None:
        self._storage: dict[str, Incident] = {}

    def create(self, incident: Incident) -> Incident:
        """Store a new incident."""
        self._storage[incident.id] = incident
        return incident

    def get(self, incident_id: str) -> Incident:
        """Retrieve an incident by its ID."""
        incident = self._storage.get(incident_id)

        if incident is None:
            raise ResourceNotFoundException(
                f"Incident '{incident_id}' not found."
            )

        return incident

    def list(self) -> list[Incident]:
        """Return all stored incidents."""
        return list(self._storage.values())