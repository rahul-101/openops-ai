"""
MongoDB implementation of IncidentRepository.
"""

from app.core.exceptions import ResourceNotFoundException
from app.domain.entities.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
)
from app.domain.repositories.incident_repository import IncidentRepository
from app.infrastructure.persistence.mongodb import get_database


class MongoIncidentRepository(IncidentRepository):
    """MongoDB implementation of IncidentRepository."""

    COLLECTION_NAME = "incidents"

    def __init__(self):
        self.collection = get_database()[self.COLLECTION_NAME]

    def create(self, incident: Incident) -> Incident:
        document = incident.model_dump()

        document["severity"] = incident.severity.value
        document["status"] = incident.status.value

        self.collection.insert_one(document)

        # Return the persisted document so datetime precision
        # matches what MongoDB actually stores.
        return self.get(incident.id)

    def get(self, incident_id: str) -> Incident:
        document = self.collection.find_one({"id": incident_id})

        if document is None:
            raise ResourceNotFoundException(
                f"Incident '{incident_id}' not found"
            )

        document.pop("_id", None)

        document["severity"] = IncidentSeverity(document["severity"])
        document["status"] = IncidentStatus(document["status"])

        return Incident(**document)

    def list(self) -> list[Incident]:
        incidents = []

        for document in self.collection.find():
            document.pop("_id", None)

            document["severity"] = IncidentSeverity(document["severity"])
            document["status"] = IncidentStatus(document["status"])

            incidents.append(Incident(**document))

        return incidents

    def update(self, incident: Incident) -> Incident:
        document = incident.model_dump()

        document["severity"] = incident.severity.value
        document["status"] = incident.status.value

        result = self.collection.replace_one(
            {"id": incident.id},
            document,
        )

        if result.matched_count == 0:
            raise ResourceNotFoundException(
                f"Incident '{incident.id}' not found"
            )

        # Return the persisted document for consistency.
        return self.get(incident.id)

    def delete(self, incident_id: str) -> None:
        result = self.collection.delete_one(
            {"id": incident_id}
        )

        if result.deleted_count == 0:
            raise ResourceNotFoundException(
                f"Incident '{incident_id}' not found"
            )