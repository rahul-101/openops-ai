from fastapi import APIRouter, Depends, HTTPException

from app.infrastructure.aiops.event_ingestion import (
    EventIngestionEngine,
)
from app.infrastructure.dependencies import (
    get_dynamic_model_selector,
    get_event_ingestion_engine,
    get_decision_confidence_engine,
    get_decision_explainer,
    get_reasoning_history_store,
    get_reasoning_orchestrator,
    get_self_verification_layer,
)
from app.infrastructure.reasoning.confidence import (
    DecisionConfidenceEngine,
)
from app.infrastructure.reasoning.explanation import (
    DecisionExplainer,
)
from app.infrastructure.reasoning.history import (
    ReasoningHistoryStore,
)
from app.infrastructure.reasoning.model_selection import (
    DynamicModelSelector,
)
from app.infrastructure.reasoning.orchestrator import (
    ReasoningOrchestrator,
)
from app.infrastructure.reasoning.verification import (
    SelfVerificationLayer,
)

router = APIRouter(
    prefix="/reasoning",
    tags=["AI Reasoning"],
)


# ==========================================================
# Multi-Agent Reasoning
# ==========================================================


@router.post(
    "/reason",
    summary="Run the multi-agent reasoning workflow for an incident",
)
async def reason(
    body: dict,
    ingestion: EventIngestionEngine = Depends(
        get_event_ingestion_engine,
    ),
    orchestrator: ReasoningOrchestrator = Depends(
        get_reasoning_orchestrator,
    ),
):

    event = ingestion.get(body.get("event_id", ""))

    if event is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event '{body.get('event_id')}' not found.",
        )

    report = await orchestrator.reason(event)

    return {
        "incident_id": report.incident_id,
        "decision": report.decision,
        "confidence": report.confidence,
        "risk": report.risk,
        "validated": report.validated,
        "reasoning": list(report.reasoning),
        "evidence": list(report.evidence),
        "alternatives": list(report.alternatives),
        "explanation": dict(report.explanation),
        "agents_involved": list(report.agents_involved),
        "model_selection": dict(report.model_selection),
        "history_id": report.history_id,
    }


# ==========================================================
# Confidence Engine
# ==========================================================


@router.post(
    "/confidence",
    summary="Evaluate the confidence and risk of a decision",
)
def evaluate_confidence(
    body: dict,
    confidence_engine: DecisionConfidenceEngine = Depends(
        get_decision_confidence_engine,
    ),
):

    confidence = confidence_engine.evaluate(
        decision=body.get("decision", ""),
        factors=body.get("factors", []) or [],
        severity=body.get("severity", "low"),
        verified=body.get("verified", False),
    )

    return {
        "decision": confidence.decision,
        "confidence": round(confidence.confidence, 4),
        "risk": confidence.risk.value,
        "validated": confidence.validated,
        "reasoning": list(confidence.reasoning),
        "factors": [
            {
                "label": factor.label,
                "weight": factor.weight,
            }
            for factor in confidence.factors
        ],
    }


# ==========================================================
# Explanation
# ==========================================================


@router.post(
    "/explain",
    summary="Explain an autonomous decision",
)
def explain_decision(
    body: dict,
    explainer: DecisionExplainer = Depends(
        get_decision_explainer,
    ),
):

    explanation = explainer.explain(
        decision=body.get("decision", ""),
        why=body.get("why", ""),
        evidence=body.get("evidence", []) or [],
        alternatives=body.get("alternatives", []) or [],
        confidence=body.get("confidence", 0.0),
        risk=body.get("risk", "low"),
    )

    return {
        "decision": explanation.decision,
        "why": explanation.why,
        "evidence": list(explanation.evidence),
        "alternatives": list(explanation.alternatives),
        "confidence": explanation.confidence,
        "risk": explanation.risk,
    }


# ==========================================================
# Self Verification
# ==========================================================


@router.post(
    "/verify",
    summary="Validate a recommendation before execution",
)
def verify_recommendation(
    body: dict,
    verification: SelfVerificationLayer = Depends(
        get_self_verification_layer,
    ),
):

    result = verification.validate(
        recommendation=body.get("recommendation", ""),
        confidence=body.get("confidence", 0.0),
        risk=body.get("risk", "low"),
    )

    return {
        "status": result.status.value,
        "reason": result.reason,
        "checks": list(result.checks),
    }


# ==========================================================
# Dynamic Model Selection
# ==========================================================


@router.post(
    "/model/select",
    summary="Select a model based on task complexity",
)
def select_model(
    body: dict,
    selector: DynamicModelSelector = Depends(
        get_dynamic_model_selector,
    ),
):

    selection = selector.select(
        body.get("description", ""),
        severity=body.get("severity", "low"),
        tags=body.get("tags", []) or [],
    )

    if selection is None:
        raise HTTPException(
            status_code=404,
            detail="No model available for the task.",
        )

    return {
        "model": selection.model,
        "provider": selection.provider,
        "complexity": selection.complexity.value,
        "reason": selection.reason,
        "estimated_cost": selection.estimated_cost,
    }


@router.get(
    "/model/classify",
    summary="Classify the complexity of a task",
)
def classify_task(
    description: str,
    severity: str = "low",
    tags: str | None = None,
    selector: DynamicModelSelector = Depends(
        get_dynamic_model_selector,
    ),
):

    tag_list = (
        [tag for tag in tags.split(",") if tag]
        if tags
        else []
    )

    return {
        "complexity": selector.classify(
            description,
            severity=severity,
            tags=tag_list,
        ).value
    }


@router.get(
    "/model/models",
    summary="List registered model tiers",
)
def list_models(
    selector: DynamicModelSelector = Depends(
        get_dynamic_model_selector,
    ),
):

    return selector.list_models()


# ==========================================================
# Reasoning History
# ==========================================================


@router.get(
    "/history",
    summary="List reasoning history",
)
def list_history(
    limit: int | None = None,
    history: ReasoningHistoryStore = Depends(
        get_reasoning_history_store,
    ),
):

    return [
        {
            "incident_id": record.incident_id,
            "agents_involved": list(record.agents_involved),
            "decisions": list(record.decisions),
            "confidence": round(record.confidence, 4),
            "risk": record.risk,
            "outcome": record.outcome,
        }
        for record in history.list(limit=limit)
    ]


@router.get(
    "/history/{incident_id}",
    summary="Get reasoning history for an incident",
)
def get_history(
    incident_id: str,
    history: ReasoningHistoryStore = Depends(
        get_reasoning_history_store,
    ),
):

    record = history.get(incident_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"History '{incident_id}' not found.",
        )

    return {
        "incident_id": record.incident_id,
        "agents_involved": list(record.agents_involved),
        "decisions": list(record.decisions),
        "confidence": round(record.confidence, 4),
        "risk": record.risk,
        "outcome": record.outcome,
        "explanation": dict(record.explanation),
    }
