import hashlib
import math
from abc import ABC, abstractmethod


class EmbeddingService(ABC):
    """
    Contract for embedding generation.

    Keeps provider abstraction: any embedding provider
    (Gemini, local hashing, etc.) can be plugged in.
    """

    @abstractmethod
    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        raise NotImplementedError

    @abstractmethod
    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        raise NotImplementedError


class HashingEmbeddingService(EmbeddingService):
    """
    Deterministic, dependency-free embedding implementation.

    Intended for local development and tests. Produces
    normalized, fixed-dimension vectors from text hashing.
    """

    DIMENSION = 64

    def __init__(
        self,
        dimension: int = DIMENSION,
    ) -> None:
        self.dimension = dimension

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        return self._embed(text)

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [
            self._embed(text)
            for text in texts
        ]

    # ==========================================================
    # Helpers
    # ==========================================================

    def _embed(
        self,
        text: str,
    ) -> list[float]:

        vector = [0.0] * self.dimension

        tokens = text.lower().split()

        if not tokens:
            return vector

        for token in tokens:

            digest = hashlib.md5(
                token.encode("utf-8")
            ).hexdigest()

            index = int(digest[:8], 16) % self.dimension

            sign = -1.0 if int(digest[8:12], 16) % 2 else 1.0

            vector[index] += sign

        norm = math.sqrt(
            sum(value * value for value in vector)
        ) or 1.0

        return [
            value / norm
            for value in vector
        ]
