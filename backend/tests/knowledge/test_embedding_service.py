from app.infrastructure.knowledge.embedding_service import (
    HashingEmbeddingService,
)
from app.infrastructure.knowledge.embeddings.gemini_embedding_service import (
    GeminiEmbeddingService,
)


def test_hashing_embedding_dimension():

    service = HashingEmbeddingService(dimension=64)

    vector = service.embed_text("database timeout")

    assert len(vector) == 64


def test_hashing_embedding_is_deterministic():

    service = HashingEmbeddingService()

    assert (
        service.embed_text("incident text")
        == service.embed_text("incident text")
    )


def test_hashing_embedding_normalized():

    service = HashingEmbeddingService()

    vector = service.embed_text("runbook restart service")

    norm = sum(value * value for value in vector) ** 0.5

    assert abs(norm - 1.0) < 1e-6


def test_embed_texts():

    service = HashingEmbeddingService(dimension=32)

    vectors = service.embed_texts(
        ["first document", "second document"]
    )

    assert len(vectors) == 2
    assert len(vectors[0]) == 32


def test_empty_text_returns_zero_vector():

    service = HashingEmbeddingService(dimension=16)

    assert service.embed_text("") == [0.0] * 16


def test_gemini_service_requires_api_key(monkeypatch):

    monkeypatch.setattr(
        "app.infrastructure.knowledge.embeddings.gemini_embedding_service.settings.GEMINI_API_KEY",
        "",
    )

    try:

        GeminiEmbeddingService(
            api_key="",
        )

    except ValueError as ex:
        assert "GEMINI_API_KEY" in str(ex)
    else:
        raise AssertionError(
            "Expected ValueError for missing API key"
        )
