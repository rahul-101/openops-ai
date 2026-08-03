from fastapi import APIRouter, Depends, Response

from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)
from app.infrastructure.dependencies import (
    get_metrics_registry,
    get_provider_health_service,
)
from app.infrastructure.monitoring.metrics_registry import (
    MetricsRegistry,
)

router = APIRouter(
    tags=["Monitoring"],
)


@router.get(
    "/metrics",
    summary="Prometheus metrics",
)
def get_prometheus_metrics(
    metrics_registry: MetricsRegistry = Depends(
        get_metrics_registry,
    ),
    health_service: ProviderHealthService = Depends(
        get_provider_health_service,
    ),
):

    metrics_registry.sync_provider_health(
        health_service
    )

    return Response(
        content=metrics_registry.render(),
        media_type="text/plain; version=0.0.4",
    )
