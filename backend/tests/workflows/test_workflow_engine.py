import pytest

from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_registry import AgentRegistry
from app.application.orchestration.agent_orchestrator import (
    AgentOrchestrator,
)
from app.application.workflows.workflow_engine import (
    WorkflowEngine,
    WorkflowStatus,
    WorkflowStepStatus,
)
from tests.agents.fakes import FakeAgent


def build_engine(
    registry: AgentRegistry,
    max_retries: int = 2,
    stop_on_failure: bool = True,
) -> WorkflowEngine:

    orchestrator = AgentOrchestrator(
        registry,
        stop_on_failure=stop_on_failure,
    )

    return WorkflowEngine(
        orchestrator=orchestrator,
        max_retries=max_retries,
        stop_on_failure=stop_on_failure,
    )


def make_context():
    return AgentContext(
        incident_id="inc-1",
        workflow_id="wf-1",
    )


def make_registry(
    alpha_fail: bool = False,
    alpha_fail_times: int = 0,
    beta_fail: bool = False,
) -> AgentRegistry:

    registry = AgentRegistry()

    registry.register(
        FakeAgent(
            name="alpha",
            order=1,
            fail=alpha_fail,
            fail_times=alpha_fail_times,
        )
    )

    registry.register(
        FakeAgent(
            name="beta",
            order=2,
            fail=beta_fail,
        )
    )

    return registry


@pytest.mark.asyncio
async def test_completed_lifecycle():

    registry = make_registry()

    engine = build_engine(registry)

    history = await engine.execute(make_context())

    assert engine.status == WorkflowStatus.COMPLETED
    assert engine.current_step == "beta"
    assert [result.status.value for result in history] == [
        "success",
        "success",
    ]

    assert (
        engine.step_status("alpha")
        == WorkflowStepStatus.SUCCEEDED
    )


@pytest.mark.asyncio
async def test_retries_transient_failure():

    registry = make_registry(
        alpha_fail_times=1,
    )

    engine = build_engine(
        registry,
        max_retries=2,
    )

    history = await engine.execute(make_context())

    assert engine.status == WorkflowStatus.COMPLETED

    assert [result.agent for result in history] == [
        "alpha",
        "beta",
    ]

    assert len(engine.get_checkpoints()) == 2


@pytest.mark.asyncio
async def test_fails_after_exhausting_retries():

    registry = make_registry(
        alpha_fail=True,
    )

    engine = build_engine(
        registry,
        max_retries=2,
    )

    _ = await engine.execute(make_context())

    assert engine.status == WorkflowStatus.FAILED

    assert engine.step_status("alpha") == (
        WorkflowStepStatus.FAILED
    )

    assert len(engine.get_checkpoints()) == 3


@pytest.mark.asyncio
async def test_partially_completed_when_not_stop_on_failure():

    registry = make_registry(
        alpha_fail=True,
    )

    engine = build_engine(
        registry,
        max_retries=1,
        stop_on_failure=False,
    )

    history = await engine.execute(make_context())

    assert engine.status == (
        WorkflowStatus.PARTIALLY_COMPLETED
    )

    assert [result.agent for result in history] == [
        "alpha",
        "beta",
    ]


@pytest.mark.asyncio
async def test_checkpoints_recorded():

    registry = make_registry()

    engine = build_engine(registry)

    await engine.execute(make_context())

    checkpoints = engine.get_checkpoints()

    assert len(checkpoints) == 1
    assert checkpoints[0].step_name == "attempt_1"
    assert checkpoints[0].status == WorkflowStatus.COMPLETED
