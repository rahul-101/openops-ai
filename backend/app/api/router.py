from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.incident_analysis import router as incident_analysis_router
from app.api.v1.incidents import router as incident_router
from app.api.routes.ai_monitoring import (
    router as ai_monitoring_router,
)
from app.api.routes.metrics import (
    router as metrics_router,
)
from app.api.routes.workflow import (
    router as workflow_router,
)
from app.api.routes.governance import (
    router as governance_router,
)
from app.api.routes.optimization import (
    router as optimization_router,
)
from app.api.routes.aiops import (
    router as aiops_router,
)
from app.api.routes.reliability import (
    router as reliability_router,
)
from app.api.routes.reasoning import (
    router as reasoning_router,
)
from app.api.routes.command_center import (
    router as command_center_router,
)
from app.api.routes.provider_management import (
    router as provider_management_router,
)
from app.api.routes.routing_api import (
    router as routing_api_router,
)
from app.api.routes.knowledge import (
    router as knowledge_router,
)
from app.api.routes.approvals import (
    router as approvals_router,
)
from app.api.routes.chat import (
    router as chat_router,
)

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(incident_router)
api_router.include_router(incident_analysis_router)
api_router.include_router(
    ai_monitoring_router,
)
api_router.include_router(
    metrics_router,
)
api_router.include_router(
    workflow_router,
)
api_router.include_router(
    governance_router,
)
api_router.include_router(
    optimization_router,
)
api_router.include_router(
    aiops_router,
)
api_router.include_router(
    reliability_router,
)
api_router.include_router(
    reasoning_router,
)
api_router.include_router(
    command_center_router,
)
api_router.include_router(
    provider_management_router,
)
api_router.include_router(
    routing_api_router,
)
api_router.include_router(
    knowledge_router,
)
api_router.include_router(
    approvals_router,
)
api_router.include_router(
    chat_router,
)
