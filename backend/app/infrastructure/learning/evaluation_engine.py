from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from uuid import uuid4


@dataclass
class EvaluationRecord:
    """
    An evaluation of an AI incident response.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    incident_id: str = ""

    rca_accurate: bool = False

    remediation_success: bool = False

    resolution_time_ms: int = 0

    confidence: float = 0.0

    outcome: bool = False

    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class EvaluationEngine:
    """
    Evaluates AI generated incident responses.

    Tracks:
    - RCA accuracy
    - remediation success
    - resolution time
    - confidence accuracy
    """

    def __init__(self) -> None:

        self._records: list[EvaluationRecord] = []

        self._lock = Lock()

    def record_evaluation(
        self,
        *,
        incident_id: str,
        rca_accurate: bool,
        remediation_success: bool,
        resolution_time_ms: int = 0,
        confidence: float = 0.0,
        outcome: bool | None = None,
        **metadata,
    ) -> EvaluationRecord:
        """
        Records an evaluation for an incident.
        """

        if outcome is None:
            outcome = (
                rca_accurate and remediation_success
            )

        record = EvaluationRecord(
            incident_id=incident_id,
            rca_accurate=rca_accurate,
            remediation_success=remediation_success,
            resolution_time_ms=resolution_time_ms,
            confidence=confidence,
            outcome=outcome,
            metadata=metadata,
        )

        with self._lock:
            self._records.append(record)

        return record

    def record_confidence(
        self,
        *,
        incident_id: str,
        confidence: float,
        outcome: bool,
    ) -> EvaluationRecord:
        """
        Records the predicted confidence against the actual
        outcome for confidence accuracy measurement.
        """

        return self.record_evaluation(
            incident_id=incident_id,
            rca_accurate=outcome,
            remediation_success=outcome,
            confidence=confidence,
            outcome=outcome,
        )

    def list(
        self,
        incident_id: str | None = None,
        limit: int | None = None,
    ) -> list[EvaluationRecord]:

        with self._lock:

            records = [
                record
                for record in self._records
                if (
                    incident_id is None
                    or record.incident_id == incident_id
                )
            ]

        if limit is not None:
            records = records[-limit:]

        return list(records)

    def get_stats(self) -> dict:

        with self._lock:

            total = len(self._records)

            if total == 0:

                return {
                    "total": 0,
                    "rca_accuracy": 0.0,
                    "remediation_success_rate": 0.0,
                    "average_resolution_time_ms": 0.0,
                    "average_confidence": 0.0,
                    "confidence_accuracy": 0.0,
                }

            rca_accurate = sum(
                1
                for r in self._records
                if r.rca_accurate
            )

            remediation_success = sum(
                1
                for r in self._records
                if r.remediation_success
            )

            resolutions = [
                r
                for r in self._records
                if r.resolution_time_ms > 0
            ]

            average_resolution = (
                sum(
                    r.resolution_time_ms
                    for r in resolutions
                )
                / len(resolutions)
                if resolutions
                else 0
            )

            confident = [
                r
                for r in self._records
                if r.confidence > 0
            ]

            confidence_accuracy = 0.0

            if confident:

                correct = sum(
                    1
                    for r in confident
                    if (
                        (r.confidence >= 0.5)
                        == r.outcome
                    )
                )

                confidence_accuracy = (
                    correct / len(confident)
                ) * 100

            return {
                "total": total,
                "rca_accuracy": (
                    rca_accurate / total
                ) * 100,
                "remediation_success_rate": (
                    remediation_success / total
                ) * 100,
                "average_resolution_time_ms": (
                    average_resolution
                ),
                "average_confidence": (
                    sum(
                        r.confidence
                        for r in self._records
                    )
                    / total
                ),
                "confidence_accuracy": (
                    confidence_accuracy
                ),
            }

    def clear(self) -> None:

        with self._lock:
            self._records.clear()
