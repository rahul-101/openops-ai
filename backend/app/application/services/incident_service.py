"""
Business logic for Incident management.
"""

from app.domain.entities.incident import Incident
from app.domain.repositories.incident_repository import IncidentRepository


class IncidentService:
    """Business logic for managing incidents."""

    def __init__(self, repository: IncidentRepository) -> None:
        self._repository = repository

    def create_incident(self, incident: Incident) -> Incident:
        return self._repository.create(incident)

    def get_incident(self, incident_id: str) -> Incident:
        return self._repository.get(incident_id)

    def list_incidents(self) -> list[Incident]:
        return self._repository.list()