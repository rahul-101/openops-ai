"""
MongoDB implementation of IncidentRepository.
"""

from app.core.exceptions import ResourceNotFoundException
from app.domain.entities.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
)
from app.domain.models.incident_query import IncidentQuery
from app.domain.models.page import Page
from app.domain.repositories.incident_repository import IncidentRepository
from app.infrastructure.persistence.mongodb import get_database


class MongoIncidentRepository(IncidentRepository):
    """MongoDB implementation of IncidentRepository."""

    COLLECTION_NAME = "incidents"

    def __init__(self):
        self.collection = get_database()[self.COLLECTION_NAME]

    def create(
        self,
        incident: Incident,
    ) -> Incident:
        document = incident.model_dump()

        document["severity"] = incident.severity.value
        document["status"] = incident.status.value

        self.collection.insert_one(document)

        return self.get(incident.id)

    def get(
        self,
        incident_id: str,
    ) -> Incident:
        document = self.collection.find_one(
            {"id": incident_id}
        )

        if document is None:
            raise ResourceNotFoundException(
                f"Incident '{incident_id}' not found"
            )

        document.pop("_id", None)

        document["severity"] = IncidentSeverity(
            document["severity"]
        )

        document["status"] = IncidentStatus(
            document["status"]
        )

        return Incident(**document)

    def list(
        self,
        query: IncidentQuery,
    ) -> Page[Incident]:

        filters = {}

        if query.status is not None:
            filters["status"] = query.status.value

        if query.severity is not None:
            filters["severity"] = query.severity.value

        if query.source is not None:
            filters["source"] = query.source

        if query.search:
            filters["$or"] = [
                {
                    "title": {
                        "$regex": query.search,
                        "$options": "i",
                    }
                },
                {
                    "description": {
                        "$regex": query.search,
                        "$options": "i",
                    }
                },
            ]

        total_items = self.collection.count_documents(
            filters
        )

        direction = -1 if query.order == "desc" else 1

        cursor = (
            self.collection.find(filters)
            .sort(query.sort_by, direction)
            .skip((query.page - 1) * query.size)
            .limit(query.size)
        )

        incidents: list[Incident] = []

        for document in cursor:
            document.pop("_id", None)

            document["severity"] = IncidentSeverity(
                document["severity"]
            )

            document["status"] = IncidentStatus(
                document["status"]
            )

            incidents.append(
                Incident(**document)
            )

        return Page(
            items=incidents,
            page=query.page,
            size=query.size,
            total_items=total_items,
        )

    def update(
        self,
        incident: Incident,
    ) -> Incident:

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

        return self.get(
            incident.id
        )

    def delete(
        self,
        incident_id: str,
    ) -> None:

        result = self.collection.delete_one(
            {"id": incident_id}
        )

        if result.deleted_count == 0:
            raise ResourceNotFoundException(
                f"Incident '{incident_id}' not found"
            )

    def clear(self) -> None:
        """Remove all incidents from the collection."""

        self.collection.delete_many({})
