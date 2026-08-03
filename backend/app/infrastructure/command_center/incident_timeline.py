from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock


@dataclass
class TimelineEntry:
    """
    A single event on an incident timeline.
    """

    timestamp: datetime

    agent: str

    action: str

    status: str = ""

    duration_ms: float = 0.0

    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:

        return {
            "timestamp": self.timestamp.isoformat(),
            "agent": self.agent,
            "action": self.action,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "metadata": dict(self.metadata),
        }


class IncidentTimeline:
    """
    Thread safe store of per incident event timelines.
    """

    def __init__(self) -> None:

        self._timelines: dict[str, list[TimelineEntry]] = {}

        self._lock = Lock()

    def record(
        self,
        incident_id: str,
        entry: TimelineEntry,
    ) -> None:

        with self._lock:

            timeline = self._timelines.setdefault(
                incident_id,
                [],
            )

            timeline.append(entry)

    def get(
        self,
        incident_id: str,
    ) -> list[TimelineEntry]:

        with self._lock:
            return list(
                self._timelines.get(incident_id, [])
            )

    def incidents(self) -> list[str]:

        with self._lock:
            return list(self._timelines.keys())

    def clear(self) -> None:

        with self._lock:
            self._timelines.clear()
