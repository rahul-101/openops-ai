from google import genai

from app.core.config import settings
from app.infrastructure.knowledge.embedding_service import (
    EmbeddingService,
)


class GeminiEmbeddingService(EmbeddingService):
    """
    Google Gemini embedding provider.
    """

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:

        self.model = model or settings.EMBEDDING_MODEL

        api_key = api_key or settings.GEMINI_API_KEY

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(api_key=api_key)

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        return self.embed_texts([text])[0]

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
        )

        return [
            embedding.values
            for embedding in response.embeddings
        ]
