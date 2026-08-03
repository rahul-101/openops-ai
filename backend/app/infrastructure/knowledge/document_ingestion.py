import re

from app.infrastructure.knowledge.knowledge_base_service import (
    KnowledgeBaseService,
)
from app.infrastructure.knowledge.models import (
    KnowledgeDocument,
    KnowledgeType,
)


class DocumentIngestionPipeline:
    """
    Ingests raw documents into the knowledge base.

    Pipeline stages:
    - parse raw content
    - chunk content into overlapping segments
    - generate embeddings per chunk
    - store vectors with metadata
    """

    def __init__(
        self,
        knowledge_base: KnowledgeBaseService,
        chunk_size: int = 200,
        chunk_overlap: int = 20,
    ) -> None:

        self.knowledge_base = knowledge_base
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def ingest(
        self,
        title: str,
        content: str,
        type_: KnowledgeType,
        source: str | None = None,
        metadata: dict | None = None,
    ) -> list[KnowledgeDocument]:

        parsed = self.parse(content)

        chunks = self.chunk(parsed)

        documents: list[KnowledgeDocument] = []

        for index, chunk in enumerate(chunks):

            chunk_title = title

            if len(chunks) > 1:
                chunk_title = (
                    f"{title} [chunk {index + 1}/{len(chunks)}]"
                )

            document = self.knowledge_base.store_document(
                title=chunk_title,
                content=chunk,
                type_=type_,
                metadata={
                    **(metadata or {}),
                    "chunk_index": index,
                    "chunk_count": len(chunks),
                },
                source=source,
            )

            documents.append(document)

        return documents

    # ==========================================================
    # Pipeline Stages
    # ==========================================================

    @staticmethod
    def parse(
        content: str,
    ) -> str:
        """
        Normalize raw document content.

        Strips markdown/code fences and collapses whitespace.
        """

        if not content:
            return ""

        text = re.sub(
            r"```.*?```",
            " ",
            content,
            flags=re.DOTALL,
        )

        text = re.sub(
            r"`[^`]*`",
            " ",
            text,
        )

        text = re.sub(
            r"[#*>_~]+",
            " ",
            text,
        )

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

    def chunk(
        self,
        content: str,
    ) -> list[str]:
        """
        Split content into overlapping word-based chunks.
        """

        words = content.split()

        if not words:
            return []

        chunks: list[str] = []

        index = 0

        while index < len(words):

            end = min(
                index + self.chunk_size,
                len(words),
            )

            chunks.append(
                " ".join(words[index:end])
            )

            if end >= len(words):
                break

            index = max(
                0,
                end - self.chunk_overlap,
            )

        return chunks
