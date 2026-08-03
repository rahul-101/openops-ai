from fastapi import APIRouter, Depends, HTTPException

from app.infrastructure.governance.approval_policy import (
    ApprovalPolicyEngine,
)
from app.infrastructure.governance.audit_log import (
    AuditLogService,
)
from app.infrastructure.governance.data_privacy import (
    DataPrivacyService,
)
from app.infrastructure.governance.exceptions import (
    GovernanceError,
)
from app.infrastructure.governance.model_governance import (
    ModelGovernanceService,
)
from app.infrastructure.governance.models import Permission
from app.infrastructure.governance.prompt_registry import (
    PromptRegistry,
)
from app.infrastructure.governance.rbac import RbacService
from app.infrastructure.dependencies import (
    get_approval_policy_engine,
    get_audit_log_service,
    get_data_privacy_service,
    get_model_governance_service,
    get_prompt_registry,
    get_rbac_service,
)

router = APIRouter(
    prefix="/governance",
    tags=["Governance"],
)


# ==========================================================
# RBAC
# ==========================================================


@router.post(
    "/rbac/check",
    summary="Check a user permission",
)
def check_permission(
    body: dict,
    rbac: RbacService = Depends(get_rbac_service),
):

    permission = Permission(body.get("permission"))

    return {
        "username": body.get("username"),
        "permission": permission.value,
        "authorized": rbac.has_permission(
            body.get("username"),
            permission,
        ),
    }


# ==========================================================
# Audit Log
# ==========================================================


@router.get(
    "/audit",
    summary="Query AI audit log",
)
def get_audit_log(
    user: str | None = None,
    action: str | None = None,
    incident_id: str | None = None,
    decision: str | None = None,
    limit: int | None = None,
    audit: AuditLogService = Depends(get_audit_log_service),
):

    return audit.list(
        user=user,
        action=action,
        incident_id=incident_id,
        decision=decision,
        limit=limit,
    )


# ==========================================================
# Approval Policy
# ==========================================================


@router.get(
    "/approval-policy/actions",
    summary="List registered actions and risk levels",
)
def list_actions(
    engine: ApprovalPolicyEngine = Depends(
        get_approval_policy_engine,
    ),
):

    return {
        action: risk.value
        for action, risk in engine.actions().items()
    }


@router.get(
    "/approval-policy/{action}/decision",
    summary="Evaluate an action against policy",
)
def evaluate_action(
    action: str,
    engine: ApprovalPolicyEngine = Depends(
        get_approval_policy_engine,
    ),
):

    return {
        "action": action,
        "risk_level": engine.risk_level(action).value,
        "decision": engine.evaluate(action).value,
    }


# ==========================================================
# Prompt Registry
# ==========================================================


@router.get(
    "/prompts/{name}",
    summary="Get active prompt version",
)
def get_active_prompt(
    name: str,
    registry: PromptRegistry = Depends(get_prompt_registry),
):

    try:

        prompt = registry.get_active(name)

    except GovernanceError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex),
        )

    return {
        "name": prompt.name,
        "version": prompt.version,
        "active": prompt.active,
        "metadata": prompt.metadata,
        "content": prompt.content,
    }


# ==========================================================
# Model Governance
# ==========================================================


@router.get(
    "/models/stats",
    summary="Model usage and cost statistics",
)
def model_stats(
    provider: str | None = None,
    governance: ModelGovernanceService = Depends(
        get_model_governance_service,
    ),
):

    return governance.get_stats(provider=provider)


# ==========================================================
# Data Privacy
# ==========================================================


@router.post(
    "/privacy/mask",
    summary="Detect and mask sensitive data",
)
def mask_sensitive_data(
    body: dict,
    privacy: DataPrivacyService = Depends(
        get_data_privacy_service,
    ),
):

    masked, detected = privacy.mask_sensitive(
        body.get("text", "")
    )

    return {
        "masked": masked,
        "detected": detected,
    }
