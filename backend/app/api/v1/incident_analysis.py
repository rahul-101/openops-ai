from fastapi import APIRouter, Depends, status

from app.application.dto.requests.incident_request import (
    IncidentRequest,
)
from app.application.dto.responses.ai_response import (
    AIResponse,
)
from app.application.services.incident_analysis_service import (
    IncidentAnalysisService,
)
from app.infrastructure.dependencies import (
    get_incident_analysis_service,
)

router = APIRouter(
    prefix="/incidents",
    tags=["Incident AI"],
)


@router.post(
    "/analyze",
    response_model=AIResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze an incident using AI",
)
async def analyze_incident(
    request: IncidentRequest,
    service: IncidentAnalysisService = Depends(
        get_incident_analysis_service,
    ),
) -> AIResponse:
    """
    Analyze an incident using Gemini.
    """

    return await service.analyze(
        title=request.title,
        description=request.description,
        severity=request.severity,
    )