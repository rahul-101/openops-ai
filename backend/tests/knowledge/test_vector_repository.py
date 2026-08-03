from app.infrastructure.knowledge.embedding_service import (
    HashingEmbeddingService,
)
from app.infrastructure.knowledge.models import (
    KnowledgeDocument,
    KnowledgeType,
)
from app.infrastructure.knowledge.vector.in_memory_vector_repository import (
    InMemoryVectorRepository,
)


def build_document(
    title: str,
    content: str,
    type_: KnowledgeType,
    embedding_service: HashingEmbeddingService,
    **metadata,
) -> KnowledgeDocument:

    return KnowledgeDocument(
        title=title,
        content=content,
        type=type_,
        metadata=metadata,
        embedding=embedding_service.embed_text(
            f"{title}\n{content}"
        ),
    )


def test_insert_and_get():

    repository = InMemoryVectorRepository()

    embedding_service = HashingEmbeddingService()

    document = build_document(
        "DB Timeout",
        "database connection pool exhausted",
        KnowledgeType.INCIDENT,
        embedding_service,
    )

    repository.insert(document)

    fetched = repository.get(document.id)

    assert fetched is not None
    assert fetched.title == "DB Timeout"
    assert fetched.embedding == document.embedding


def test_delete():

    repository = InMemoryVectorRepository()

    embedding_service = HashingEmbeddingService()

    document = build_document(
        "Disk Full",
        "disk storage at capacity",
        KnowledgeType.INCIDENT,
        embedding_service,
    )

    repository.insert(document)

    repository.delete(document.id)

    assert repository.get(document.id) is None


def test_similarity_search_ranks_relevant_first():

    repository = InMemoryVectorRepository()

    embedding_service = HashingEmbeddingService()

    repository.insert(
        build_document(
            "Database Timeout",
            "database connection pool exhausted under load",
            KnowledgeType.INCIDENT,
            embedding_service,
            category="database",
        )
    )

    repository.insert(
        build_document(
            "Network Latency",
            "network packets dropped at edge gateway",
            KnowledgeType.INCIDENT,
            embedding_service,
            category="network",
        )
    )

    results = repository.search(
        embedding_service.embed_text("database connection timeout"),
        limit=5,
    )

    assert len(results) == 2

    assert results[0].document_id != results[1].document_id

    assert results[0].score >= results[1].score


def test_search_with_type_filter():

    repository = InMemoryVectorRepository()

    embedding_service = HashingEmbeddingService()

    repository.insert(
        build_document(
            "Restart Service",
            "restart the database service",
            KnowledgeType.RUNBOOK,
            embedding_service,
        )
    )

    repository.insert(
        build_document(
            "Restart Service",
            "restart the database service",
            KnowledgeType.INCIDENT,
            embedding_service,
        )
    )

    results = repository.search(
        embedding_service.embed_text("restart database service"),
        limit=5,
        filters={"type": "runbook"},
    )

    assert len(results) == 1
    assert results[0].type == "runbook"


def test_search_with_metadata_filter():

    repository = InMemoryVectorRepository()

    embedding_service = HashingEmbeddingService()

    repository.insert(
        build_document(
            "Auth Outage",
            "authentication service failed",
            KnowledgeType.INCIDENT,
            embedding_service,
            category="security",
        )
    )

    repository.insert(
        build_document(
            "Auth Outage",
            "authentication service failed",
            KnowledgeType.INCIDENT,
            embedding_service,
            category="database",
        )
    )

    results = repository.search(
        embedding_service.embed_text("auth outage"),
        limit=5,
        filters={"category": "security"},
    )

    assert len(results) == 1
    assert results[0].metadata["category"] == "security"
