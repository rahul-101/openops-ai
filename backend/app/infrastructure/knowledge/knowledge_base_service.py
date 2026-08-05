from app.infrastructure.knowledge.embedding_service import (
    EmbeddingService,
)
from app.infrastructure.knowledge.models import (
    KnowledgeDocument,
    KnowledgeType,
    SimilaritySearchResult,
)
from app.infrastructure.knowledge.vector_repository import (
    VectorRepository,
)


class KnowledgeBaseService:
    """
    Stores incidents, runbooks, resolutions and troubleshooting
    documents as vector-embedded knowledge.
    """

    def __init__(
        self,
        repository: VectorRepository,
        embedding_service: EmbeddingService,
    ) -> None:

        self.repository = repository
        self.embedding_service = embedding_service

    # ==========================================================
    # Store
    # ==========================================================

    def store_document(
        self,
        title: str,
        content: str,
        type_: KnowledgeType,
        metadata: dict | None = None,
        source: str | None = None,
        embedding: list[float] | None = None,
    ) -> KnowledgeDocument:

        if embedding is None:

            embedding = self.embedding_service.embed_text(
                f"{title}\n{content}"
            )

        document = KnowledgeDocument(
            title=title,
            content=content,
            type=type_,
            metadata=metadata or {},
            embedding=embedding,
            source=source,
        )

        self.repository.insert(document)

        return document

    def store_incident(
        self,
        title: str,
        description: str,
        resolution: str | None = None,
        category: str | None = None,
        severity: str | None = None,
    ) -> KnowledgeDocument:

        return self.store_document(
            title=title,
            content=description,
            type_=KnowledgeType.INCIDENT,
            metadata={
                "category": category,
                "severity": severity,
                "resolution": resolution,
            },
        )

    def store_runbook(
        self,
        title: str,
        content: str,
        metadata: dict | None = None,
    ) -> KnowledgeDocument:

        return self.store_document(
            title=title,
            content=content,
            type_=KnowledgeType.RUNBOOK,
            metadata=metadata,
        )

    def store_resolution(
        self,
        title: str,
        content: str,
        metadata: dict | None = None,
    ) -> KnowledgeDocument:

        return self.store_document(
            title=title,
            content=content,
            type_=KnowledgeType.RESOLUTION,
            metadata=metadata,
        )

    def store_troubleshooting_document(
        self,
        title: str,
        content: str,
        metadata: dict | None = None,
    ) -> KnowledgeDocument:

        return self.store_document(
            title=title,
            content=content,
            type_=KnowledgeType.TROUBLESHOOTING,
            metadata=metadata,
        )

    # ==========================================================
    # Retrieve
    # ==========================================================

    def search(
        self,
        query: str,
        limit: int = 5,
        type_: KnowledgeType | None = None,
        **metadata_filters,
    ) -> list[SimilaritySearchResult]:

        embedding = self.embedding_service.embed_text(
            query
        )

        filters = dict(metadata_filters)

        if type_ is not None:
            filters["type"] = type_.value

        return self.repository.search(
            embedding,
            limit=limit,
            filters=filters or None,
        )

    def search_similar_incidents(
        self,
        title: str,
        description: str,
        limit: int = 5,
        category: str | None = None,
    ) -> list[SimilaritySearchResult]:

        return self.search(
            query=f"{title} {description}",
            limit=limit,
            type_=KnowledgeType.INCIDENT,
            category=category,
        )

    def search_resolutions(
        self,
        query: str,
        limit: int = 5,
    ) -> list[SimilaritySearchResult]:

        return self.search(
            query=query,
            limit=limit,
            type_=KnowledgeType.RESOLUTION,
        )

    def get(
        self,
        document_id: str,
    ) -> KnowledgeDocument | None:

        return self.repository.get(document_id)

    def list(
        self,
        limit: int | None = None,
    ) -> list[KnowledgeDocument]:

        return self.repository.list(limit=limit)

    def delete(
        self,
        document_id: str,
    ) -> None:

        self.repository.delete(document_id)

    def clear(self) -> None:

        self.repository.clear()
