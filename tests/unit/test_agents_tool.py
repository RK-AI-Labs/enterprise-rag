"""Unit tests for the Tool Agent node."""

import pytest

from app.agents.tool import NotImplementedToolExecutor, build_tool_node


class _FakeToolExecutor:
    def __init__(self, result: str) -> None:
        self._result = result
        self.last_query: str | None = None

    async def run(self, query: str) -> str:
        self.last_query = query
        return self._result


async def test_tool_node_uses_rewritten_query_and_records_result() -> None:
    """The node should invoke the tool with the rewritten query and record its result."""
    executor = _FakeToolExecutor("42")
    node = build_tool_node(executor)

    result = await node({"query": "raw", "rewritten_query": "tool: 2 + 2"})

    assert executor.last_query == "tool: 2 + 2"
    assert result == {"tool_result": "42"}


async def test_tool_node_falls_back_to_raw_query_when_not_rewritten() -> None:
    """When no rewritten query is present, the raw query should be used instead."""
    executor = _FakeToolExecutor("ok")
    node = build_tool_node(executor)

    await node({"query": "raw"})

    assert executor.last_query == "raw"


async def test_not_implemented_tool_executor_raises() -> None:
    """The placeholder executor should always raise `NotImplementedError`."""
    executor = NotImplementedToolExecutor()

    with pytest.raises(NotImplementedError):
        await executor.run("anything")
