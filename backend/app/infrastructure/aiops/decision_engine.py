from dataclasses import dataclass, field
from datetime import datetime

from app.infrastructure.aiops.event_ingestion import (
    NormalizedEvent,
)
from app.infrastructure.aiops.playbook_engine import (
    Playbook,
    PlaybookStep,
)
from app.infrastructure.aiops.risk_based_execution import (
    ExecutionPlan,
    RiskBasedExecutor,
)
from app.infrastructure.governance.models import (
    ActionDecision,
    RiskLevel,
)


@dataclass
class IncidentAnalysis:
    """
    Result of analyzing an incident event.
    """

    incident_id: str

    summary: str

    category: str = ""

    probable_cause: str = ""

    recommendation: str = ""

    confidence: float = 0.0

    analyzed_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class ToolAction:
    """
    A tool action selected for execution.
    """

    tool: str

    action: str

    parameters: dict = field(default_factory=dict)

    risk_level: RiskLevel = RiskLevel.MEDIUM

    decision: ActionDecision = (
        ActionDecision.APPROVAL_REQUIRED
    )

    approved: bool = False


@dataclass
class RemediationDecision:
    """
    The full autonomous decision for an incident.
    """

    incident_id: str

    analysis: IncidentAnalysis

    playbook: str | None = None

    actions: list[ToolAction] = field(
        default_factory=list
    )

    decided_at: datetime = field(
        default_factory=datetime.utcnow
    )

    @property
    def can_auto_execute(self) -> bool:
        """
        True when all selected actions are approved.
        """

        if not self.actions:
            return False

        return all(
            action.approved
            for action in self.actions
        )


class AutonomousDecisionEngine:
    """
    Analyzes an incident, selects a remediation playbook,
    chooses the tool actions and decides whether they can
    auto execute based on risk.
    """

    def __init__(
        self,
        risk_executor: RiskBasedExecutor,
    ) -> None:

        self.risk_executor = risk_executor

    def analyze(
        self,
        event: NormalizedEvent,
    ) -> IncidentAnalysis:
        """
        Produces a rule based incident analysis.
        """

        description = (
            event.description or event.title
        ).lower()

        cause, recommendation = self._diagnose(
            description,
        )

        return IncidentAnalysis(
            incident_id=event.event_id,
            summary=f"{event.title}",
            category=self._categorize(description),
            probable_cause=cause,
            recommendation=recommendation,
            confidence=self._confidence(description),
        )

    def decide(
        self,
        event: NormalizedEvent,
        playbook: Playbook | None,
    ) -> RemediationDecision:
        """
        Selects the tool actions for an event and evaluates
        each against the risk policy.
        """

        analysis = self.analyze(event)

        actions: list[ToolAction] = []

        if playbook is not None:

            for step in playbook.steps:
                actions.append(
                    self._evaluate_step(
                        event.event_id,
                        step,
                    )
                )

        return RemediationDecision(
            incident_id=event.event_id,
            analysis=analysis,
            playbook=(
                playbook.name if playbook else None
            ),
            actions=actions,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def _evaluate_step(
        self,
        incident_id: str,
        step: PlaybookStep,
    ) -> ToolAction:

        action_name = f"tool.{step.tool}.{step.action}"

        plan: ExecutionPlan = (
            self.risk_executor.evaluate(action_name)
        )

        return ToolAction(
            tool=step.tool,
            action=step.action,
            parameters=dict(step.parameters),
            risk_level=plan.risk_level,
            decision=plan.decision,
            approved=plan.approved,
        )

    @staticmethod
    def _categorize(
        description: str,
    ) -> str:

        if any(
            word in description
            for word in ("cpu", "memory", "disk", "latency")
        ):
            return "infrastructure"

        if any(
            word in description
            for word in ("crash", "error", "exception")
        ):
            return "application"

        return "unknown"

    @staticmethod
    def _diagnose(
        description: str,
    ) -> tuple[str, str]:

        if "crash" in description or "restart" in description:

            return (
                "Service crash loop detected.",
                "Restart the deployment.",
            )

        if "cpu" in description:

            return (
                "CPU resource exhaustion.",
                "Scale up or restart the affected node.",
            )

        if "memory" in description:

            return (
                "Memory resource exhaustion.",
                "Restart the pod to reclaim memory.",
            )

        if "latency" in description or "slow" in description:

            return (
                "Degraded service latency.",
                "Investigate downstream dependencies.",
            )

        return (
            "No known root cause signature.",
            "Escalate for manual investigation.",
        )

    @staticmethod
    def _confidence(
        description: str,
    ) -> float:

        known = (
            "crash",
            "restart",
            "cpu",
            "memory",
            "latency",
            "slow",
        )

        matches = sum(
            1
            for word in known
            if word in description
        )

        if matches >= 2:
            return 0.9

        if matches == 1:
            return 0.7

        return 0.3
