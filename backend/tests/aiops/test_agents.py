import pytest

from app.infrastructure.aiops.agents import (
    AIOpsContext,
    ExecutionAgent,
    IncidentAgent,
    MultiAgentRunner,
    PlannerAgent,
    RcaAgent,
    VerificationAgent,
)
from app.infrastructure.aiops.decision_engine import (
    AutonomousDecisionEngine,
)
from app.infrastructure.aiops.event_ingestion import (
    EventSeverity,
    NormalizedEvent,
)
from app.infrastructure.aiops.playbook_engine import (
    Playbook,
    PlaybookStep,
)
from app.infrastructure.aiops.risk_based_execution import (
    RiskBasedExecutor,
)
from app.infrastructure.tools.base import Tool
from app.infrastructure.tools.models import (
    ToolCategory,
    ToolExecutionContext,
    ToolMetadata,
    ToolResult,
)
from app.infrastructure.governance.models import RiskLevel


class FakeKubernetesTool(Tool):
    """
    Fake kubernetes tool with a successful restart.
    """

    RISKY_ACTIONS = ("restart",)

    def __init__(self) -> None:

        super().__init__(
            ToolMetadata(
                name="kubernetes",
                category=ToolCategory.KUBERNETES,
                description="fake",
            )
        )

        self.calls: list[dict] = []

    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext | None = None,
    ) -> ToolResult:

        self.calls.append(parameters)

        return ToolResult(
            tool="kubernetes",
            success=True,
            data={"action": parameters.get("action")},
        )


class FakeExecutor:
    """
    Minimal executor double used by the ExecutionAgent.
    """

    def __init__(
        self,
        tool: Tool,
    ) -> None:

        self.tool = tool

    async def execute(
        self,
        tool_name: str,
        parameters: dict,
        context: ToolExecutionContext | None = None,
    ) -> ToolResult:

        return await self.tool.execute(
            parameters,
            context,
        )


def make_context() -> AIOpsContext:

    event = NormalizedEvent(
        event_id="event-1",
        source="kubernetes",
        title="Crash loop",
        description="pod crash loop",
        severity=EventSeverity.HIGH,
        tags=["crash"],
    )

    risk = RiskBasedExecutor()

    risk.register_action(
        "tool.kubernetes.pod_status",
        RiskLevel.LOW,
    )

    risk.register_action(
        "tool.kubernetes.restart",
        RiskLevel.MEDIUM,
    )

    engine = AutonomousDecisionEngine(risk_executor=risk)

    playbook = Playbook(
        name="crash_restart",
        steps=[
            PlaybookStep(
                name="check",
                tool="kubernetes",
                action="pod_status",
                risk_level="low",
            ),
            PlaybookStep(
                name="restart",
                tool="kubernetes",
                action="restart",
                risk_level="medium",
            ),
        ],
    )

    decision = engine.decide(event, playbook)

    return AIOpsContext(
        event=event,
        analysis=decision.analysis,
        decision=decision,
        incident_id=event.event_id,
    )


def build_runner(
    executor=None,
) -> MultiAgentRunner:

    return MultiAgentRunner(
        agents=[
            IncidentAgent(),
            RcaAgent(),
            PlannerAgent(),
            ExecutionAgent(executor=executor),
            VerificationAgent(),
        ]
    )


@pytest.mark.asyncio
async def test_full_agent_flow():

    tool = FakeKubernetesTool()

    executor = FakeExecutor(tool)

    runner = build_runner(executor)

    context = make_context()

    results = await runner.run(context)

    names = [r.agent for r in results]

    assert names == [
        "incident",
        "rca",
        "planner",
        "execution",
        "verification",
    ]

    assert context.incident_id == "event-1"

    incident = results[0]

    assert incident.output["severity"] == "high"

    rca = results[1]

    assert "crash" in rca.output["probable_cause"].lower()

    planner = results[2]

    assert planner.output["playbook"] == "crash_restart"
    assert planner.output["can_auto_execute"] is False

    execution = results[3]

    assert execution.output["executed"] == 2
    assert execution.output["failures"] == 1

    verification = results[4]

    assert verification.output["resolved"] is False
    assert verification.output["executed"] == 1
    assert verification.output["failures"] == 0
    assert verification.output["blocked_or_pending"] == 1


@pytest.mark.asyncio
async def test_execution_agent_runs_approved_actions():

    tool = FakeKubernetesTool()

    executor = FakeExecutor(tool)

    context = make_context()

    # Make both playbook steps low risk by overriding decisions
    for action in context.decision.actions:
        action.approved = True

    agent = ExecutionAgent(executor=executor)

    result = await agent.execute(context)

    assert result.status.value == "success"
    assert result.output["failures"] == 0
    assert len(tool.calls) == 2


@pytest.mark.asyncio
async def test_incident_agent_captures_facts():

    agent = IncidentAgent()

    result = await agent.execute(make_context())

    assert result.output["incident_id"] == "event-1"
    assert result.output["source"] == "kubernetes"
