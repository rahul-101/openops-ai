import pytest

from app.infrastructure.knowledge.embedding_service import (
    HashingEmbeddingService,
)
from app.infrastructure.knowledge.knowledge_base_service import (
    KnowledgeBaseService,
)
from app.infrastructure.knowledge.models import KnowledgeType
from app.infrastructure.knowledge.vector.in_memory_vector_repository import (
    InMemoryVectorRepository,
)


@pytest.fixture
def service() -> KnowledgeBaseService:

    return KnowledgeBaseService(
        repository=InMemoryVectorRepository(),
        embedding_service=HashingEmbeddingService(),
    )


def test_store_incident(service):

    document = service.store_incident(
        title="DB outage",
        description="database is down",
        resolution="restarted pool",
        category="database",
        severity="High",
    )

    assert document.type == KnowledgeType.INCIDENT
    assert document.embedding is not None
    assert document.metadata["category"] == "database"


def test_store_runbook_resolution_troubleshooting(service):

    service.store_runbook(
        title="Runbook",
        content="steps to restart",
    )

    service.store_resolution(
        title="Resolution",
        content="increased pool size",
    )

    service.store_troubleshooting_document(
        title="Troubleshooting",
        content="check logs first",
    )

    assert len(service.repository._documents) == 3


def test_search_similar_incidents(service):

    service.store_incident(
        title="DB timeout",
        description="connection pool exhausted",
        category="database",
    )

    service.store_incident(
        title="Network loss",
        description="packets dropped",
        category="network",
    )

    results = service.search_similar_incidents(
        title="database timeout",
        description="connection pool exhausted",
        category="database",
    )

    assert len(results) == 1
    assert results[0].type == "incident"


def test_search_resolutions(service):

    service.store_resolution(
        title="Pool resize",
        content="increase connection pool size",
    )

    service.store_runbook(
        title="Restart",
        content="increase connection pool size",
    )

    results = service.search_resolutions(
        "increase connection pool",
    )

    assert len(results) == 1
    assert results[0].type == "resolution"


def test_search_by_type(service):

    service.store_runbook(
        title="Restart DB",
        content="run restart commands",
    )

    service.store_incident(
        title="Restart DB",
        description="run restart commands",
    )

    results = service.search(
        "restart database",
        type_=KnowledgeType.RUNBOOK,
    )

    assert len(results) == 1
    assert results[0].type == "runbook"


def test_get_and_delete(service):

    document = service.store_incident(
        title="Temp",
        description="temporary incident",
    )

    assert service.get(document.id) is not None

    service.delete(document.id)

    assert service.get(document.id) is None
