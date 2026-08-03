from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.infrastructure.aiops.decision_engine import (
    IncidentAnalysis,
    RemediationDecision,
)
from app.infrastructure.aiops.event_ingestion import (
    NormalizedEvent,
)


class AgentStatus(str, Enum):
    """
    Execution outcome of an AIOps agent.
    """

    SUCCESS = "success"

    FAILURE = "failure"


@dataclass
class AgentResult:
    """
    Result produced by a single AIOps agent.
    """

    agent: str

    status: AgentStatus

    output: dict = field(default_factory=dict)

    error: str | None = None

    executed_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class AIOpsContext:
    """
    Shared state passed through the agent execution flow.
    """

    event: NormalizedEvent

    analysis: IncidentAnalysis | None = None

    decision: RemediationDecision | None = None

    verification: dict = field(default_factory=dict)

    execution_results: list[dict] = field(
        default_factory=list
    )

    incident_id: str | None = None


class AIOpsAgent(ABC):
    """
    Contract for every AIOps execution agent.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    async def execute(
        self,
        context: AIOpsContext,
    ) -> AgentResult:
        raise NotImplementedError


class IncidentAgent(AIOpsAgent):
    """
    Captures the incident facts from the normalized event.
    """

    def __init__(self) -> None:

        super().__init__("incident")

    async def execute(
        self,
        context: AIOpsContext,
    ) -> AgentResult:

        context.incident_id = context.event.event_id

        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={
                "incident_id": context.event.event_id,
                "source": context.event.source,
                "title": context.event.title,
                "severity": context.event.severity.value,
                "service": context.event.service,
                "tags": list(context.event.tags),
            },
        )


class RcaAgent(AIOpsAgent):
    """
    Produces the root cause analysis for an incident.
    """

    def __init__(self) -> None:

        super().__init__("rca")

    async def execute(
        self,
        context: AIOpsContext,
    ) -> AgentResult:

        analysis = context.analysis

        if analysis is None:
            return AgentResult(
                agent=self.name,
                status=AgentStatus.FAILURE,
                error="No incident analysis available.",
            )

        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={
                "summary": analysis.summary,
                "category": analysis.category,
                "probable_cause": analysis.probable_cause,
                "confidence": analysis.confidence,
            },
        )


class PlannerAgent(AIOpsAgent):
    """
    Selects the remediation plan for an incident.
    """

    def __init__(self) -> None:

        super().__init__("planner")

    async def execute(
        self,
        context: AIOpsContext,
    ) -> AgentResult:

        decision = context.decision

        if decision is None:
            return AgentResult(
                agent=self.name,
                status=AgentStatus.FAILURE,
                error="No remediation decision available.",
            )

        actions = [
            {
                "tool": action.tool,
                "action": action.action,
                "risk_level": action.risk_level.value,
                "decision": action.decision.value,
                "approved": action.approved,
            }
            for action in decision.actions
        ]

        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={
                "playbook": decision.playbook,
                "recommendation": (
                    decision.analysis.recommendation
                ),
                "actions": actions,
                "can_auto_execute": (
                    decision.can_auto_execute
                ),
            },
        )


class ExecutionAgent(AIOpsAgent):
    """
    Executes the planned tool actions respecting the risk
    decision for each action.
    """

    def __init__(
        self,
        executor,
    ) -> None:

        super().__init__("execution")

        self.executor = executor

    async def execute(
        self,
        context: AIOpsContext,
    ) -> AgentResult:

        decision = context.decision

        if decision is None:
            return AgentResult(
                agent=self.name,
                status=AgentStatus.FAILURE,
                error="No remediation decision available.",
            )

        results: list[dict] = []

        failures = 0

        for action in decision.actions:

            result = await self._run_action(
                context,
                action,
            )

            results.append(result)

            if not result["success"]:
                failures += 1

        context.execution_results = results

        return AgentResult(
            agent=self.name,
            status=(
                AgentStatus.SUCCESS
                if failures == 0
                else AgentStatus.FAILURE
            ),
            output={
                "executed": len(results),
                "failures": failures,
                "results": results,
            },
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    async def _run_action(
        self,
        context: AIOpsContext,
        action,
    ) -> dict:

        if not action.approved:

            from app.infrastructure.governance.models import (
                ActionDecision,
            )
            from app.infrastructure.tools.models import (
                ToolExecutionContext,
            )

            parameters = dict(action.parameters)

            parameters.setdefault("action", action.action)

            approval_id = None

            approval_workflow = getattr(
                self.executor,
                "approval",
                None,
            )

            if (
                action.decision == ActionDecision.APPROVAL_REQUIRED
                and approval_workflow is not None
            ):

                approval = approval_workflow.request(
                    tool_name=action.tool,
                    parameters=parameters,
                    context={
                        "incident_id": context.incident_id,
                    },
                )

                approval_id = approval.id

            return {
                "tool": action.tool,
                "action": action.action,
                "success": False,
                "status": action.decision.value,
                "error": (
                    "Action not approved for execution."
                ),
                "data": {
                    "approval_id": approval_id,
                },
            }

        from app.infrastructure.tools.models import (
            ToolExecutionContext,
        )

        parameters = dict(action.parameters)

        parameters.setdefault("action", action.action)

        tool_result = await self.executor.execute(
            tool_name=action.tool,
            parameters=parameters,
            context=ToolExecutionContext(
                incident_id=context.incident_id,
            ),
        )

        return {
            "tool": action.tool,
            "action": action.action,
            "success": tool_result.success,
            "status": "executed",
            "error": tool_result.error,
            "data": tool_result.data,
        }


class VerificationAgent(AIOpsAgent):
    """
    Verifies that remediation actions succeeded.
    """

    def __init__(self) -> None:

        super().__init__("verification")

    async def execute(
        self,
        context: AIOpsContext,
    ) -> AgentResult:

        results = context.execution_results

        executed = [
            r for r in results if r["status"] == "executed"
        ]

        failures = [
            r
            for r in executed
            if not r["success"]
        ]

        not_approved = [
            r
            for r in results
            if r["status"] != "executed"
        ]

        resolved = (
            len(executed) > 0
            and len(failures) == 0
            and len(not_approved) == 0
        )

        context.verification = {
            "resolved": resolved,
            "executed": len(executed),
            "failures": len(failures),
            "blocked_or_pending": len(not_approved),
        }

        return AgentResult(
            agent=self.name,
            status=(
                AgentStatus.SUCCESS
                if resolved
                else AgentStatus.FAILURE
            ),
            output=dict(context.verification),
        )


class MultiAgentRunner:
    """
    Runs the AIOps agents in a fixed order sharing context.
    """

    def __init__(
        self,
        agents: list[AIOpsAgent],
    ) -> None:

        self.agents = agents

    async def run(
        self,
        context: AIOpsContext,
    ) -> list[AgentResult]:

        results: list[AgentResult] = []

        for agent in self.agents:

            result = await agent.execute(context)

            results.append(result)

        return results
