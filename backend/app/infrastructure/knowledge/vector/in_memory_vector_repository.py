import math
from threading import Lock

from app.infrastructure.knowledge.models import (
    KnowledgeDocument,
    SimilaritySearchResult,
)
from app.infrastructure.knowledge.vector_repository import (
    VectorRepository,
)


class InMemoryVectorRepository(VectorRepository):
    """
    In-memory vector store with cosine similarity search.

    Used for local development and tests where MongoDB
    Atlas Vector Search is not available.
    """

    def __init__(self) -> None:

        self._documents: dict[str, KnowledgeDocument] = {}

        self._lock = Lock()

    def insert(
        self,
        document: KnowledgeDocument,
    ) -> None:

        with self._lock:
            self._documents[document.id] = document

    def get(
        self,
        document_id: str,
    ) -> KnowledgeDocument | None:

        return self._documents.get(document_id)

    def delete(
        self,
        document_id: str,
    ) -> None:

        with self._lock:
            self._documents.pop(document_id, None)

    def search(
        self,
        embedding: list[float],
        limit: int = 5,
        filters: dict | None = None,
    ) -> list[SimilaritySearchResult]:

        scored = []

        with self._lock:

            for document in self._documents.values():

                if document.embedding is None:
                    continue

                if not self._matches(document, filters):
                    continue

                score = self._cosine(
                    embedding,
                    document.embedding,
                )

                scored.append((score, document))

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            SimilaritySearchResult(
                document_id=document.id,
                title=document.title,
                content=document.content,
                type=document.type.value,
                metadata=dict(document.metadata),
                score=score,
            )
            for score, document in scored[:limit]
        ]

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _matches(
        document: KnowledgeDocument,
        filters: dict | None,
    ) -> bool:

        if not filters:
            return True

        for key, value in filters.items():

            if key == "type":
                if document.type.value != value:
                    return False
                continue

            if key == "source":
                if document.source != value:
                    return False
                continue

            if document.metadata.get(key) != value:
                return False

        return True

    @staticmethod
    def _cosine(
        a: list[float],
        b: list[float],
    ) -> float:

        dot = sum(x * y for x, y in zip(a, b))

        norm_a = math.sqrt(sum(x * x for x in a)) or 1.0

        norm_b = math.sqrt(sum(x * x for x in b)) or 1.0

        return dot / (norm_a * norm_b)
