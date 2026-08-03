import pytest

from app.infrastructure.aiops.agents import (
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
    EventIngestionEngine,
    RawAlert,
)
from app.infrastructure.aiops.lifecycle import (
    IncidentLifecycleOrchestrator,
    LifecycleStatus,
)
from app.infrastructure.aiops.playbook_engine import (
    RemediationPlaybookEngine,
)
from app.infrastructure.aiops.risk_based_execution import (
    RiskBasedExecutor,
)
from app.infrastructure.learning.evaluation_engine import (
    EvaluationEngine,
)
from app.infrastructure.learning.feedback_engine import (
    FeedbackEngine,
)
from app.infrastructure.tools.base import Tool
from app.infrastructure.tools.models import (
    ToolCategory,
    ToolExecutionContext,
    ToolMetadata,
    ToolResult,
)
from app.infrastructure.governance.models import RiskLevel


class FakeServiceNowTool(Tool):
    """
    Fake ServiceNow tool used by the lifecycle.
    """

    def __init__(self) -> None:

        super().__init__(
            ToolMetadata(
                name="servicenow",
                category=ToolCategory.SERVICENOW,
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
            tool="servicenow",
            success=True,
            data={"sys_id": "SN-123"},
        )


class FakeKubernetesTool(Tool):
    """
    Fake kubernetes tool for pod status checks.
    """

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
    Dispatches to the registered fake tools.
    """

    def __init__(self) -> None:

        self.servicenow = FakeServiceNowTool()

        self.kubernetes = FakeKubernetesTool()

    async def execute(
        self,
        tool_name: str,
        parameters: dict,
        context: ToolExecutionContext | None = None,
    ) -> ToolResult:

        if tool_name == "servicenow":
            return await self.servicenow.execute(
                parameters,
                context,
            )

        if tool_name == "kubernetes":
            return await self.kubernetes.execute(
                parameters,
                context,
            )

        raise ValueError(f"Unknown tool '{tool_name}'.")


def build_orchestrator() -> IncidentLifecycleOrchestrator:

    ingestion = EventIngestionEngine()

    risk = RiskBasedExecutor()

    risk.register_action(
        "tool.servicenow.create_incident",
        RiskLevel.LOW,
    )

    risk.register_action(
        "tool.kubernetes.pod_status",
        RiskLevel.LOW,
    )

    playbooks = RemediationPlaybookEngine()

    playbooks.load_yaml(
        """
name: kubernetes_crash_restart
match:
  source: kubernetes
  severities:
    - high
  tags:
    - crash
steps:
  - name: check_pod_status
    tool: kubernetes
    action: pod_status
    risk_level: low
"""
    )

    decision_engine = AutonomousDecisionEngine(
        risk_executor=risk,
    )

    executor = FakeExecutor()

    runners = MultiAgentRunner(
        agents=[
            IncidentAgent(),
            RcaAgent(),
            PlannerAgent(),
            ExecutionAgent(executor=executor),
            VerificationAgent(),
        ]
    )

    feedback = FeedbackEngine()

    evaluation = EvaluationEngine()

    return IncidentLifecycleOrchestrator(
        ingestion=ingestion,
        decision_engine=decision_engine,
        playbooks=playbooks,
        agents=runners,
        feedback=feedback,
        evaluation=evaluation,
        executor=executor,
    )


@pytest.mark.asyncio
async def test_full_lifecycle_success():

    orchestrator = build_orchestrator()

    alert = RawAlert(
        source="kubernetes",
        alert_id="alert-1",
        title="Crash loop",
        description="pod crash loop",
        severity="high",
        service="payments",
        tags=["crash"],
    )

    incident = await orchestrator.handle_alert(alert)

    assert incident.incident_id
    assert incident.status == LifecycleStatus.COMPLETED
    assert incident.servicenow_updated is True
    assert incident.learning_recorded is True

    stages = [s.stage for s in incident.steps]

    assert stages == [
        "ingestion",
        "analysis",
        "remediation",
        "verification",
        "servicenow",
        "learning",
    ]

    # ServiceNow was invoked
    servicenow_calls = orchestrator.executor.servicenow.calls

    assert len(servicenow_calls) == 1

    assert servicenow_calls[0]["action"] == "create_incident"
    assert servicenow_calls[0]["short_description"] == "Crash loop"
    assert servicenow_calls[0]["impact"] == "1"


@pytest.mark.asyncio
async def test_lifecycle_recorded_in_learning_engines():

    orchestrator = build_orchestrator()

    alert = RawAlert(
        source="kubernetes",
        alert_id="alert-2",
        title="Crash loop",
        description="pod crash loop",
        severity="high",
        tags=["crash"],
    )

    incident = await orchestrator.handle_alert(alert)

    feedback = orchestrator.feedback.list(
        incident_id=incident.incident_id,
    )

    assert len(feedback) == 1
    assert feedback[0].outcome == "success"

    evaluations = orchestrator.evaluation.list(
        incident_id=incident.incident_id,
    )

    assert len(evaluations) == 1
    assert evaluations[0].outcome is True


@pytest.mark.asyncio
async def test_get_and_list_lifecycle():

    orchestrator = build_orchestrator()

    alert = RawAlert(
        source="kubernetes",
        alert_id="alert-3",
        title="Crash loop",
        description="pod crash loop",
        severity="high",
        tags=["crash"],
    )

    incident = await orchestrator.handle_alert(alert)

    fetched = orchestrator.get(incident.incident_id)

    assert fetched is not None
    assert fetched.incident_id == incident.incident_id

    assert len(orchestrator.list()) == 1
