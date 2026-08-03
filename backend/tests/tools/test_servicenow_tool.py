import pytest

from app.infrastructure.tools.servicenow.servicenow_tool import (
    ServiceNowTool,
)
from tests.tools.fakes import FakeTransport


@pytest.fixture
def transport() -> FakeTransport:
    return FakeTransport(
        status=201,
        payload={
            "result": {
                "sys_id": "sys-1",
                "number": "INC0010001",
            }
        },
    )


@pytest.fixture
def tool(transport) -> ServiceNowTool:
    return ServiceNowTool(
        instance="https://dev.example.com",
        transport=transport,
    )


@pytest.mark.asyncio
async def test_create_incident(tool, transport):

    result = await tool.execute(
        {
            "action": "create_incident",
            "short_description": "DB down",
            "description": "database is down",
            "category": "database",
        }
    )

    assert result.success is True
    assert result.data["action"] == "create_incident"

    call = transport.calls[0]

    assert call["method"] == "POST"
    assert (
        call["url"]
        == "https://dev.example.com/api/now/table/incident"
    )
    assert call["json"]["short_description"] == "DB down"


@pytest.mark.asyncio
async def test_get_incident(tool, transport):

    result = await tool.execute(
        {
            "action": "get_incident",
            "incident_id": "INC0010001",
        }
    )

    assert result.success is True

    call = transport.calls[0]

    assert call["method"] == "GET"
    assert (
        "INC0010001"
        in call["url"]
    )


@pytest.mark.asyncio
async def test_update_incident(tool, transport):

    result = await tool.execute(
        {
            "action": "update_incident",
            "incident_id": "INC0010001",
            "state": "3",
        }
    )

    assert result.success is True
    assert transport.calls[0]["method"] == "PATCH"


@pytest.mark.asyncio
async def test_add_work_notes(tool, transport):

    result = await tool.execute(
        {
            "action": "add_work_notes",
            "incident_id": "INC0010001",
            "notes": "investigating",
        }
    )

    assert result.success is True

    assert (
        transport.calls[0]["json"]["work_notes"]
        == "investigating"
    )


@pytest.mark.asyncio
async def test_assign_incident(tool, transport):

    result = await tool.execute(
        {
            "action": "assign_incident",
            "incident_id": "INC0010001",
            "assignee": "john.doe",
            "assignment_group": "SRE",
        }
    )

    assert result.success is True

    assert (
        transport.calls[0]["json"]["assigned_to"]
        == "john.doe"
    )


@pytest.mark.asyncio
async def test_resolve_incident(tool, transport):

    result = await tool.execute(
        {
            "action": "resolve_incident",
            "incident_id": "INC0010001",
            "resolution_notes": "resized pool",
        }
    )

    assert result.success is True

    assert transport.calls[0]["json"]["state"] == "6"


@pytest.mark.asyncio
async def test_create_change_request(tool, transport):

    result = await tool.execute(
        {
            "action": "create_change_request",
            "short_description": "Pool resize",
            "description": "increase pool size",
        }
    )

    assert result.success is True

    assert (
        "/change_request"
        in transport.calls[0]["url"]
    )


@pytest.mark.asyncio
async def test_error_on_failure_response():

    failing = ServiceNowTool(
        instance="https://dev.example.com",
        transport=FakeTransport(
            status=500,
            payload={"error": "boom"},
        ),
    )

    result = await failing.execute(
        {
            "action": "create_incident",
            "short_description": "DB down",
            "description": "database is down",
        }
    )

    assert result.success is False
    assert "failed" in result.error


@pytest.mark.asyncio
async def test_unsupported_action(tool):

    result = await tool.execute({"action": "nope"})

    assert result.success is False


def test_risky_actions_require_approval(tool):

    assert tool.requires_approval(
        {"action": "resolve_incident"}
    ) is True

    assert tool.requires_approval(
        {"action": "create_incident"}
    ) is False
