from datetime import datetime

from app.core.config import settings
from app.infrastructure.knowledge.incident_memory_repository import (
    IncidentMemoryRepository,
)
from app.infrastructure.knowledge.models import (
    IncidentMemory,
)
from app.infrastructure.persistence.mongodb import get_database


class MongoIncidentMemoryRepository(
    IncidentMemoryRepository
):
    """
    MongoDB implementation of incident memory storage.
    """

    def __init__(self) -> None:

        self.collection = get_database()[
            settings.INCIDENT_MEMORY_COLLECTION
        ]

    def save(
        self,
        memory: IncidentMemory,
    ) -> IncidentMemory:

        document = self._to_document(memory)

        self.collection.replace_one(
            {"incident_id": memory.incident_id},
            document,
            upsert=True,
        )

        return memory

    def get(
        self,
        incident_id: str,
    ) -> IncidentMemory | None:

        document = self.collection.find_one(
            {"incident_id": incident_id}
        )

        if document is None:
            return None

        return self._from_document(document)

    def list(self) -> list[IncidentMemory]:

        return [
            self._from_document(document)
            for document in self.collection.find({})
        ]

    def delete(
        self,
        incident_id: str,
    ) -> None:

        self.collection.delete_one(
            {"incident_id": incident_id}
        )

    # ==========================================================
    # Mapping Helpers
    # ==========================================================

    @staticmethod
    def _to_document(
        memory: IncidentMemory,
    ) -> dict:

        return {
            "incident_id": memory.incident_id,
            "root_cause": memory.root_cause,
            "recommendation": memory.recommendation,
            "final_resolution": memory.final_resolution,
            "human_feedback": memory.human_feedback,
            "created_at": memory.created_at,
            "updated_at": datetime.utcnow(),
        }

    @staticmethod
    def _from_document(
        document: dict,
    ) -> IncidentMemory:

        document.pop("_id", None)

        return IncidentMemory(**document)
