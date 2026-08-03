from fastapi import APIRouter, Depends, HTTPException

from app.infrastructure.aiops.decision_engine import (
    AutonomousDecisionEngine,
)
from app.infrastructure.aiops.event_ingestion import (
    EventIngestionEngine,
    RawAlert,
)
from app.infrastructure.aiops.lifecycle import (
    IncidentLifecycleOrchestrator,
)
from app.infrastructure.aiops.playbook_engine import (
    RemediationPlaybookEngine,
)
from app.infrastructure.aiops.risk_based_execution import (
    RiskBasedExecutor,
)
from app.infrastructure.dependencies import (
    get_autonomous_decision_engine,
    get_event_ingestion_engine,
    get_incident_lifecycle_orchestrator,
    get_playbook_engine,
    get_risk_based_executor,
)

router = APIRouter(
    prefix="/aiops",
    tags=["AI Ops"],
)


# ==========================================================
# Event Ingestion
# ==========================================================


@router.post(
    "/alerts/ingest",
    summary="Ingest a raw alert from a monitoring system",
)
def ingest_alert(
    body: dict,
    ingestion: EventIngestionEngine = Depends(
        get_event_ingestion_engine,
    ),
):

    alert = RawAlert(
        source=body.get("source", ""),
        alert_id=body.get("alert_id", ""),
        title=body.get("title", ""),
        description=body.get("description", ""),
        severity=body.get("severity", "low"),
        service=body.get("service"),
        tags=body.get("tags", []) or [],
        metadata=body.get("metadata", {}) or {},
    )

    event = ingestion.ingest_alert(alert)

    return {
        "event_id": event.event_id,
        "source": event.source,
        "title": event.title,
        "severity": event.severity.value,
        "service": event.service,
    }


@router.get(
    "/events",
    summary="List normalized incident events",
)
def list_events(
    source: str | None = None,
    limit: int | None = None,
    ingestion: EventIngestionEngine = Depends(
        get_event_ingestion_engine,
    ),
):

    return [
        {
            "event_id": e.event_id,
            "source": e.source,
            "title": e.title,
            "severity": e.severity.value,
            "service": e.service,
        }
        for e in ingestion.list(
            source=source,
            limit=limit,
        )
    ]


# ==========================================================
# Autonomous Decision
# ==========================================================


@router.post(
    "/decide",
    summary="Analyze an event and select remediation",
)
def decide(
    body: dict,
    ingestion: EventIngestionEngine = Depends(
        get_event_ingestion_engine,
    ),
    decision_engine: AutonomousDecisionEngine = Depends(
        get_autonomous_decision_engine,
    ),
    playbooks: RemediationPlaybookEngine = Depends(
        get_playbook_engine,
    ),
):

    event = ingestion.get(body.get("event_id", ""))

    if event is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event '{body.get('event_id')}' not found.",
        )

    playbook = playbooks.find(event)

    decision = decision_engine.decide(event, playbook)

    return {
        "incident_id": decision.incident_id,
        "summary": decision.analysis.summary,
        "category": decision.analysis.category,
        "probable_cause": (
            decision.analysis.probable_cause
        ),
        "recommendation": (
            decision.analysis.recommendation
        ),
        "confidence": decision.analysis.confidence,
        "playbook": decision.playbook,
        "can_auto_execute": decision.can_auto_execute,
        "actions": [
            {
                "tool": a.tool,
                "action": a.action,
                "risk_level": a.risk_level.value,
                "decision": a.decision.value,
                "approved": a.approved,
            }
            for a in decision.actions
        ],
    }


# ==========================================================
# Risk Policy
# ==========================================================


@router.get(
    "/risk/actions",
    summary="List registered actions and risk levels",
)
def list_risk_actions(
    risk: RiskBasedExecutor = Depends(get_risk_based_executor),
):

    return {
        action: risk_level.value
        for action, risk_level in risk.actions().items()
    }


# ==========================================================
# Playbooks
# ==========================================================


@router.get(
    "/playbooks",
    summary="List registered remediation playbooks",
)
def list_playbooks(
    playbooks: RemediationPlaybookEngine = Depends(
        get_playbook_engine,
    ),
):

    return [
        {
            "name": p.name,
            "description": p.description,
            "version": p.version,
            "steps": [
                {
                    "name": s.name,
                    "tool": s.tool,
                    "action": s.action,
                    "risk_level": s.risk_level,
                }
                for s in p.steps
            ],
        }
        for p in playbooks.list()
    ]


# ==========================================================
# E2E Lifecycle
# ==========================================================


@router.post(
    "/lifecycle/run",
    summary="Run the end-to-end incident lifecycle",
)
async def run_lifecycle(
    body: dict,
    orchestrator: IncidentLifecycleOrchestrator = Depends(
        get_incident_lifecycle_orchestrator,
    ),
):

    alert = RawAlert(
        source=body.get("source", ""),
        alert_id=body.get("alert_id", ""),
        title=body.get("title", ""),
        description=body.get("description", ""),
        severity=body.get("severity", "low"),
        service=body.get("service"),
        tags=body.get("tags", []) or [],
        metadata=body.get("metadata", {}) or {},
    )

    incident = await orchestrator.handle_alert(alert)

    return {
        "incident_id": incident.incident_id,
        "status": incident.status.value,
        "servicenow_updated": incident.servicenow_updated,
        "learning_recorded": incident.learning_recorded,
        "steps": [
            {
                "stage": s.stage,
                "status": s.status,
                "details": s.details,
            }
            for s in incident.steps
        ],
    }


@router.get(
    "/lifecycle/{incident_id}",
    summary="Get an incident lifecycle record",
)
def get_lifecycle(
    incident_id: str,
    orchestrator: IncidentLifecycleOrchestrator = Depends(
        get_incident_lifecycle_orchestrator,
    ),
):

    incident = orchestrator.get(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail=f"Lifecycle '{incident_id}' not found.",
        )

    return {
        "incident_id": incident.incident_id,
        "status": incident.status.value,
        "servicenow_updated": incident.servicenow_updated,
        "learning_recorded": incident.learning_recorded,
        "steps": [
            {
                "stage": s.stage,
                "status": s.status,
                "details": s.details,
            }
            for s in incident.steps
        ],
    }


@router.get(
    "/lifecycle",
    summary="List incident lifecycle records",
)
def list_lifecycle(
    orchestrator: IncidentLifecycleOrchestrator = Depends(
        get_incident_lifecycle_orchestrator,
    ),
):

    return [
        {
            "incident_id": i.incident_id,
            "status": i.status.value,
            "servicenow_updated": i.servicenow_updated,
        }
        for i in orchestrator.list()
    ]
