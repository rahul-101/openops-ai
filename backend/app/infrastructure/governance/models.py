from enum import Enum


class RiskLevel(str, Enum):
    """
    Risk classification used by the approval policy engine.
    """

    LOW = "low"

    MEDIUM = "medium"

    HIGH = "high"


class ActionDecision(str, Enum):
    """
    Outcome of evaluating an action against policy.
    """

    AUTO_EXECUTED = "auto_executed"

    APPROVAL_REQUIRED = "approval_required"

    BLOCKED = "blocked"


class Permission(str, Enum):
    """
    Fine-grained permissions used by RBAC.
    """

    INCIDENT_READ = "incident:read"

    INCIDENT_WRITE = "incident:write"

    AI_EXECUTE = "ai:execute"

    TOOL_EXECUTE = "tool:execute"

    APPROVAL_APPROVE = "approval:approve"

    GOVERNANCE_READ = "governance:read"

    ADMIN = "admin:*"
