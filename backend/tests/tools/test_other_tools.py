import pytest

from app.infrastructure.tools.database.database_tool import (
    DatabaseTool,
)
from app.infrastructure.tools.slack.slack_tool import SlackTool
from app.infrastructure.tools.teams.teams_tool import TeamsTool
from tests.tools.fakes import FakeDatabaseAdapter, FakeTransport


# ==========================================================
# Slack
# ==========================================================


@pytest.mark.asyncio
async def test_slack_send_message():

    transport = FakeTransport(
        status=200,
        payload={"ok": True},
    )

    tool = SlackTool(transport=transport)

    result = await tool.execute(
        {
            "action": "send_message",
            "channel": "#incidents",
            "message": "DB down",
        }
    )

    assert result.success is True

    assert (
        transport.calls[0]["json"]["channel"]
        == "#incidents"
    )


@pytest.mark.asyncio
async def test_slack_unsupported_action():

    tool = SlackTool(transport=FakeTransport())

    result = await tool.execute({"action": "list_channels"})

    assert result.success is False


# ==========================================================
# Teams
# ==========================================================


@pytest.mark.asyncio
async def test_teams_send_message():

    transport = FakeTransport(
        status=201,
        payload={"id": "msg-1"},
    )

    tool = TeamsTool(transport=transport)

    result = await tool.execute(
        {
            "action": "send_message",
            "team_id": "team-1",
            "channel_id": "ch-1",
            "message": "DB down",
        }
    )

    assert result.success is True

    assert (
        "teams/team-1/channels/ch-1/messages"
        in transport.calls[0]["url"]
    )


@pytest.mark.asyncio
async def test_teams_unsupported_action():

    tool = TeamsTool(transport=FakeTransport())

    result = await tool.execute({"action": "get_messages"})

    assert result.success is False


# ==========================================================
# Database
# ==========================================================


@pytest.mark.asyncio
async def test_database_query():

    adapter = FakeDatabaseAdapter(
        rows=[{"status": "healthy"}]
    )

    tool = DatabaseTool(adapter)

    result = await tool.execute(
        {
            "action": "query",
            "sql": "SELECT status FROM incidents",
        }
    )

    assert result.success is True
    assert result.data["row_count"] == 1
    assert adapter.queries[0].startswith("SELECT")


@pytest.mark.asyncio
async def test_database_execute():

    adapter = FakeDatabaseAdapter(affected=2)

    tool = DatabaseTool(adapter)

    result = await tool.execute(
        {
            "action": "execute",
            "sql": "UPDATE incidents SET status='resolved'",
        }
    )

    assert result.success is True
    assert result.data["affected_rows"] == 2


@pytest.mark.asyncio
async def test_database_unsupported_action():

    tool = DatabaseTool(FakeDatabaseAdapter())

    result = await tool.execute({"action": "vacuum"})

    assert result.success is False


@pytest.mark.asyncio
async def test_database_execute_requires_approval():

    tool = DatabaseTool(FakeDatabaseAdapter())

    assert tool.requires_approval(
        {"action": "execute"}
    ) is True

    assert tool.requires_approval(
        {"action": "query"}
    ) is False
