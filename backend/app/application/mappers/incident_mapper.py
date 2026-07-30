"""
Mapper between DTOs and domain models.
"""

from app.application.dto.requests.incident_request import (
    CreateIncidentRequest,
)
from app.application.dto.responses.incident_response import (
    IncidentResponse,
)
from app.domain.entities.incident import Incident
from app.application.dto.responses.paginated_response import (
    PaginatedResponse,
)

from app.domain.models.page import Page


class IncidentMapper:
    """Maps between DTOs and domain models."""

    @staticmethod
    def to_domain(request: CreateIncidentRequest) -> Incident:
        return Incident(
            title=request.title,
            description=request.description,
            severity=request.severity,
            source=request.source,
        )

    @staticmethod
    def to_response(
        incident: Incident,
    ) -> IncidentResponse:
        return IncidentResponse(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            severity=incident.severity,
            status=incident.status,
            source=incident.source,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
        )
    
    @staticmethod
    def to_paginated_response(
        page: Page[Incident],
    ) -> PaginatedResponse[IncidentResponse]:

        return PaginatedResponse(
            items=[
                IncidentMapper.to_response(item)
                for item in page.items
            ],
            page=page.page,
            size=page.size,
            total_items=page.total_items,
            total_pages=page.total_pages,
            has_next=page.has_next,
            has_previous=page.has_previous,
        )
    