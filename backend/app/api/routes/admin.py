"""
Admin utilities: resetting demo data to a clean seeded state.

Kept out of the public API surface and guarded by the same env
flag used to enable seeding, so it can never run in production.
"""

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.infrastructure.demo_seed import seed_demo_data
from app.infrastructure.dependencies import (
    get_agent_analytics,
    get_approval_workflow,
    get_audit_log_service,
    get_event_ingestion_engine,
    get_incident_lifecycle_orchestrator,
    get_incident_repository,
    get_knowledge_base_service,
    get_model_governance_service,
    get_operations_command_center,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


def clear_all_stores() -> None:
    """Wipe every persisted domain store before re-seeding."""

    get_operations_command_center().clear()
    get_event_ingestion_engine().clear()
    get_incident_lifecycle_orchestrator().clear()
    get_incident_repository().clear()
    get_approval_workflow().clear()
    get_agent_analytics().clear()
    get_model_governance_service().clear()
    get_audit_log_service().clear()
    get_knowledge_base_service().clear()


@router.post("/reset-demo")
async def reset_demo() -> dict:
    """
    Wipe all operational data and re-seed the demo dataset.

    Only available when demo seeding is enabled (dev/test only).
    """

    settings = get_settings()

    if not settings.SEED_DEMO_DATA:
        raise HTTPException(
            status_code=403,
            detail="Demo reset is disabled in this environment",
        )

    clear_all_stores()

    await seed_demo_data()

    return {"status": "ok", "reset": True}
