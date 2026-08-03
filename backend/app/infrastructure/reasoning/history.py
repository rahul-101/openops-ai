from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock


@dataclass
class ReasoningHistoryRecord:
    """
    A persisted reasoning history entry for an incident.
    """

    incident_id: str

    agents_involved: list[str] = field(
        default_factory=list
    )

    decisions: list[str] = field(default_factory=list)

    confidence: float = 0.0

    risk: str = "low"

    outcome: str | None = None

    explanation: dict = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class ReasoningHistoryStore:
    """
    Thread safe in-memory store for reasoning history.
    """

    def __init__(self) -> None:

        self._records: dict[str, ReasoningHistoryRecord] = {}

        self._lock = Lock()

    def record(
        self,
        *,
        incident_id: str,
        agents_involved: list[str],
        decisions: list[str],
        confidence: float,
        risk: str,
        outcome: str | None = None,
        explanation: dict | None = None,
    ) -> ReasoningHistoryRecord:

        record = ReasoningHistoryRecord(
            incident_id=incident_id,
            agents_involved=list(agents_involved),
            decisions=list(decisions),
            confidence=confidence,
            risk=risk,
            outcome=outcome,
            explanation=dict(explanation or {}),
        )

        with self._lock:
            self._records[incident_id] = record

        return record

    def update_outcome(
        self,
        incident_id: str,
        outcome: str,
    ) -> ReasoningHistoryRecord | None:

        with self._lock:

            record = self._records.get(incident_id)

            if record is None:
                return None

            record.outcome = outcome
            record.updated_at = datetime.utcnow()

            return record

    def get(
        self,
        incident_id: str,
    ) -> ReasoningHistoryRecord | None:

        with self._lock:
            return self._records.get(incident_id)

    def list(
        self,
        limit: int | None = None,
    ) -> list[ReasoningHistoryRecord]:

        with self._lock:

            records = list(self._records.values())

        if limit is not None:
            records = records[-limit:]

        return records

    def list_by_outcome(
        self,
        outcome: str,
    ) -> list[ReasoningHistoryRecord]:

        with self._lock:

            return [
                record
                for record in self._records.values()
                if record.outcome == outcome
            ]

    def clear(self) -> None:

        with self._lock:
            self._records.clear()
