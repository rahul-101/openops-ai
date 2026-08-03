import pytest

from app.infrastructure.tools.kubernetes.kubernetes_tool import (
    KubernetesTool,
)
from tests.tools.fakes import FakeTransport


@pytest.fixture
def transport() -> FakeTransport:
    return FakeTransport(
        status=200,
        payload={"items": [{"metadata": {"name": "api-0"}}]},
    )


@pytest.fixture
def tool(transport) -> KubernetesTool:
    return KubernetesTool(
        endpoint="https://kube.example.com",
        transport=transport,
    )


@pytest.mark.asyncio
async def test_pod_status(tool, transport):

    result = await tool.execute(
        {
            "action": "pod_status",
            "namespace": "prod",
        }
    )

    assert result.success is True

    call = transport.calls[0]

    assert call["method"] == "GET"
    assert "/namespaces/prod/pods" in call["url"]


@pytest.mark.asyncio
async def test_logs(tool, transport):

    result = await tool.execute(
        {
            "action": "logs",
            "namespace": "prod",
            "pod_name": "api-0",
        }
    )

    assert result.success is True

    assert (
        "/namespaces/prod/pods/api-0/log"
        in transport.calls[0]["url"]
    )


@pytest.mark.asyncio
async def test_restart(tool, transport):

    result = await tool.execute(
        {
            "action": "restart",
            "namespace": "prod",
            "deployment": "api",
        }
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_scale(tool, transport):

    result = await tool.execute(
        {
            "action": "scale",
            "namespace": "prod",
            "deployment": "api",
            "replicas": 5,
        }
    )

    assert result.success is True

    assert transport.calls[0]["json"]["replicas"] == 5


@pytest.mark.asyncio
async def test_error_on_failure():

    failing = KubernetesTool(
        endpoint="https://kube.example.com",
        transport=FakeTransport(
            status=500,
            payload={"error": "boom"},
        ),
    )

    result = await failing.execute(
        {
            "action": "scale",
            "namespace": "prod",
            "deployment": "api",
            "replicas": 5,
        }
    )

    assert result.success is False


def test_risky_actions_require_approval(tool):

    assert tool.requires_approval(
        {"action": "restart"}
    ) is True

    assert tool.requires_approval(
        {"action": "scale"}
    ) is True

    assert tool.requires_approval(
        {"action": "logs"}
    ) is False
