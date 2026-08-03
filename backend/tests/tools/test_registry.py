import pytest

from app.infrastructure.tools.base import Tool
from app.infrastructure.tools.exceptions import (
    ToolNotFoundError,
)
from app.infrastructure.tools.models import (
    ToolCategory,
    ToolMetadata,
    ToolResult,
)
from app.infrastructure.tools.registry import ToolRegistry


class PingTool(Tool):

    def __init__(self, name: str = "ping"):
        super().__init__(
            ToolMetadata(
                name=name,
                category=ToolCategory.DATABASE,
                description="test tool",
            )
        )

    async def execute(self, parameters, context=None) -> ToolResult:
        return ToolResult(tool=self.name, success=True, data={"ping": "pong"})


def test_register_and_get():

    registry = ToolRegistry()

    registry.register(PingTool())

    assert registry.exists("ping")
    assert registry.get("ping").name == "ping"


def test_register_is_case_insensitive():

    registry = ToolRegistry()

    registry.register(PingTool())

    assert registry.get("PING").name == "ping"


def test_get_unknown_raises():

    registry = ToolRegistry()

    with pytest.raises(ToolNotFoundError):
        registry.get("missing")


def test_list_sorted():

    registry = ToolRegistry()

    registry.register(PingTool("b"))
    registry.register(PingTool("a"))

    assert registry.list() == ["a", "b"]


def test_by_category():

    registry = ToolRegistry()

    registry.register(PingTool("b"))
    registry.register(PingTool("a"))

    tools = registry.by_category(ToolCategory.DATABASE)

    assert len(tools) == 2


def test_len():

    registry = ToolRegistry()

    registry.register(PingTool())

    assert len(registry) == 1


@pytest.mark.asyncio
async def test_base_requires_approval_default_false():

    tool = PingTool()

    assert tool.requires_approval({"action": "anything"}) is False
