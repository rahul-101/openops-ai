from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class AgentStatus(str, Enum):
    """
    Execution outcome of a single agent.
    """

    SUCCESS = "success"

    FAILURE = "failure"

    SKIPPED = "skipped"


@dataclass
class AgentResult:
    """
    Result produced by an agent execution.
    """

    agent: str

    status: AgentStatus

    output: dict = field(default_factory=dict)

    error: str | None = None

    duration_ms: float = 0.0

    executed_at: datetime = field(
        default_factory=datetime.utcnow
    )
