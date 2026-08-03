from abc import ABC, abstractmethod

from app.infrastructure.knowledge.models import (
    IncidentMemory,
)


class IncidentMemoryRepository(ABC):
    """
    Contract for persisting incident memory.
    """

    @abstractmethod
    def save(
        self,
        memory: IncidentMemory,
    ) -> IncidentMemory:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        incident_id: str,
    ) -> IncidentMemory | None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[IncidentMemory]:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        incident_id: str,
    ) -> None:
        raise NotImplementedError
