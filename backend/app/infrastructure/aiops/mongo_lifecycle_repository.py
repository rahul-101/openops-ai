from typing import Optional

from app.core.config import settings
from app.infrastructure.aiops.lifecycle import (
    LifecycleIncident,
    LifecycleStatus,
    LifecycleStep,
)
from app.infrastructure.aiops.event_ingestion import NormalizedEvent
from app.infrastructure.persistence.mongodb import get_database


class MongoLifecycleRepository:
    """
    MongoDB persistence for incident lifecycle records.
    """

    def __init__(self) -> None:
        self.collection = get_database()[
            settings.LIFECYCLE_COLLECTION
        ]

    def _step_to_document(self, step: LifecycleStep) -> dict:
        return {
            "stage": step.stage,
            "status": step.status,
            "details": step.details,
            "timestamp": step.timestamp,
        }

    def _step_from_document(self, document: dict) -> LifecycleStep:
        return LifecycleStep(
            stage=document["stage"],
            status=document["status"],
            details=document.get("details", {}),
            timestamp=document.get("timestamp"),
        )

    def _event_to_document(self, event: NormalizedEvent) -> dict:
        return {
            "event_id": event.event_id,
            "source": event.source,
            "title": event.title,
            "description": event.description,
            "severity": event.severity.value,
            "timestamp": event.timestamp,
            "metadata": event.metadata,
        }

    def _event_from_document(self, document: dict) -> NormalizedEvent:
        from app.infrastructure.aiops.event_ingestion import (
            EventSeverity,
            NormalizedEvent,
        )

        return NormalizedEvent(
            event_id=document["event_id"],
            source=document["source"],
            title=document["title"],
            description=document.get("description", ""),
            severity=EventSeverity(document["severity"]),
            timestamp=document.get("timestamp"),
            metadata=document.get("metadata", {}),
        )

    def _to_document(self, incident: LifecycleIncident) -> dict:
        return {
            "incident_id": incident.incident_id,
            "status": incident.status.value,
            "event": (
                self._event_to_document(incident.event)
                if incident.event is not None
                else None
            ),
            "steps": [
                self._step_to_document(step) for step in incident.steps
            ],
            "servicenow_updated": incident.servicenow_updated,
            "learning_recorded": incident.learning_recorded,
            "created_at": incident.created_at,
            "updated_at": incident.updated_at,
        }

    def _from_document(self, document: dict) -> LifecycleIncident:
        document.pop("_id", None)

        event = document.get("event")
        return LifecycleIncident(
            incident_id=document["incident_id"],
            status=LifecycleStatus(document["status"]),
            event=self._event_from_document(event) if event else None,
            steps=[
                self._step_from_document(step)
                for step in document.get("steps", [])
            ],
            servicenow_updated=document.get("servicenow_updated", False),
            learning_recorded=document.get("learning_recorded", False),
            created_at=document.get("created_at"),
            updated_at=document.get("updated_at"),
        )

    def save(self, incident: LifecycleIncident) -> None:
        self.collection.replace_one(
            {"incident_id": incident.incident_id},
            self._to_document(incident),
            upsert=True,
        )

    def get(self, incident_id: str) -> LifecycleIncident | None:
        document = self.collection.find_one(
            {"incident_id": incident_id}
        )
        if document is None:
            return None
        return self._from_document(document)

    def list(self) -> list[LifecycleIncident]:
        cursor = self.collection.find({}).sort("created_at", -1)
        return [self._from_document(doc) for doc in cursor]

    def clear(self) -> None:
        self.collection.delete_many({})