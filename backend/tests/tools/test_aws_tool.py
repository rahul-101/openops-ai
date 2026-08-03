import pytest

from app.infrastructure.tools.aws.aws_tool import AWSTool
from tests.tools.fakes import FakeTransport


@pytest.fixture
def transport() -> FakeTransport:
    return FakeTransport(
        status=200,
        payload={"instances": ["i-123"]},
    )


@pytest.fixture
def tool(transport) -> AWSTool:
    return AWSTool(
        endpoint="https://aws.example.com",
        transport=transport,
    )


@pytest.mark.asyncio
async def test_describe_instances(tool, transport):

    result = await tool.execute(
        {"action": "describe_instances"}
    )

    assert result.success is True
    assert transport.calls[0]["method"] == "POST"


@pytest.mark.asyncio
async def test_start_instance(tool, transport):

    result = await tool.execute(
        {
            "action": "start_instance",
            "instance_id": "i-123",
        }
    )

    assert result.success is True

    assert (
        transport.calls[0]["json"]["instance_ids"]
        == ["i-123"]
    )


@pytest.mark.asyncio
async def test_stop_instance(tool, transport):

    result = await tool.execute(
        {
            "action": "stop_instance",
            "instance_id": "i-123",
        }
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_get_cloudwatch_metrics(tool, transport):

    result = await tool.execute(
        {
            "action": "get_cloudwatch_metrics",
            "namespace": "AWS/EC2",
            "metric_name": "CPUUtilization",
        }
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_describe_db_instances(tool):

    result = await tool.execute(
        {"action": "describe_db_instances"}
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_reboot_db_instance(tool, transport):

    result = await tool.execute(
        {
            "action": "reboot_db_instance",
            "db_instance_identifier": "prod-db",
        }
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_error_on_failure():

    failing = AWSTool(
        endpoint="https://aws.example.com",
        transport=FakeTransport(
            status=503,
            payload={"error": "unavailable"},
        ),
    )

    result = await failing.execute(
        {
            "action": "start_instance",
            "instance_id": "i-123",
        }
    )

    assert result.success is False


def test_risky_actions_require_approval(tool):

    assert tool.requires_approval(
        {"action": "reboot_db_instance"}
    ) is True

    assert tool.requires_approval(
        {"action": "describe_instances"}
    ) is False
