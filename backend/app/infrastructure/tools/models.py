from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class ToolCategory(str, Enum):
    """
    Tool category used for registry organization.
    """

    SERVICENOW = "servicenow"

    JIRA = "jira"

    AWS = "aws"

    AZURE = "azure"

    KUBERNETES = "kubernetes"

    SLACK = "slack"

    TEAMS = "teams"

    DATABASE = "database"


@dataclass(frozen=True)
class ToolMetadata:
    """
    Static metadata describing a tool.
    """

    name: str

    category: ToolCategory

    description: str

    version: str = "1.0.0"

    parameters: dict = field(default_factory=dict)


@dataclass
class ToolExecutionContext:
    """
    Execution context for a tool call.
    """

    incident_id: str | None = None

    workflow_id: str | None = None

    actor: str | None = None


@dataclass
class ToolResult:
    """
    Result of a tool execution.
    """

    tool: str

    success: bool

    data: dict = field(default_factory=dict)

    error: str | None = None


class ApprovalStatus(str, Enum):
    """
    Lifecycle of an approval request.
    """

    PENDING = "pending"

    APPROVED = "approved"

    REJECTED = "rejected"

    EXECUTED = "executed"


@dataclass
class ApprovalRequest:
    """
    A request to authorize a risky tool action.
    """

    tool_name: str

    parameters: dict

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    context: dict | None = field(default_factory=dict)

    status: ApprovalStatus = ApprovalStatus.PENDING

    requested_by: str | None = None

    approved_by: str | None = None

    reason: str | None = None

    result: dict | None = None

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )
