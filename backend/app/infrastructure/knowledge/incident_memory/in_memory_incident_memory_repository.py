from datetime import datetime
from threading import Lock

from app.infrastructure.knowledge.incident_memory_repository import (
    IncidentMemoryRepository,
)
from app.infrastructure.knowledge.models import (
    IncidentMemory,
)


class InMemoryIncidentMemoryRepository(
    IncidentMemoryRepository
):
    """
    In-memory incident memory storage.
    """

    def __init__(self) -> None:

        self._store: dict[str, IncidentMemory] = {}

        self._lock = Lock()

    def save(
        self,
        memory: IncidentMemory,
    ) -> IncidentMemory:

        with self._lock:

            memory.updated_at = datetime.utcnow()

            self._store[memory.incident_id] = memory

        return memory

    def get(
        self,
        incident_id: str,
    ) -> IncidentMemory | None:

        return self._store.get(incident_id)

    def list(self) -> list[IncidentMemory]:

        with self._lock:
            return list(self._store.values())

    def delete(
        self,
        incident_id: str,
    ) -> None:

        with self._lock:
            self._store.pop(incident_id, None)
