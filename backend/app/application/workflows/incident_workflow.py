from uuid import uuid4

from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_registry import AgentRegistry
from app.application.agents.agent_result import AgentResult
from app.domain.entities.incident_workflow_state import (
    AgentHistoryEntry,
    IncidentWorkflowState,
    WorkflowExecutionStatus,
)
from app.application.workflows.workflow_engine import (
    WorkflowEngine,
    WorkflowStatus,
)


class IncidentWorkflow:
    """
    Defines the agent sequence for incident response.

    Architecture: WorkflowEngine -> AgentOrchestrator
    -> AgentRegistry -> Agents -> AI Router.
    """

    AGENTS = [
        "triage",
        "analysis",
        "recommendation",
    ]

    def __init__(
        self,
        engine: WorkflowEngine,
        registry: AgentRegistry,
    ) -> None:

        self.engine = engine
        self.registry = registry

    async def run(
        self,
        incident_id: str,
        input_data: dict,
    ) -> IncidentWorkflowState:

        context = AgentContext(
            incident_id=incident_id,
            workflow_id=str(uuid4()),
            input=input_data,
        )

        history = await self.engine.execute(
            context,
            self.AGENTS,
        )

        return self._build_state(
            context,
            history,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def _build_state(
        self,
        context: AgentContext,
        history: list[AgentResult],
    ) -> IncidentWorkflowState:

        state = IncidentWorkflowState(
            incident_id=context.incident_id,
            workflow_id=context.workflow_id,
            workflow_status=self._map_status(
                self.engine.status
            ),
            current_step=self.engine.current_step,
            recommendations=list(
                context.recommendations
            ),
            execution_result=dict(context.state),
        )

        for result in history:

            state.add_history(
                AgentHistoryEntry(
                    agent=result.agent,
                    status=result.status.value,
                    output=dict(result.output),
                    error=result.error,
                    duration_ms=result.duration_ms,
                    executed_at=result.executed_at,
                )
            )

        return state

    @staticmethod
    def _map_status(
        status: WorkflowStatus,
    ) -> WorkflowExecutionStatus:

        mapping = {
            WorkflowStatus.PENDING: (
                WorkflowExecutionStatus.PENDING
            ),
            WorkflowStatus.RUNNING: (
                WorkflowExecutionStatus.RUNNING
            ),
            WorkflowStatus.COMPLETED: (
                WorkflowExecutionStatus.COMPLETED
            ),
            WorkflowStatus.FAILED: (
                WorkflowExecutionStatus.FAILED
            ),
            WorkflowStatus.PARTIALLY_COMPLETED: (
                WorkflowExecutionStatus.PARTIALLY_COMPLETED
            ),
        }

        return mapping.get(
            status,
            WorkflowExecutionStatus.PENDING,
        )
