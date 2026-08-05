"""
In-memory implementation of the IncidentRepository.
"""

from app.core.exceptions import ResourceNotFoundException
from app.domain.entities.incident import Incident
from app.domain.models.incident_query import IncidentQuery
from app.domain.models.page import Page
from app.domain.repositories.incident_repository import IncidentRepository
from app.infrastructure.persistence import new_store


class InMemoryIncidentRepository(IncidentRepository):
    """In-memory implementation of the Incident repository."""

    def __init__(self) -> None:
        self._storage: dict[str, Incident] = {}

        self._store = new_store("incidents")

        if self._store is not None:

            for record in self._store.all():

                incident = Incident.model_validate(record)

                if incident is not None:
                    self._storage[incident.id] = incident

    def _persist(
        self,
        incident: Incident,
    ) -> None:

        if self._store is not None:
            self._store.save(
                incident.id,
                incident.model_dump(mode="json"),
            )

    def create(
        self,
        incident: Incident,
    ) -> Incident:
        """Store a new incident."""

        self._storage[incident.id] = incident
        self._persist(incident)
        return incident

    def get(
        self,
        incident_id: str,
    ) -> Incident:
        """Retrieve an incident by its ID."""

        incident = self._storage.get(incident_id)

        if incident is None:
            raise ResourceNotFoundException(
                f"Incident '{incident_id}' not found"
            )

        return incident

    def list(
        self,
        query: IncidentQuery,
    ) -> Page[Incident]:
        """Return incidents matching the supplied query."""

        incidents = list(self._storage.values())

        # --------------------------------
        # Filtering
        # --------------------------------

        if query.status is not None:
            incidents = [
                incident
                for incident in incidents
                if incident.status == query.status
            ]

        if query.severity is not None:
            incidents = [
                incident
                for incident in incidents
                if incident.severity == query.severity
            ]

        if query.source is not None:
            incidents = [
                incident
                for incident in incidents
                if incident.source.lower()
                == query.source.lower()
            ]

        if query.search:
            keyword = query.search.lower()

            incidents = [
                incident
                for incident in incidents
                if keyword in incident.title.lower()
                or keyword in incident.description.lower()
            ]

        # --------------------------------
        # Sorting
        # --------------------------------

        reverse = query.order == "desc"

        incidents.sort(
            key=lambda incident: getattr(
                incident,
                query.sort_by,
            ),
            reverse=reverse,
        )

        # --------------------------------
        # Pagination
        # --------------------------------

        total_items = len(incidents)

        start = (query.page - 1) * query.size
        end = start + query.size

        paginated_items = incidents[start:end]

        return Page(
            items=paginated_items,
            page=query.page,
            size=query.size,
            total_items=total_items,
        )

    def update(
        self,
        incident: Incident,
    ) -> Incident:
        """Update an existing incident."""

        if incident.id not in self._storage:
            raise ResourceNotFoundException(
                f"Incident '{incident.id}' not found"
            )

        self._storage[incident.id] = incident
        self._persist(incident)
        return incident

    def delete(
        self,
        incident_id: str,
    ) -> None:
        """Delete an incident."""

        if incident_id not in self._storage:
            raise ResourceNotFoundException(
                f"Incident '{incident_id}' not found"
            )

        del self._storage[incident_id]

        if self._store is not None:
            self._store.delete(incident_id)

    def clear(self) -> None:
        """Remove all incidents."""

        self._storage.clear()

        if self._store is not None:
            self._store.clear()
