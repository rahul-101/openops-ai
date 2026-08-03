"""
Incident API endpoints.
"""

from fastapi import APIRouter, Depends, Query, Response, status

from app.application.dto.requests.incident_request import (
    CreateIncidentRequest,
    UpdateIncidentRequest,
)
from app.application.dto.responses.incident_response import IncidentResponse
from app.application.dto.responses.paginated_response import (
    PaginatedResponse,
)
from app.application.mappers.incident_mapper import IncidentMapper
from app.application.services.incident_service import IncidentService
from app.domain.entities.incident import (
    IncidentSeverity,
    IncidentStatus,
)
from app.domain.models.incident_query import IncidentQuery
from app.infrastructure.dependencies import get_incident_service

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


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
    response_model=PaginatedResponse[IncidentResponse],
)
def list_incidents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: IncidentStatus | None = Query(
        default=None,
        alias="status",
    ),
    severity: IncidentSeverity | None = None,
    source: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
    ),
    service: IncidentService = Depends(get_incident_service),
) -> PaginatedResponse[IncidentResponse]:
    """
    List incidents with filtering, sorting and pagination.
    """

    query = IncidentQuery(
        page=page,
        size=size,
        status=status_filter,
        severity=severity,
        source=source,
        search=search,
        sort_by=sort_by,
        order=order,
    )

    incidents = service.list_incidents(query)

    return IncidentMapper.to_paginated_response(
        incidents
    )


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


@router.put(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def update_incident(
    incident_id: str,
    request: UpdateIncidentRequest,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentResponse:
    """
    Update an existing incident.
    """

    updated = service.update_incident(
        incident_id=incident_id,
        request=request,
    )

    return IncidentMapper.to_response(updated)


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_incident(
    incident_id: str,
    service: IncidentService = Depends(get_incident_service),
) -> Response:
    """
    Delete an incident.
    """

    service.delete_incident(incident_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
