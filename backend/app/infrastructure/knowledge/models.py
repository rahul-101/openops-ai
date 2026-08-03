from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class KnowledgeType(str, Enum):
    """
    Type of a knowledge document.
    """

    INCIDENT = "incident"

    RUNBOOK = "runbook"

    RESOLUTION = "resolution"

    TROUBLESHOOTING = "troubleshooting_document"


@dataclass
class KnowledgeDocument:
    """
    A chunked, vector-embedded knowledge entry.
    """

    title: str

    content: str

    type: KnowledgeType

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    metadata: dict = field(default_factory=dict)

    embedding: list[float] | None = None

    source: str | None = None

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    def to_embedding_text(self) -> str:
        """
        Combined text used for embedding.
        """

        parts = [
            self.title,
            self.content,
        ]

        parts.extend(
            str(value)
            for value in self.metadata.values()
        )

        return "\n".join(parts)


@dataclass
class SimilaritySearchResult:
    """
    Result of a vector similarity search.
    """

    document_id: str

    title: str

    content: str

    type: str

    metadata: dict

    score: float


@dataclass
class IncidentMemory:
    """
    Persistent memory of an incident's outcome.
    """

    incident_id: str

    root_cause: str

    recommendation: str

    final_resolution: str

    human_feedback: str | None = None

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )
