from app.infrastructure.knowledge.incident_memory_repository import (
    IncidentMemoryRepository,
)
from app.infrastructure.knowledge.knowledge_base_service import (
    KnowledgeBaseService,
)
from app.infrastructure.knowledge.models import (
    IncidentMemory,
)


class IncidentMemoryService:
    """
    Captures root cause, recommendation, final resolution
    and human feedback for incidents.

    Memory can optionally be indexed into the knowledge base
    so future incidents can learn from past outcomes.
    """

    def __init__(
        self,
        repository: IncidentMemoryRepository,
        knowledge_base: KnowledgeBaseService | None = None,
    ) -> None:

        self.repository = repository
        self.knowledge_base = knowledge_base

    # ==========================================================
    # Save
    # ==========================================================

    def save(
        self,
        incident_id: str,
        root_cause: str,
        recommendation: str,
        final_resolution: str,
        human_feedback: str | None = None,
    ) -> IncidentMemory:

        memory = IncidentMemory(
            incident_id=incident_id,
            root_cause=root_cause,
            recommendation=recommendation,
            final_resolution=final_resolution,
            human_feedback=human_feedback,
        )

        self.repository.save(memory)

        if self.knowledge_base is not None:

            self.knowledge_base.store_resolution(
                title=f"Incident {incident_id} resolution",
                content=final_resolution,
                metadata={
                    "incident_id": incident_id,
                    "root_cause": root_cause,
                    "recommendation": recommendation,
                },
            )

        return memory

    # ==========================================================
    # Retrieve
    # ==========================================================

    def get(
        self,
        incident_id: str,
    ) -> IncidentMemory | None:

        return self.repository.get(incident_id)

    def list(self) -> list[IncidentMemory]:

        return self.repository.list()

    # ==========================================================
    # Feedback
    # ==========================================================

    def update_feedback(
        self,
        incident_id: str,
        human_feedback: str,
    ) -> IncidentMemory:

        memory = self.repository.get(incident_id)

        if memory is None:
            raise ValueError(
                f"No memory for incident '{incident_id}'."
            )

        memory.human_feedback = human_feedback

        return self.repository.save(memory)
