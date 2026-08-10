"""Tool Agent node: executes an external tool for queries routed away from retrieval.

No concrete tool (SQL/Web/Knowledge-Graph) is implemented for the MVP; `NotImplementedToolExecutor`
is a placeholder so the graph remains wireable end-to-end, extensible in future phases.
"""

from typing import Protocol

from app.agents.state import GraphState


class ToolExecutor(Protocol):
    """Narrow interface for a single tool invocation."""

    async def run(self, query: str) -> str:
        """Execute the tool for `query` and return its textual result."""
        ...


class NotImplementedToolExecutor:
    """Placeholder `ToolExecutor`; concrete SQL/Web/KG tools are future work."""

    async def run(self, query: str) -> str:
        """Always raise, since no tool is implemented in the MVP."""
        raise NotImplementedError("Tool execution is not implemented in the MVP.")


# Note: the returned closure is intentionally left without an explicit `Callable[...]` return
# annotation. LangGraph's `StateGraph.add_node` overloads match against the closure's own
# precise inferred type; wrapping it in a `Callable[[GraphState], Coroutine[...]]` alias breaks
# that overload resolution under mypy (verified against langgraph 1.2.10).
def build_tool_node(tool_executor: ToolExecutor):
    """Build the Tool Agent node bound to the given tool executor."""

    async def tool_node(state: GraphState) -> GraphState:
        """Execute the configured tool for the current query."""
        query = state.get("rewritten_query") or state["query"]
        result = await tool_executor.run(query)
        return {"tool_result": result}

    return tool_node
