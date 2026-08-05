import math
from datetime import datetime
from threading import Lock

from app.infrastructure.knowledge.models import (
    KnowledgeDocument,
    SimilaritySearchResult,
)
from app.infrastructure.knowledge.vector_repository import (
    VectorRepository,
)
from app.infrastructure.persistence import (
    from_jsonable,
    new_store,
    to_jsonable,
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

        self._store = new_store("knowledge_docs")

        if self._store is not None:

            for record in self._store.all():

                document = from_jsonable(
                    record,
                    KnowledgeDocument,
                )

                if document is not None:
                    self._documents[document.id] = document

    def _persist(
        self,
        document: KnowledgeDocument,
    ) -> None:

        if self._store is not None:
            self._store.save(
                document.id,
                to_jsonable(document),
            )

    def insert(
        self,
        document: KnowledgeDocument,
    ) -> None:

        with self._lock:
            self._documents[document.id] = document

        self._persist(document)

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

        if self._store is not None:
            self._store.delete(document_id)

    def clear(self) -> None:

        with self._lock:
            self._documents.clear()

        if self._store is not None:
            self._store.clear()

    def list(
        self,
        limit: int | None = None,
    ) -> list[KnowledgeDocument]:

        with self._lock:
            documents = list(self._documents.values())

        documents.sort(
            key=lambda d: d.created_at or datetime.min,
            reverse=True,
        )

        if limit is not None:
            documents = documents[:limit]

        return documents

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
