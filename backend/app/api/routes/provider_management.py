from fastapi import APIRouter, Depends, HTTPException

from app.infrastructure.ai.registry.provider_metadata import (
    ProviderMetadata,
)
from app.infrastructure.ai.registry.provider_metadata_registry import (
    ProviderMetadataRegistry,
)
from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)
from app.infrastructure.dependencies import (
    get_provider_metadata_registry,
    get_provider_registry,
)

router = APIRouter(
    prefix="/providers",
    tags=["Provider Management"],
)


# ==========================================================
# Provider Catalog
# ==========================================================


def _metadata_to_dict(
    metadata: ProviderMetadata,
) -> dict:
    return {
        "name": metadata.name,
        "display_name": metadata.display_name,
        "model": metadata.model,
        "priority": metadata.priority,
        "input_cost_per_1k_tokens": (
            metadata.input_cost_per_1k_tokens
        ),
        "output_cost_per_1k_tokens": (
            metadata.output_cost_per_1k_tokens
        ),
        "max_context_tokens": metadata.max_context_tokens,
        "capabilities": sorted(
            capability.value
            for capability in metadata.capabilities
        ),
        "enabled": metadata.enabled,
    }


@router.get(
    "",
    summary="List registered AI providers",
)
def list_providers(
    metadata_registry: ProviderMetadataRegistry = Depends(
        get_provider_metadata_registry,
    ),
    registry: ProviderRegistry = Depends(
        get_provider_registry,
    ),
):

    providers = []

    for name in registry.list():

        metadata = (
            metadata_registry.get(name)
            if metadata_registry.exists(name)
            else None
        )

        providers.append(
            _metadata_to_dict(metadata)
            if metadata
            else {"name": name}
        )

    return providers


@router.get(
    "/{name}",
    summary="Get metadata for a single provider",
)
def get_provider(
    name: str,
    metadata_registry: ProviderMetadataRegistry = Depends(
        get_provider_metadata_registry,
    ),
    registry: ProviderRegistry = Depends(
        get_provider_registry,
    ),
):

    if not registry.exists(name):
        raise HTTPException(
            status_code=404,
            detail=f"AI provider '{name}' is not registered.",
        )

    if not metadata_registry.exists(name):
        raise HTTPException(
            status_code=404,
            detail=(
                f"Metadata for AI provider '{name}' "
                "is not registered."
            ),
        )

    return _metadata_to_dict(
        metadata_registry.get(name)
    )


@router.get(
    "/{name}/capabilities",
    summary="List capabilities supported by a provider",
)
def get_provider_capabilities(
    name: str,
    metadata_registry: ProviderMetadataRegistry = Depends(
        get_provider_metadata_registry,
    ),
    registry: ProviderRegistry = Depends(
        get_provider_registry,
    ),
):

    if not registry.exists(name):
        raise HTTPException(
            status_code=404,
            detail=f"AI provider '{name}' is not registered.",
        )

    if not metadata_registry.exists(name):
        raise HTTPException(
            status_code=404,
            detail=(
                f"Metadata for AI provider '{name}' "
                "is not registered."
            ),
        )

    metadata = metadata_registry.get(name)

    return sorted(
        capability.value
        for capability in metadata.capabilities
    )
