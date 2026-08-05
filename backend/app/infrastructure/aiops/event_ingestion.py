from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from uuid import uuid4

from app.infrastructure.persistence import (
    from_jsonable,
    new_store,
    to_jsonable,
)


class EventSeverity(str, Enum):
    """
    Normalized severity for an ingested alert.
    """

    LOW = "low"

    MEDIUM = "medium"

    HIGH = "high"


SEVERITY_ALIASES = {
    "p1": EventSeverity.HIGH,
    "critical": EventSeverity.HIGH,
    "sev1": EventSeverity.HIGH,
    "high": EventSeverity.HIGH,
    "severe": EventSeverity.HIGH,
    "p2": EventSeverity.MEDIUM,
    "warning": EventSeverity.MEDIUM,
    "medium": EventSeverity.MEDIUM,
    "moderate": EventSeverity.MEDIUM,
    "sev2": EventSeverity.MEDIUM,
    "p3": EventSeverity.LOW,
    "info": EventSeverity.LOW,
    "low": EventSeverity.LOW,
    "minor": EventSeverity.LOW,
    "sev3": EventSeverity.LOW,
}


@dataclass
class RawAlert:
    """
    A raw alert as received from a monitoring system.
    """

    source: str

    alert_id: str

    title: str

    description: str = ""

    severity: str = "low"

    service: str | None = None

    tags: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    received_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class NormalizedEvent:
    """
    A normalized incident event produced from a raw alert.
    """

    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    source: str = ""

    alert_id: str = ""

    title: str = ""

    description: str = ""

    severity: EventSeverity = EventSeverity.LOW

    service: str | None = None

    tags: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    received_at: datetime = field(
        default_factory=datetime.utcnow
    )


class EventIngestionEngine:
    """
    Accepts alerts from monitoring systems and normalizes
    them into incident events.
    """

    def __init__(self) -> None:

        self._events: dict[str, NormalizedEvent] = {}

        self._lock = Lock()

        self._store = new_store("events")

        if self._store is not None:

            for record in self._store.all():

                event = from_jsonable(
                    record,
                    NormalizedEvent,
                )

                if event is not None:
                    self._events[event.event_id] = event

    def _persist(
        self,
        event: NormalizedEvent,
    ) -> None:

        if self._store is not None:
            self._store.save(
                event.event_id,
                to_jsonable(event),
            )

    def ingest(
        self,
        *,
        source: str,
        alert_id: str,
        title: str,
        description: str = "",
        severity: str = "low",
        service: str | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> NormalizedEvent:

        alert = RawAlert(
            source=source,
            alert_id=alert_id,
            title=title,
            description=description,
            severity=severity,
            service=service,
            tags=tags or [],
            metadata=metadata or {},
        )

        return self.ingest_alert(alert)

    def ingest_alert(
        self,
        alert: RawAlert,
    ) -> NormalizedEvent:

        event = NormalizedEvent(
            source=alert.source,
            alert_id=alert.alert_id,
            title=alert.title,
            description=alert.description,
            severity=self._normalize_severity(
                alert.severity
            ),
            service=alert.service,
            tags=list(alert.tags),
            metadata=dict(alert.metadata),
            received_at=alert.received_at,
        )

        with self._lock:
            self._events[event.event_id] = event

        self._persist(event)

        return event

    def list(
        self,
        source: str | None = None,
        severity: EventSeverity | None = None,
        limit: int | None = None,
    ) -> list[NormalizedEvent]:

        with self._lock:

            events = [
                event
                for event in self._events.values()
                if (
                    source is None
                    or event.source == source
                )
                and (
                    severity is None
                    or event.severity == severity
                )
            ]

        if limit is not None:
            events = events[-limit:]

        return list(events)

    def get(
        self,
        event_id: str,
    ) -> NormalizedEvent | None:

        with self._lock:
            return self._events.get(event_id)

    def clear(self) -> None:

        with self._lock:
            self._events.clear()

        if self._store is not None:
            self._store.clear()

    @staticmethod
    def _normalize_severity(
        severity: str,
    ) -> EventSeverity:

        key = str(severity).strip().lower()

        return SEVERITY_ALIASES.get(
            key,
            EventSeverity.LOW,
        )
