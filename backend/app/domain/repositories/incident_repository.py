"""
Repository interface for Incident.
"""

from abc import ABC, abstractmethod

from app.domain.entities.incident import Incident


class IncidentRepository(ABC):
    """Abstract repository for Incident persistence."""

    @abstractmethod
    def create(self, incident: Incident) -> Incident:
        """Persist a new incident."""
        raise NotImplementedError

    @abstractmethod
    def get(self, incident_id: str) -> Incident:
        """Retrieve an incident by ID."""
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Incident]:
        """Return all incidents."""
        raise NotImplementedError