from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Optional
from uuid import uuid4

from app.core.config import settings
from app.infrastructure.persistence import (
    from_jsonable,
    new_store,
    to_jsonable,
)
from app.infrastructure.persistence.mongodb import get_database

_LIST_KEY = "__all__"


@dataclass
class AuditLogEntry:
    """
    A single auditable AI decision.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )

    user: str = "system"

    action: str = ""

    decision: str = ""

    incident_id: str | None = None

    agent: str | None = None

    model: str | None = None

    approval_id: str | None = None

    metadata: dict = field(default_factory=dict)


class AuditLogService:
    """
    Records and queries AI audit events.

    Tracks user, incident, agent, model, action, decision,
    approval and timestamp for every auditable event.
    """

    def __init__(self) -> None:

        self._entries: list[AuditLogEntry] = []

        self._lock = Lock()

        self._store = new_store("audit_log")

        self._mongo_repo = None
        if settings.REPOSITORY_TYPE.lower() == "mongo":
            from app.infrastructure.governance.mongo_audit_log_repository import (
                MongoAuditLogRepository,
            )
            self._mongo_repo = MongoAuditLogRepository()

        if self._store is not None:

            blob = self._store.get(_LIST_KEY) or {}

            self._entries = []

            for record in blob.get("entries", []):

                parsed = from_jsonable(
                    record,
                    AuditLogEntry,
                )

                if parsed is not None:
                    self._entries.append(parsed)

    def _persist(self) -> None:

        if self._store is not None:
            self._store.save(
                _LIST_KEY,
                {
                    "entries": [
                        to_jsonable(entry)
                        for entry in self._entries
                    ]
                },
            )

    def record(
        self,
        *,
        user: str,
        action: str,
        decision: str,
        incident_id: str | None = None,
        agent: str | None = None,
        model: str | None = None,
        approval_id: str | None = None,
        **metadata,
    ) -> AuditLogEntry:

        entry = AuditLogEntry(
            user=user,
            action=action,
            decision=decision,
            incident_id=incident_id,
            agent=agent,
            model=model,
            approval_id=approval_id,
            metadata=metadata,
        )

        with self._lock:
            self._entries.append(entry)

        self._persist()

        if self._mongo_repo is not None:
            self._mongo_repo.insert(entry)

        return entry

    def list(
        self,
        user: str | None = None,
        action: str | None = None,
        incident_id: str | None = None,
        decision: str | None = None,
        limit: int | None = None,
    ) -> list[AuditLogEntry]:

        if self._mongo_repo is not None:
            return self._mongo_repo.list(
                user=user,
                action=action,
                incident_id=incident_id,
                decision=decision,
                limit=limit,
            )

        with self._lock:

            entries = [
                entry
                for entry in self._entries
                if (
                    user is None or entry.user == user
                )
                and (
                    action is None
                    or entry.action == action
                )
                and (
                    incident_id is None
                    or entry.incident_id == incident_id
                )
                and (
                    decision is None
                    or entry.decision == decision
                )
            ]

        if limit is not None:
            entries = entries[-limit:]

        return list(entries)

    def clear(self) -> None:

        with self._lock:
            self._entries.clear()

        if self._store is not None:
            self._store.clear()

        if self._mongo_repo is not None:
            self._mongo_repo.clear()
