import pytest

from app.infrastructure.knowledge.incident_memory.in_memory_incident_memory_repository import (
    InMemoryIncidentMemoryRepository,
)
from app.infrastructure.knowledge.incident_memory_service import (
    IncidentMemoryService,
)


@pytest.fixture
def service() -> IncidentMemoryService:

    return IncidentMemoryService(
        repository=InMemoryIncidentMemoryRepository(),
    )


def test_save_and_get(service):

    _ = service.save(
        incident_id="inc-1",
        root_cause="pool exhaustion",
        recommendation="increase pool",
        final_resolution="resized pool",
    )

    fetched = service.get("inc-1")

    assert fetched is not None
    assert fetched.root_cause == "pool exhaustion"
    assert fetched.incident_id == "inc-1"
    assert fetched.human_feedback is None


def test_list(service):

    service.save(
        incident_id="inc-1",
        root_cause="cause 1",
        recommendation="rec 1",
        final_resolution="res 1",
    )

    service.save(
        incident_id="inc-2",
        root_cause="cause 2",
        recommendation="rec 2",
        final_resolution="res 2",
    )

    assert len(service.list()) == 2


def test_update_feedback(service):

    service.save(
        incident_id="inc-1",
        root_cause="cause",
        recommendation="rec",
        final_resolution="res",
    )

    updated = service.update_feedback(
        "inc-1",
        "feedback looks good",
    )

    assert updated.human_feedback == "feedback looks good"

    assert service.get("inc-1").human_feedback == (
        "feedback looks good"
    )


def test_update_feedback_missing_raises(service):

    with pytest.raises(ValueError):
        service.update_feedback(
            "missing",
            "feedback",
        )


def test_save_with_knowledge_base_indexes_resolution():

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

    knowledge_base = KnowledgeBaseService(
        repository=InMemoryVectorRepository(),
        embedding_service=HashingEmbeddingService(),
    )

    service = IncidentMemoryService(
        repository=InMemoryIncidentMemoryRepository(),
        knowledge_base=knowledge_base,
    )

    service.save(
        incident_id="inc-1",
        root_cause="pool exhaustion",
        recommendation="increase pool",
        final_resolution="resized the connection pool",
    )

    results = knowledge_base.search_resolutions(
        "connection pool resized"
    )

    assert len(results) == 1
    assert results[0].type == KnowledgeType.RESOLUTION.value
