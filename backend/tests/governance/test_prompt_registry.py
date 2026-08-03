import pytest

from app.infrastructure.governance.exceptions import (
    PromptNotFoundError,
    PromptVersionError,
)
from app.infrastructure.governance.prompt_registry import (
    PromptRegistry,
)


@pytest.fixture
def registry() -> PromptRegistry:

    service = PromptRegistry()

    service.register(
        name="incident_analysis",
        version="1.0.0",
        content="Analyze incident {{id}}",
        metadata={"author": "platform"},
    )

    return service


def test_first_version_is_active(registry):

    prompt = registry.get_active("incident_analysis")

    assert prompt.version == "1.0.0"
    assert prompt.active is True


def test_register_duplicate_version_raises(registry):

    with pytest.raises(PromptVersionError):
        registry.register(
            name="incident_analysis",
            version="1.0.0",
            content="Duplicate",
        )


def test_activate_version(registry):

    v2 = registry.register(
        name="incident_analysis",
        version="2.0.0",
        content="New analysis template",
    )

    assert v2.active is False

    activated = registry.activate(
        "incident_analysis",
        "2.0.0",
    )

    assert activated.active is True

    active = registry.get_active("incident_analysis")

    assert active.version == "2.0.0"

    old = registry.get(
        "incident_analysis",
        "1.0.0",
    )

    assert old.active is False


def test_get_active_missing_prompt_raises(registry):

    with pytest.raises(PromptNotFoundError):
        registry.get_active("missing_prompt")


def test_get_specific_version(registry):

    prompt = registry.get(
        "incident_analysis",
        "1.0.0",
    )

    assert prompt.content == "Analyze incident {{id}}"


def test_get_missing_version_raises(registry):

    with pytest.raises(PromptNotFoundError):
        registry.get(
            "incident_analysis",
            "9.9.9",
        )


def test_list_versions(registry):

    registry.register(
        name="incident_analysis",
        version="2.0.0",
        content="New",
    )

    registry.register(
        name="incident_analysis",
        version="1.0.1",
        content="Patch",
    )

    versions = registry.list_versions("incident_analysis")

    assert [v.version for v in versions] == [
        "1.0.0",
        "1.0.1",
        "2.0.0",
    ]


def test_all_returns_every_prompt(registry):

    registry.register(
        name="summary_prompt",
        version="1.0.0",
        content="Summarize",
    )

    prompts = registry.all()

    assert len(prompts) == 2
