"""Router Agent node: decides whether to run retrieval or a tool for the current query.

Routing is a simple prefix heuristic for the MVP; a future phase can replace `route_query` with
an LLM-based classifier without changing the graph wiring.
"""

from app.agents.state import GraphState

_TOOL_PREFIXES = ("tool:", "calc:")


def route_query(state: GraphState) -> str:
    """Return the routing decision (`"retrieve"` or `"tool"`) for the current query."""
    query = state.get("rewritten_query", "")
    return "tool" if query.lower().startswith(_TOOL_PREFIXES) else "retrieve"


async def router_node(state: GraphState) -> GraphState:
    """Compute and record the routing decision for the current query."""
    return {"route": route_query(state)}
