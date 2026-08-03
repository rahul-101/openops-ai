from fastapi import APIRouter, Depends

from app.application.dto.responses.provider_health_response import (
    ProviderHealthResponse,
)
from app.application.dto.responses.provider_metrics_response import (
    ProviderMetricsResponse,
)
from app.application.services.provider_monitoring_service import (
    ProviderMonitoringService,
)
from app.infrastructure.dependencies import (
    get_provider_monitoring_service,
)

router = APIRouter(
    prefix="/ai/providers",
    tags=["AI Monitoring"],
)


# ==========================================================
# Provider Health
# ==========================================================


@router.get(
    "/health",
    response_model=list[ProviderHealthResponse],
    summary="Get provider health",
)
def get_provider_health(
    monitoring_service: ProviderMonitoringService = Depends(
        get_provider_monitoring_service,
    ),
) -> list[ProviderHealthResponse]:

    return monitoring_service.get_provider_health()


# ==========================================================
# Provider Metrics
# ==========================================================


@router.get(
    "/metrics",
    response_model=list[ProviderMetricsResponse],
    summary="Get provider metrics",
)
def get_provider_metrics(
    monitoring_service: ProviderMonitoringService = Depends(
        get_provider_monitoring_service,
    ),
) -> list[ProviderMetricsResponse]:

    return monitoring_service.get_provider_metrics()
