from abc import ABC, abstractmethod

from app.infrastructure.knowledge.models import (
    KnowledgeDocument,
    SimilaritySearchResult,
)


class VectorRepository(ABC):
    """
    Contract for storing embeddings and performing
    similarity search.
    """

    @abstractmethod
    def insert(
        self,
        document: KnowledgeDocument,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        document_id: str,
    ) -> KnowledgeDocument | None:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        document_id: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        limit: int | None = None,
    ) -> list[KnowledgeDocument]:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        embedding: list[float],
        limit: int = 5,
        filters: dict | None = None,
    ) -> list[SimilaritySearchResult]:
        raise NotImplementedError
