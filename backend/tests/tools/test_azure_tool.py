import pytest

from app.infrastructure.tools.azure.azure_tool import AzureTool
from tests.tools.fakes import FakeTransport


@pytest.fixture
def transport() -> FakeTransport:
    return FakeTransport(
        status=200,
        payload={"vm": "web-01", "status": "running"},
    )


@pytest.fixture
def tool(transport) -> AzureTool:
    return AzureTool(
        endpoint="https://azure.example.com",
        transport=transport,
    )


@pytest.mark.asyncio
async def test_get_vm(tool, transport):

    result = await tool.execute(
        {
            "action": "get_vm",
            "vm_name": "web-01",
        }
    )

    assert result.success is True
    assert transport.calls[0]["method"] == "GET"


@pytest.mark.asyncio
async def test_start_vm(tool, transport):

    result = await tool.execute(
        {
            "action": "start_vm",
            "vm_name": "web-01",
        }
    )

    assert result.success is True

    assert (
        transport.calls[0]["json"]["vm_name"]
        == "web-01"
    )


@pytest.mark.asyncio
async def test_stop_vm(tool, transport):

    result = await tool.execute(
        {
            "action": "stop_vm",
            "vm_name": "web-01",
        }
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_get_metrics(tool):

    result = await tool.execute(
        {
            "action": "get_metrics",
            "resource": "/subscriptions/x",
            "metric_name": "Percentage CPU",
        }
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_run_log_analytics_query(tool, transport):

    result = await tool.execute(
        {
            "action": "run_log_analytics_query",
            "workspace_id": "ws-1",
            "query": "Heartbeat | count",
        }
    )

    assert result.success is True

    assert (
        transport.calls[0]["json"]["query"]
        == "Heartbeat | count"
    )


@pytest.mark.asyncio
async def test_error_on_failure():

    failing = AzureTool(
        endpoint="https://azure.example.com",
        transport=FakeTransport(
            status=403,
            payload={"error": "forbidden"},
        ),
    )

    result = await failing.execute(
        {
            "action": "start_vm",
            "vm_name": "web-01",
        }
    )

    assert result.success is False


def test_risky_actions_require_approval(tool):

    assert tool.requires_approval(
        {"action": "stop_vm"}
    ) is True

    assert tool.requires_approval(
        {"action": "get_metrics"}
    ) is False
