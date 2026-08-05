from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.infrastructure.command_center.events import (
    CommandCenterEvent,
    EventType,
)
from app.infrastructure.persistence.mongodb import get_database


class MongoEventRepository:
    """
    MongoDB persistence for command center events.
    """

    def __init__(self) -> None:
        self.collection = get_database()[
            settings.COMMAND_CENTER_EVENTS_COLLECTION
        ]

    def _to_document(self, event: CommandCenterEvent) -> dict:
        return {
            "event_id": event.event_id,
            "type": event.type.value,
            "incident_id": event.incident_id,
            "agent": event.agent,
            "action": event.action,
            "status": event.status,
            "duration_ms": event.duration_ms,
            "metadata": event.metadata,
            "timestamp": event.timestamp,
        }

    def _from_document(self, document: dict) -> CommandCenterEvent:
        document.pop("_id", None)
        return CommandCenterEvent(
            event_id=document["event_id"],
            type=EventType(document["type"]),
            incident_id=document.get("incident_id", ""),
            agent=document.get("agent", ""),
            action=document.get("action", ""),
            status=document.get("status", ""),
            duration_ms=document.get("duration_ms", 0.0),
            metadata=document.get("metadata", {}),
            timestamp=document.get("timestamp", datetime.utcnow()),
        )

    def insert(self, event: CommandCenterEvent) -> None:
        self.collection.replace_one(
            {"event_id": event.event_id},
            self._to_document(event),
            upsert=True,
        )

    def history(
        self,
        limit: Optional[int] = None,
        event_type: Optional[EventType] = None,
        incident_id: Optional[str] = None,
    ) -> list[CommandCenterEvent]:
        query = {}
        if event_type is not None:
            query["type"] = event_type.value
        if incident_id is not None:
            query["incident_id"] = incident_id

        cursor = self.collection.find(query).sort("timestamp", -1)

        if limit is not None:
            cursor = cursor.limit(limit)

        return [self._from_document(doc) for doc in cursor]

    def clear(self) -> None:
        self.collection.delete_many({})