from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock


class CorrelationMethod(str, Enum):
    """
    How incidents were determined to be related.
    """

    EXACT_DUPLICATE = "exact_duplicate"

    SIMILAR_SIGNATURE = "similar_signature"

    SHARED_SERVICE = "shared_service"

    SHARED_TAG = "shared_tag"


@dataclass
class CorrelationGroup:
    """
    A group of related incidents.
    """

    id: str

    incidents: list[str] = field(default_factory=list)

    methods: list[str] = field(default_factory=list)

    primary_incident: str | None = None

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class CorrelationResult:
    """
    Result of checking an incident against known incidents.
    """

    incident_id: str

    duplicate: bool = False

    group_id: str | None = None

    matches: list[str] = field(default_factory=list)

    method: CorrelationMethod | None = None


class IncidentCorrelation:
    """
    Detects duplicate incidents and merges related incidents.

    An incident signature is built from its source, service
    and tags. Incidents with the same signature are treated
    as duplicates; incidents sharing service or tags are
    merged into a related group.
    """

    def __init__(self) -> None:

        self._incidents: dict[str, dict] = {}

        self._groups: dict[str, CorrelationGroup] = {}

        self._next_group = 0

        self._lock = Lock()

    def register_incident(
        self,
        *,
        incident_id: str,
        source: str = "",
        service: str | None = None,
        tags: list[str] | None = None,
        title: str = "",
    ) -> None:

        with self._lock:

            self._incidents[incident_id] = {
                "source": source,
                "service": service,
                "tags": [t.lower() for t in tags or []],
                "title": title,
            }

    def correlate(
        self,
        *,
        incident_id: str,
        source: str = "",
        service: str | None = None,
        tags: list[str] | None = None,
        title: str = "",
    ) -> CorrelationResult:
        """
        Checks an incident for duplicates or related groups.
        """

        normalized = {
            "source": source,
            "service": service,
            "tags": [t.lower() for t in tags or []],
            "title": title,
        }

        with self._lock:

            existing = list(self._incidents.items())

            for known_id, known in existing:

                if self._is_exact_duplicate(
                    normalized,
                    known,
                ):

                    group = self._group_for(known_id)

                    if group is not None:
                        self._add_to_group(
                            group.id,
                            incident_id,
                        )

                    return CorrelationResult(
                        incident_id=incident_id,
                        duplicate=True,
                        group_id=(
                            group.id if group else None
                        ),
                        matches=[known_id],
                        method=(
                            CorrelationMethod.EXACT_DUPLICATE
                        ),
                    )

            related = self._find_related(
                incident_id,
                normalized,
            )

        self.register_incident(
            incident_id=incident_id,
            source=source,
            service=service,
            tags=tags,
            title=title,
        )

        if related is not None:

            return CorrelationResult(
                incident_id=incident_id,
                duplicate=False,
                group_id=related.id,
                matches=list(related.incidents),
                method=self._related_method(
                    normalized,
                    related,
                ),
            )

        return CorrelationResult(
            incident_id=incident_id,
        )

    def merge(
        self,
        primary: str,
        secondary: str,
    ) -> CorrelationGroup:
        """
        Merges two incidents into a related group.
        """

        with self._lock:

            group_id = self._new_group_id()

            group = CorrelationGroup(
                id=group_id,
                incidents=[primary, secondary],
                primary_incident=primary,
            )

            self._groups[group_id] = group

            return group

    def get_group(
        self,
        group_id: str,
    ) -> CorrelationGroup | None:

        with self._lock:
            return self._groups.get(group_id)

    def list_groups(self) -> list[CorrelationGroup]:

        with self._lock:
            return list(self._groups.values())

    def clear(self) -> None:

        with self._lock:
            self._incidents.clear()
            self._groups.clear()
            self._next_group = 0

    # ==========================================================
    # Helpers
    # ==========================================================

    def _is_exact_duplicate(
        self,
        candidate: dict,
        known: dict,
    ) -> bool:
        """
        Duplicate when signature fields fully match.
        """

        return (
            candidate["source"] == known["source"]
            and candidate["service"] == known["service"]
            and set(candidate["tags"]) == set(known["tags"])
        )

    def _find_related(
        self,
        incident_id: str,
        candidate: dict,
    ) -> CorrelationGroup | None:
        """
        Finds an existing group sharing service or tags.
        """

        for group in self._groups.values():

            for member in group.incidents:

                known = self._incidents.get(member)

                if known is None:
                    continue

                if self._shares_relation(candidate, known):

                    self._add_to_group(
                        group.id,
                        incident_id,
                    )

                    return group

        return None

    @staticmethod
    def _shares_relation(
        candidate: dict,
        known: dict,
    ) -> bool:
        """
        Related when sharing a service or a tag.
        """

        shares_service = (
            candidate["service"] is not None
            and candidate["service"] == known["service"]
        )

        shares_tag = bool(
            set(candidate["tags"]) & set(known["tags"])
        )

        return shares_service or shares_tag

    def _related_method(
        self,
        candidate: dict,
        group: CorrelationGroup,
    ) -> CorrelationMethod | None:

        for member in group.incidents:

            known = self._incidents.get(member)

            if known is None:
                continue

            if (
                candidate["service"] is not None
                and candidate["service"] == known["service"]
            ):
                return CorrelationMethod.SHARED_SERVICE

            if set(candidate["tags"]) & set(known["tags"]):
                return CorrelationMethod.SHARED_TAG

        return None

    def _group_for(
        self,
        incident_id: str,
    ) -> CorrelationGroup | None:

        for group in self._groups.values():

            if incident_id in group.incidents:
                return group

        return None

    def _add_to_group(
        self,
        group_id: str,
        incident_id: str,
    ) -> None:

        group = self._groups.get(group_id)

        if group is None:
            return

        if incident_id not in group.incidents:
            group.incidents.append(incident_id)

    def _new_group_id(self) -> str:

        self._next_group += 1

        return f"group-{self._next_group}"
