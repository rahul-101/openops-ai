"""
Incident API endpoints.
"""

from fastapi import APIRouter, Depends, status

from app.application.dto.requests.incident_request import CreateIncidentRequest
from app.application.dto.responses.incident_response import IncidentResponse
from app.application.mappers.incident_mapper import IncidentMapper
from app.application.services.incident_service import IncidentService
from app.infrastructure.dependencies import get_incident_service

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(
    request: CreateIncidentRequest,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentResponse:
    """
    Create a new incident.
    """

    incident = IncidentMapper.to_domain(request)

    created = service.create_incident(incident)

    return IncidentMapper.to_response(created)


@router.get(
    "",
    response_model=list[IncidentResponse],
)
def list_incidents(
    service: IncidentService = Depends(get_incident_service),
) -> list[IncidentResponse]:
    """
    List all incidents.
    """

    incidents = service.list_incidents()

    return [
        IncidentMapper.to_response(incident)
        for incident in incidents
    ]


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    incident_id: str,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentResponse:
    """
    Get an incident by ID.
    """

    incident = service.get_incident(incident_id)

    return IncidentMapper.to_response(incident)