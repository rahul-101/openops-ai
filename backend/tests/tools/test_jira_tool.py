import pytest

from app.infrastructure.tools.jira.jira_tool import JiraTool
from tests.tools.fakes import FakeTransport


@pytest.fixture
def transport() -> FakeTransport:
    return FakeTransport(
        status=200,
        payload={"id": "10000", "key": "OPS-1"},
    )


@pytest.fixture
def tool(transport) -> JiraTool:
    return JiraTool(
        base_url="https://ops.atlassian.net",
        transport=transport,
    )


@pytest.mark.asyncio
async def test_create_issue(tool, transport):

    result = await tool.execute(
        {
            "action": "create_issue",
            "project_key": "OPS",
            "summary": "DB down",
            "description": "database is down",
        }
    )

    assert result.success is True

    call = transport.calls[0]

    assert call["method"] == "POST"
    assert (
        call["url"]
        == "https://ops.atlassian.net/rest/api/2/issue"
    )
    assert call["json"]["fields"]["project"]["key"] == "OPS"
    assert call["json"]["fields"]["issuetype"]["name"] == "Task"


@pytest.mark.asyncio
async def test_update_issue(tool, transport):

    result = await tool.execute(
        {
            "action": "update_issue",
            "issue_key": "OPS-1",
            "summary": "New summary",
        }
    )

    assert result.success is True
    assert transport.calls[0]["method"] == "PUT"


@pytest.mark.asyncio
async def test_add_comment(tool, transport):

    result = await tool.execute(
        {
            "action": "add_comment",
            "issue_key": "OPS-1",
            "comment": "restarted service",
        }
    )

    assert result.success is True

    assert (
        transport.calls[0]["json"]["body"]
        == "restarted service"
    )


@pytest.mark.asyncio
async def test_transition_status(tool, transport):

    result = await tool.execute(
        {
            "action": "transition_status",
            "issue_key": "OPS-1",
            "transition_id": "31",
        }
    )

    assert result.success is True

    assert (
        transport.calls[0]["json"]["transition"]["id"]
        == "31"
    )


@pytest.mark.asyncio
async def test_error_on_failure():

    failing = JiraTool(
        base_url="https://ops.atlassian.net",
        transport=FakeTransport(
            status=401,
            payload={"errorMessages": ["unauthorized"]},
        ),
    )

    result = await failing.execute(
        {
            "action": "create_issue",
            "project_key": "OPS",
            "summary": "DB down",
            "description": "database is down",
        }
    )

    assert result.success is False
    assert "failed" in result.error


@pytest.mark.asyncio
async def test_unsupported_action(tool):

    result = await tool.execute({"action": "delete_issue"})

    assert result.success is False


def test_risky_actions_require_approval(tool):

    assert tool.requires_approval(
        {"action": "transition_status"}
    ) is True

    assert tool.requires_approval(
        {"action": "add_comment"}
    ) is False
