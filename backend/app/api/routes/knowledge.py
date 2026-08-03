from typing import Literal

from fastapi import APIRouter, Depends, HTTPException

from app.infrastructure.dependencies import (
    get_document_ingestion_pipeline,
    get_incident_memory_service,
    get_knowledge_base_service,
)
from app.infrastructure.knowledge.document_ingestion import (
    DocumentIngestionPipeline,
)
from app.infrastructure.knowledge.incident_memory_service import (
    IncidentMemoryService,
)
from app.infrastructure.knowledge.knowledge_base_service import (
    KnowledgeBaseService,
)
from app.infrastructure.knowledge.models import (
    IncidentMemory,
    KnowledgeType,
)

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Base"],
)


# ==========================================================
# Store
# ==========================================================


@router.post(
    "/runbooks",
    summary="Store a runbook in the knowledge base",
)
def store_runbook(
    body: dict,
    knowledge: KnowledgeBaseService = Depends(
        get_knowledge_base_service,
    ),
):

    if not body.get("title") or not body.get("content"):
        raise HTTPException(
            status_code=422,
            detail="Both 'title' and 'content' are required.",
        )

    document = knowledge.store_runbook(
        title=body["title"],
        content=body["content"],
        metadata=body.get("metadata", {}) or {},
    )

    return _document_response(document)


@router.post(
    "/resolutions",
    summary="Store a resolution in the knowledge base",
)
def store_resolution(
    body: dict,
    knowledge: KnowledgeBaseService = Depends(
        get_knowledge_base_service,
    ),
):

    if not body.get("title") or not body.get("content"):
        raise HTTPException(
            status_code=422,
            detail="Both 'title' and 'content' are required.",
        )

    document = knowledge.store_resolution(
        title=body["title"],
        content=body["content"],
        metadata=body.get("metadata", {}) or {},
    )

    return _document_response(document)


@router.post(
    "/incidents",
    summary="Store an incident as knowledge",
)
def store_incident(
    body: dict,
    knowledge: KnowledgeBaseService = Depends(
        get_knowledge_base_service,
    ),
):

    if not body.get("title") or not body.get("description"):
        raise HTTPException(
            status_code=422,
            detail=(
                "Both 'title' and 'description' are required."
            ),
        )

    document = knowledge.store_incident(
        title=body["title"],
        description=body["description"],
        resolution=body.get("resolution"),
        category=body.get("category"),
        severity=body.get("severity"),
    )

    return _document_response(document)


# ============================================================
# Ingestion
# ============================================================

_TYPE_TYPES = {
    t.value: t
    for t in KnowledgeType
}


@router.post(
    "/ingest",
    summary="Ingest a document (parsed and chunked)",
)
def ingest_document(
    body: dict,
    pipeline: DocumentIngestionPipeline = Depends(
        get_document_ingestion_pipeline,
    ),
):

    if not body.get("title") or not body.get("content"):
        raise HTTPException(
            status_code=422,
            detail="Both 'title' and 'content' are required.",
        )

    type_value = body.get(
        "type",
        KnowledgeType.RUNBOOK.value,
    )

    type_ = _TYPE_TYPES.get(type_value)

    if type_ is None:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported type '{type_value}'.",
        )

    documents = pipeline.ingest(
        title=body["title"],
        content=body["content"],
        type_=type_,
        source=body.get("source"),
        metadata=body.get("metadata", {}) or {},
    )

    return [
        _document_response(d)
        for d in documents
    ]


# ============================================================
# Search
# ============================================================


@router.get(
    "/search",
    summary="Semantic search over the knowledge base",
)
def search_knowledge(
    q: str,
    limit: int = 5,
    type: Literal[
        "incident",
        "runbook",
        "resolution",
        "troubleshooting_document",
    ]
    | None = None,
    knowledge: KnowledgeBaseService = Depends(
        get_knowledge_base_service,
    ),
):

    type_ = _TYPE_TYPES.get(type) if type else None

    results = knowledge.search(
        query=q,
        limit=limit,
        type_=type_,
    )

    return [
        {
            "document_id": r.document_id,
            "title": r.title,
            "content": r.content,
            "type": r.type,
            "score": r.score,
        }
        for r in results
    ]


# ============================================================
# Documents
# ============================================================


@router.get(
    "/documents/{document_id}",
    summary="Get a knowledge document by id",
)
def get_document(
    document_id: str,
    knowledge: KnowledgeBaseService = Depends(
        get_knowledge_base_service,
    ),
):

    document = knowledge.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Knowledge document '{document_id}' not found."
            ),
        )

    return _document_response(document)


@router.delete(
    "/documents/{document_id}",
    summary="Delete a knowledge document by id",
)
def delete_document(
    document_id: str,
    knowledge: KnowledgeBaseService = Depends(
        get_knowledge_base_service,
    ),
):

    document = knowledge.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Knowledge document '{document_id}' not found."
            ),
        )

    knowledge.delete(document_id)

    return {"deleted": document_id}


# ============================================================
# Incident Memory
# ============================================================


@router.post(
    "/memory",
    summary="Save incident memory (resolved outcome)",
)
def save_incident_memory(
    body: dict,
    memory_service: IncidentMemoryService = Depends(
        get_incident_memory_service,
    ),
):

    if not body.get("incident_id"):
        raise HTTPException(
            status_code=422,
            detail="'incident_id' is required.",
        )

    memory = memory_service.save(
        incident_id=body["incident_id"],
        root_cause=body.get("root_cause", ""),
        recommendation=body.get("recommendation", ""),
        final_resolution=body.get("final_resolution", ""),
        human_feedback=body.get("human_feedback"),
    )

    return _memory_response(memory)


@router.get(
    "/memory/{incident_id}",
    summary="Get incident memory",
)
def get_incident_memory(
    incident_id: str,
    memory_service: IncidentMemoryService = Depends(
        get_incident_memory_service,
    ),
):

    memory = memory_service.get(incident_id)

    if memory is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No memory for incident '{incident_id}'."
            ),
        )

    return _memory_response(memory)


# ============================================================
# Helpers
# ============================================================


def _document_response(document) -> dict:
    return {
        "id": document.id,
        "title": document.title,
        "content": document.content,
        "type": document.type.value,
        "source": document.source,
        "metadata": document.metadata,
        "created_at": (
            document.created_at.isoformat()
            if document.created_at
            else None
        ),
    }


def _memory_response(
    memory: IncidentMemory,
) -> dict:
    return {
        "incident_id": memory.incident_id,
        "root_cause": memory.root_cause,
        "recommendation": memory.recommendation,
        "final_resolution": memory.final_resolution,
        "human_feedback": memory.human_feedback,
    }
