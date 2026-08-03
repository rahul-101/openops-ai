from fastapi import APIRouter, Depends

from app.infrastructure.ai.routing.priority_routing_policy import (
    PriorityRoutingPolicy,
)
from app.infrastructure.ai.routing.routing_engine import (
    RoutingEngine,
)
from app.infrastructure.dependencies import (
    get_routing_engine,
    get_routing_policy,
)

router = APIRouter(
    prefix="/routing",
    tags=["Routing API"],
)


@router.get(
    "/priority",
    summary="Get the current provider priority order",
)
def get_provider_priority(
    routing_policy: PriorityRoutingPolicy = Depends(
        get_routing_policy,
    ),
):

    return {
        "providers": (
            routing_policy.get_provider_priority()
        ),
    }


@router.get(
    "/ranked",
    summary="Get providers ranked by the routing engine",
)
def get_ranked_providers(
    routing_engine: RoutingEngine = Depends(
        get_routing_engine,
    ),
):

    return {
        "providers": routing_engine.rank_providers(),
    }
