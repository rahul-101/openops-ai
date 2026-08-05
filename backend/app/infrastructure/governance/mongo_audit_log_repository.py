from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.infrastructure.governance.audit_log import AuditLogEntry
from app.infrastructure.persistence.mongodb import get_database


class MongoAuditLogRepository:
    """
    MongoDB persistence for audit log entries.
    """

    def __init__(self) -> None:
        self.collection = get_database()[
            settings.AUDIT_LOG_COLLECTION
        ]

    def _to_document(self, entry: AuditLogEntry) -> dict:
        return {
            "id": entry.id,
            "timestamp": entry.timestamp,
            "user": entry.user,
            "action": entry.action,
            "decision": entry.decision,
            "incident_id": entry.incident_id,
            "agent": entry.agent,
            "model": entry.model,
            "approval_id": entry.approval_id,
            "metadata": entry.metadata,
        }

    def _from_document(self, document: dict) -> AuditLogEntry:
        document.pop("_id", None)
        return AuditLogEntry(**document)

    def insert(self, entry: AuditLogEntry) -> None:
        self.collection.replace_one(
            {"id": entry.id},
            self._to_document(entry),
            upsert=True,
        )

    def list(
        self,
        user: Optional[str] = None,
        action: Optional[str] = None,
        incident_id: Optional[str] = None,
        decision: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[AuditLogEntry]:
        query = {}
        if user is not None:
            query["user"] = user
        if action is not None:
            query["action"] = action
        if incident_id is not None:
            query["incident_id"] = incident_id
        if decision is not None:
            query["decision"] = decision

        cursor = self.collection.find(query).sort("timestamp", -1)

        if limit is not None:
            cursor = cursor.limit(limit)

        return [self._from_document(doc) for doc in cursor]

    def clear(self) -> None:
        self.collection.delete_many({})