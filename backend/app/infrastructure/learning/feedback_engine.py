from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from uuid import uuid4


@dataclass
class FeedbackEntry:
    """
    A single captured AI recommendation outcome.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    recommendation_id: str = ""

    incident_id: str | None = None

    agent: str | None = None

    model: str | None = None

    outcome: str = ""

    human_feedback: str | None = None

    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class FeedbackEngine:
    """
    Captures AI recommendation outcomes.

    Stores whether a recommendation succeeded or failed and
    collects optional human feedback for each recommendation.
    """

    def __init__(self) -> None:

        self._entries: list[FeedbackEntry] = []

        self._lock = Lock()

    def record_outcome(
        self,
        *,
        recommendation_id: str,
        outcome: str,
        incident_id: str | None = None,
        agent: str | None = None,
        model: str | None = None,
        **metadata,
    ) -> FeedbackEntry:
        """
        Records the success or failure of a recommendation.
        """

        entry = FeedbackEntry(
            recommendation_id=recommendation_id,
            incident_id=incident_id,
            agent=agent,
            model=model,
            outcome=outcome,
            metadata=metadata,
        )

        with self._lock:
            self._entries.append(entry)

        return entry

    def record_human_feedback(
        self,
        *,
        recommendation_id: str,
        feedback: str,
        outcome: str | None = None,
    ) -> FeedbackEntry:
        """
        Attaches human feedback to a recommendation outcome.
        """

        with self._lock:

            for entry in reversed(self._entries):

                if (
                    entry.recommendation_id
                    == recommendation_id
                ):

                    entry.human_feedback = feedback

                    if outcome is not None:
                        entry.outcome = outcome

                    return entry

            entry = FeedbackEntry(
                recommendation_id=recommendation_id,
                outcome=outcome or "unknown",
                human_feedback=feedback,
            )

            self._entries.append(entry)

            return entry

    def list(
        self,
        outcome: str | None = None,
        incident_id: str | None = None,
        limit: int | None = None,
    ) -> list[FeedbackEntry]:

        with self._lock:

            entries = [
                entry
                for entry in self._entries
                if (
                    outcome is None
                    or entry.outcome == outcome
                )
                and (
                    incident_id is None
                    or entry.incident_id == incident_id
                )
            ]

        if limit is not None:
            entries = entries[-limit:]

        return list(entries)

    def get_stats(self) -> dict:

        with self._lock:

            total = len(self._entries)

            if total == 0:

                return {
                    "total": 0,
                    "successes": 0,
                    "failures": 0,
                    "success_rate": 0.0,
                    "with_human_feedback": 0,
                }

            successes = sum(
                1
                for e in self._entries
                if e.outcome == "success"
            )

            failures = sum(
                1
                for e in self._entries
                if e.outcome == "failure"
            )

            with_feedback = sum(
                1
                for e in self._entries
                if e.human_feedback is not None
            )

            return {
                "total": total,
                "successes": successes,
                "failures": failures,
                "success_rate": (successes / total) * 100,
                "with_human_feedback": with_feedback,
            }

    def clear(self) -> None:

        with self._lock:
            self._entries.clear()
