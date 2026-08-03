from fastapi import APIRouter, Depends, HTTPException

from app.infrastructure.dependencies import (
    get_business_impact_analysis,
    get_chaos_testing_simulator,
    get_dependency_intelligence,
    get_incident_correlation,
    get_remediation_rollback,
    get_root_cause_graph,
    get_workflow_recovery,
)
from app.infrastructure.reliability.business_impact import (
    BusinessImpactAnalysis,
)
from app.infrastructure.reliability.chaos_simulator import (
    ChaosTestingSimulator,
    FailureType,
)
from app.infrastructure.reliability.dependency_intelligence import (
    DependencyIntelligence,
)
from app.infrastructure.reliability.incident_correlation import (
    IncidentCorrelation,
)
from app.infrastructure.reliability.rollback import (
    RemediationRollback,
)
from app.infrastructure.reliability.root_cause_graph import (
    RootCauseGraph,
)
from app.infrastructure.reliability.workflow_recovery import (
    WorkflowRecovery,
)

router = APIRouter(
    prefix="/reliability",
    tags=["Reliability"],
)


# ==========================================================
# Workflow Recovery
# ==========================================================


@router.post(
    "/workflows/begin",
    summary="Begin a recoverable workflow",
)
def begin_workflow(
    body: dict,
    recovery: WorkflowRecovery = Depends(get_workflow_recovery),
):

    record = recovery.begin(
        workflow_id=body.get("workflow_id"),
        steps=body.get("steps", []) or [],
    )

    return {
        "workflow_id": record.workflow_id,
        "status": record.status.value,
        "steps": list(record.steps.keys()),
    }


@router.post(
    "/workflows/{workflow_id}/checkpoint",
    summary="Checkpoint a completed workflow step",
)
def checkpoint_workflow(
    workflow_id: str,
    body: dict,
    recovery: WorkflowRecovery = Depends(get_workflow_recovery),
):

    try:

        checkpoint = recovery.checkpoint(
            workflow_id=workflow_id,
            step=body.get("step"),
            output=body.get("output") or {},
        )

    except KeyError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex),
        )

    return {
        "workflow_id": checkpoint.workflow_id,
        "step": checkpoint.step,
    }


@router.get(
    "/workflows/{workflow_id}/resume",
    summary="Get steps to resume a workflow",
)
def resume_workflow(
    workflow_id: str,
    recovery: WorkflowRecovery = Depends(get_workflow_recovery),
):

    try:

        return {
            "workflow_id": workflow_id,
            "remaining_steps": recovery.resume(workflow_id),
        }

    except KeyError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex),
        )


# ==========================================================
# Remediation Rollback
# ==========================================================


@router.post(
    "/rollback/begin",
    summary="Begin a remediation rollback record",
)
def begin_rollback(
    body: dict,
    rollback: RemediationRollback = Depends(get_remediation_rollback),
):

    record = rollback.begin(
        incident_id=body.get("incident_id"),
    )

    return {
        "record_id": record.id,
        "incident_id": record.incident_id,
    }


# ==========================================================
# Root Cause Graph
# ==========================================================


@router.post(
    "/rca/{incident_id}/factors",
    summary="Add a root cause factor",
)
def add_rca_factor(
    incident_id: str,
    body: dict,
    graph: RootCauseGraph = Depends(get_root_cause_graph),
):

    factor = graph.add_factor(
        incident_id,
        factor=body.get("factor"),
        service=body.get("service"),
        weight=body.get("weight", 1.0),
        evidence=body.get("evidence", ""),
    )

    return {
        "incident_id": incident_id,
        "factor": factor.factor,
        "service": factor.service,
        "weight": factor.weight,
    }


@router.get(
    "/rca/{incident_id}/ranked",
    summary="Rank root causes by weight",
)
def ranked_root_causes(
    incident_id: str,
    graph: RootCauseGraph = Depends(get_root_cause_graph),
):

    factors = graph.rank_root_causes(incident_id)

    return [
        {
            "factor": f.factor,
            "service": f.service,
            "weight": f.weight,
            "evidence": f.evidence,
        }
        for f in factors
    ]


# ==========================================================
# Dependency Intelligence
# ==========================================================


@router.post(
    "/dependencies",
    summary="Register a service dependency",
)
def register_dependency(
    body: dict,
    intelligence: DependencyIntelligence = Depends(
        get_dependency_intelligence,
    ),
):

    entry = intelligence.register_dependency(
        dependent=body.get("dependent"),
        dependency=body.get("dependency"),
        critical=body.get("critical", False),
    )

    return {
        "dependent": entry.dependent,
        "dependency": entry.dependency,
        "critical": entry.critical,
    }


@router.get(
    "/dependencies/{service}/impact",
    summary="Impact analysis for a failing service",
)
def impact_analysis(
    service: str,
    intelligence: DependencyIntelligence = Depends(
        get_dependency_intelligence,
    ),
):

    impact = intelligence.impact_analysis(service)

    return {
        "service": impact.service,
        "directly_affected": impact.directly_affected,
        "transitively_affected": (
            impact.transitively_affected
        ),
        "critical_dependencies": (
            impact.critical_dependencies
        ),
    }


# ==========================================================
# Incident Correlation
# ==========================================================


@router.post(
    "/correlate",
    summary="Check an incident for duplicates or relations",
)
def correlate_incident(
    body: dict,
    correlation: IncidentCorrelation = Depends(
        get_incident_correlation,
    ),
):

    result = correlation.correlate(
        incident_id=body.get("incident_id"),
        source=body.get("source", ""),
        service=body.get("service"),
        tags=body.get("tags", []) or [],
        title=body.get("title", ""),
    )

    return {
        "incident_id": result.incident_id,
        "duplicate": result.duplicate,
        "group_id": result.group_id,
        "matches": result.matches,
        "method": (
            result.method.value if result.method else None
        ),
    }


# ==========================================================
# Business Impact Analysis
# ==========================================================


@router.post(
    "/impact/analyze",
    summary="Calculate business impact for an incident",
)
def analyze_impact(
    body: dict,
    analysis: BusinessImpactAnalysis = Depends(
        get_business_impact_analysis,
    ),
):

    impact = analysis.analyze(
        incident_id=body.get("incident_id"),
        affected_users=body.get("affected_users", 0),
        revenue_at_risk=body.get("revenue_at_risk", 0.0),
        response_time_sla_minutes=body.get(
            "response_time_sla_minutes",
            60,
        ),
        elapsed_minutes=body.get("elapsed_minutes", 0),
    )

    return {
        "incident_id": impact.incident_id,
        "severity": impact.severity.value,
        "sla_status": impact.sla_status.value,
        "score": impact.score,
    }


# ==========================================================
# Chaos Testing Simulator
# ==========================================================


@router.post(
    "/chaos/inject",
    summary="Inject a simulated failure",
)
def inject_failure(
    body: dict,
    simulator: ChaosTestingSimulator = Depends(
        get_chaos_testing_simulator,
    ),
):

    experiment = simulator.inject_failure(
        name=body.get("name", "chaos"),
        target_service=body.get("target_service"),
        failure_type=FailureType(
            body.get("failure_type")
        ),
        duration_seconds=body.get(
            "duration_seconds",
            60,
        ),
    )

    return {
        "experiment_id": experiment.id,
        "name": experiment.name,
        "target_service": experiment.target_service,
        "failure_type": experiment.failure_type.value,
    }


@router.post(
    "/chaos/{experiment_id}/validate",
    summary="Validate autonomous recovery",
)
def validate_recovery(
    experiment_id: str,
    body: dict,
    simulator: ChaosTestingSimulator = Depends(
        get_chaos_testing_simulator,
    ),
):

    try:

        resolved = simulator.validate_recovery(
            experiment_id,
            body.get("resolved", False),
        )

    except KeyError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex),
        )

    return {
        "experiment_id": experiment_id,
        "resolved": resolved,
    }


@router.get(
    "/chaos/recovery-rate",
    summary="Autonomous recovery rate",
)
def recovery_rate(
    simulator: ChaosTestingSimulator = Depends(
        get_chaos_testing_simulator,
    ),
):

    return {
        "recovery_rate": simulator.get_recovery_rate(),
    }
