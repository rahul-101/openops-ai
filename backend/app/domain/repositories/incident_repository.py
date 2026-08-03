"""
Repository interface for Incident persistence.
"""

from abc import ABC, abstractmethod

from app.domain.entities.incident import Incident
from app.domain.models.incident_query import IncidentQuery
from app.domain.models.page import Page


class IncidentRepository(ABC):
    """Repository contract for Incident persistence."""

    @abstractmethod
    def create(
        self,
        incident: Incident,
    ) -> Incident:
        """Persist a new incident."""

    @abstractmethod
    def get(
        self,
        incident_id: str,
    ) -> Incident:
        """Retrieve an incident by ID."""

    @abstractmethod
    def list(
    self,
    query: IncidentQuery,
) -> Page[Incident]:
        """Retrieve incidents matching the supplied query."""

    @abstractmethod
    def update(
        self,
        incident: Incident,
    ) -> Incident:
        """Update an existing incident."""

    @abstractmethod
    def delete(
        self,
        incident_id: str,
    ) -> None:
        """Delete an incident."""
