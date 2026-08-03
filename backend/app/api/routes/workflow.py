from fastapi import APIRouter, Depends, status

from app.application.dto.requests.incident_request import (
    IncidentRequest,
)
from app.application.dto.responses.workflow_state_response import (
    AgentHistoryResponse,
    WorkflowStateResponse,
)
from app.application.workflows.incident_workflow import (
    IncidentWorkflow,
)
from app.infrastructure.dependencies import (
    get_incident_workflow,
)

router = APIRouter(
    prefix="/incidents/{incident_id}/workflow",
    tags=["Incident Workflow"],
)


@router.post(
    "/run",
    response_model=WorkflowStateResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute the incident response workflow",
)
async def run_workflow(
    incident_id: str,
    request: IncidentRequest,
    workflow: IncidentWorkflow = Depends(
        get_incident_workflow,
    ),
) -> WorkflowStateResponse:

    state = await workflow.run(
        incident_id=incident_id,
        input_data=request.model_dump(),
    )

    return WorkflowStateResponse(
        incident_id=state.incident_id,
        workflow_id=state.workflow_id,
        workflow_status=state.workflow_status,
        current_step=state.current_step,
        agent_history=[
            AgentHistoryResponse.model_validate(entry)
            for entry in state.agent_history
        ],
        recommendations=state.recommendations,
        execution_result=state.execution_result,
        created_at=state.created_at,
        updated_at=state.updated_at,
    )
