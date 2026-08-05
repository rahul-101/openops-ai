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
    get_playbook_engine,
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
# Playbooks
# ==========================================================


@router.get(
    "/playbooks",
    summary="List registered remediation playbooks",
)
def list_playbooks(
    playbooks: RemediationPlaybookEngine = Depends(get_playbook_engine),
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
                    "auto_execute": s.auto_execute,
                }
                for s in p.steps
            ],
        }
        for p in playbooks.list()
    ]


@router.post(
    "/playbooks",
    summary="Create or update a playbook",
)
def save_playbook(
    body: dict,
    playbooks: RemediationPlaybookEngine = Depends(get_playbook_engine),
):

    import yaml

    content = body.get("yaml_content", "")
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Missing 'yaml_content' in request body.",
        )

    try:
        playbook = playbooks.load_yaml(content)
    except Exception as ex:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid playbook YAML: {str(ex)}",
        )

    return {
        "name": playbook.name,
        "version": playbook.version,
        "description": playbook.description,
        "steps_count": len(playbook.steps),
    }


@router.get(
    "/playbooks/{name}",
    summary="Get a specific playbook",
)
def get_playbook(
    name: str,
    playbooks: RemediationPlaybookEngine = Depends(get_playbook_engine),
):

    playbook = playbooks.get(name)
    if playbook is None:
        raise HTTPException(
            status_code=404,
            detail=f"Playbook '{name}' not found.",
        )

    return {
        "name": playbook.name,
        "description": playbook.description,
        "version": playbook.version,
        "source": playbook.match.source,
        "severities": playbook.match.severities,
        "tags": playbook.match.tags,
        "steps": [
            {
                "name": s.name,
                "tool": s.tool,
                "action": s.action,
                "parameters": s.parameters,
                "risk_level": s.risk_level,
                "auto_execute": s.auto_execute,
            }
            for s in playbook.steps
        ],
        "created_at": playbook.created_at.isoformat(),
    }


@router.delete(
    "/playbooks/{name}",
    summary="Remove a playbook",
)
def delete_playbook(
    name: str,
    playbooks: RemediationPlaybookEngine = Depends(get_playbook_engine),
):

    playbook = playbooks.get(name)
    if playbook is None:
        raise HTTPException(
            status_code=404,
            detail=f"Playbook '{name}' not found.",
        )

    playbooks.clear()

    return {"message": f"Playbook '{name}' removed."}


@router.post(
    "/playbooks/yaml-validate",
    summary="Validate playbook YAML content",
)
def validate_playbook_yaml(
    body: dict,
):

    import yaml

    content = body.get("yaml_content", "")
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Missing 'yaml_content' in request body.",
        )

    try:
        data = yaml.safe_load(content)

        required = ["name", "description", "steps"]
        for field in required:
            if field not in data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}",
                )

        return {
            "valid": True,
            "name": data.get("name"),
            "version": data.get("version", "1.0.0"),
            "steps_count": len(data.get("steps", [])),
        }

    except yaml.YAMLError as ex:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid YAML: {str(ex)}",
        )


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
