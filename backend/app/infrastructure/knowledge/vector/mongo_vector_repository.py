from app.core.config import settings
from app.infrastructure.knowledge.models import (
    KnowledgeDocument,
    KnowledgeType,
    SimilaritySearchResult,
)
from app.infrastructure.knowledge.vector_repository import (
    VectorRepository,
)
from app.infrastructure.persistence.mongodb import get_database


class MongoVectorRepository(VectorRepository):
    """
    MongoDB Atlas Vector Search implementation.

    Requires an Atlas Search index named `settings.VECTOR_SEARCH_INDEX`
    on the `embedding` field of the knowledge collection.
    """

    def __init__(self) -> None:

        self.collection = get_database()[
            settings.KNOWLEDGE_COLLECTION
        ]

    def insert(
        self,
        document: KnowledgeDocument,
    ) -> None:

        self.collection.replace_one(
            {"id": document.id},
            self._to_document(document),
            upsert=True,
        )

    def get(
        self,
        document_id: str,
    ) -> KnowledgeDocument | None:

        document = self.collection.find_one(
            {"id": document_id}
        )

        if document is None:
            return None

        return self._from_document(document)

    def delete(
        self,
        document_id: str,
    ) -> None:

        self.collection.delete_one(
            {"id": document_id}
        )

    def list(
        self,
        limit: int | None = None,
    ) -> list[KnowledgeDocument]:

        cursor = self.collection.find(
            {},
            {"embedding": 0},
        ).sort(
            "created_at", -1
        )

        if limit is not None:
            cursor = cursor.limit(limit)

        return [
            self._from_document(document)
            for document in cursor
        ]

    def search(
        self,
        embedding: list[float],
        limit: int = 5,
        filters: dict | None = None,
    ) -> list[SimilaritySearchResult]:

        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": embedding,
                    "path": "embedding",
                    "numCandidates": limit * 10,
                    "limit": limit,
                    "index": settings.VECTOR_SEARCH_INDEX,
                }
            },
            {
                "$set": {
                    "score": {"$meta": "vectorSearchScore"}
                }
            },
        ]

        if filters:
            pipeline.append(
                {"$match": self._to_match(filters)}
            )

        pipeline.append(
            {"$project": {"embedding": 0}}
        )

        return [
            self._to_search_result(document)
            for document in self.collection.aggregate(pipeline)
        ]

    # ==========================================================
    # Mapping Helpers
    # ==========================================================

    def _to_document(
        self,
        document: KnowledgeDocument,
    ) -> dict:

        return {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "type": document.type.value,
            "metadata": document.metadata,
            "embedding": document.embedding,
            "source": document.source,
            "created_at": document.created_at,
            "updated_at": document.updated_at,
        }

    def _from_document(
        self,
        document: dict,
    ) -> KnowledgeDocument:

        document.pop("_id", None)

        document["type"] = KnowledgeType(
            document["type"]
        )

        return KnowledgeDocument(**document)

    @staticmethod
    def _to_match(
        filters: dict,
    ) -> dict:

        match = {}

        for key, value in filters.items():

            if key in (
                "type",
                "source",
                "title",
            ):
                match[key] = value
            else:
                match[f"metadata.{key}"] = value

        return match

    @staticmethod
    def _to_search_result(
        document: dict,
    ) -> SimilaritySearchResult:

        return SimilaritySearchResult(
            document_id=document["id"],
            title=document.get("title", ""),
            content=document.get("content", ""),
            type=document.get("type", ""),
            metadata=document.get("metadata", {}),
            score=document.get("score", 0.0),
        )
