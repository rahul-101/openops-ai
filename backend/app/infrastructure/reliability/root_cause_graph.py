from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock


@dataclass
class RootCauseFactor:
    """
    A single factor contributing to an incident's root cause.
    """

    factor: str

    service: str

    weight: float = 1.0

    evidence: str = ""

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class RootCauseGraphNode:
    """
    A node in the root cause graph.
    """

    name: str

    factor: str = ""

    weight: float = 1.0

    evidence: str = ""


@dataclass
class RootCauseGraphRecord:
    """
    The multi-factor RCA for an incident.
    """

    incident_id: str

    factors: list[RootCauseFactor] = field(
        default_factory=list
    )

    edges: list[tuple[str, str]] = field(
        default_factory=list
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


class RootCauseGraph:
    """
    Builds a multi-factor root cause graph for an incident.

    - Records multiple contributing factors.
    - Captures dependency relationships between services
      involved in the incident.
    - Computes weighted root cause rankings.
    """

    def __init__(self) -> None:

        self._records: dict[str, RootCauseGraphRecord] = {}

        self._lock = Lock()

    def create(
        self,
        incident_id: str,
    ) -> RootCauseGraphRecord:

        with self._lock:

            record = self._records.setdefault(
                incident_id,
                RootCauseGraphRecord(
                    incident_id=incident_id,
                ),
            )

            return record

    def add_factor(
        self,
        incident_id: str,
        *,
        factor: str,
        service: str,
        weight: float = 1.0,
        evidence: str = "",
    ) -> RootCauseFactor:

        with self._lock:

            record = self._records.setdefault(
                incident_id,
                RootCauseGraphRecord(
                    incident_id=incident_id,
                ),
            )

            entry = RootCauseFactor(
                factor=factor,
                service=service,
                weight=weight,
                evidence=evidence,
            )

            record.factors.append(entry)

            return entry

    def add_dependency(
        self,
        incident_id: str,
        dependent: str,
        dependency: str,
    ) -> None:
        """
        Records that `dependent` depends on `dependency`.
        """

        with self._lock:

            record = self._records.setdefault(
                incident_id,
                RootCauseGraphRecord(
                    incident_id=incident_id,
                ),
            )

            edge = (dependent, dependency)

            if edge not in record.edges:
                record.edges.append(edge)

    def get(
        self,
        incident_id: str,
    ) -> RootCauseGraphRecord | None:

        with self._lock:
            return self._records.get(incident_id)

    def get_nodes(
        self,
        incident_id: str,
    ) -> list[RootCauseGraphNode]:
        """
        Returns graph nodes with weighted scores.
        """

        with self._lock:

            record = self._records.get(incident_id)

            if record is None:
                return []

            return [
                RootCauseGraphNode(
                    name=entry.service,
                    factor=entry.factor,
                    weight=entry.weight,
                    evidence=entry.evidence,
                )
                for entry in record.factors
            ]

    def get_edges(
        self,
        incident_id: str,
    ) -> list[tuple[str, str]]:

        with self._lock:

            record = self._records.get(incident_id)

            if record is None:
                return []

            return list(record.edges)

    def rank_root_causes(
        self,
        incident_id: str,
    ) -> list[RootCauseFactor]:
        """
        Returns factors ranked by weight descending.
        """

        with self._lock:

            record = self._records.get(incident_id)

            if record is None:
                return []

            factors = list(record.factors)

            factors.sort(
                key=lambda factor: factor.weight,
                reverse=True,
            )

            return factors

    def list(self) -> list[RootCauseGraphRecord]:

        with self._lock:
            return list(self._records.values())

    def clear(self) -> None:

        with self._lock:
            self._records.clear()
