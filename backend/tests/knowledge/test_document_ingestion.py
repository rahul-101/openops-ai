from app.infrastructure.knowledge.document_ingestion import (
    DocumentIngestionPipeline,
)
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


def make_pipeline(
    chunk_size: int = 20,
    chunk_overlap: int = 5,
) -> DocumentIngestionPipeline:

    knowledge_base = KnowledgeBaseService(
        repository=InMemoryVectorRepository(),
        embedding_service=HashingEmbeddingService(),
    )

    return DocumentIngestionPipeline(
        knowledge_base=knowledge_base,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def test_parse_strips_markdown():

    pipeline = make_pipeline()

    parsed = pipeline.parse(
        "# Title\n```python\nprint('x')\n```\nSome *text* here."
    )

    assert "```" not in parsed
    assert "Title" in parsed
    assert "Some" in parsed


def test_parse_empty():

    pipeline = make_pipeline()

    assert pipeline.parse("") == ""


def test_chunk_single():

    pipeline = make_pipeline(chunk_size=100)

    chunks = pipeline.chunk("one two three four")

    assert chunks == ["one two three four"]


def test_chunk_multiple_with_overlap():

    pipeline = make_pipeline(
        chunk_size=4,
        chunk_overlap=2,
    )

    chunks = pipeline.chunk(
        "one two three four five six"
    )

    assert len(chunks) == 2

    assert chunks[0] == "one two three four"
    assert chunks[1] == "three four five six"


def test_chunk_empty():

    pipeline = make_pipeline()

    assert pipeline.chunk("") == []


def test_ingest_creates_chunked_documents():

    pipeline = make_pipeline(
        chunk_size=5,
        chunk_overlap=2,
    )

    content = " ".join(f"word{i}" for i in range(15))

    documents = pipeline.ingest(
        title="Runbook",
        content=content,
        type_=KnowledgeType.RUNBOOK,
        source="docs/runbook.md",
        metadata={"team": "platform"},
    )

    assert len(documents) > 1

    for index, document in enumerate(documents):

        assert document.type == KnowledgeType.RUNBOOK
        assert document.source == "docs/runbook.md"
        assert document.metadata["team"] == "platform"
        assert document.metadata["chunk_index"] == index
        assert document.embedding is not None

    assert documents[0].metadata["chunk_count"] == len(
        documents
    )


def test_ingest_searches_original_content():

    pipeline = make_pipeline(
        chunk_size=5,
        chunk_overlap=2,
    )

    _ = pipeline.ingest(
        title="Database Runbook",
        content=(
            "first step stop the database service "
            "second step restart and verify"
        ),
        type_=KnowledgeType.RUNBOOK,
    )

    results = pipeline.knowledge_base.search(
        "stop the database service"
    )

    assert len(results) >= 1
