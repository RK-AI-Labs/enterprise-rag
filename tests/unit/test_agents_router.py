"""Unit tests for the Router Agent node."""

from app.agents.router import route_query, router_node


def test_route_query_defaults_to_retrieve() -> None:
    """A plain query with no tool prefix should route to retrieval."""
    assert route_query({"rewritten_query": "what is RAG?"}) == "retrieve"


def test_route_query_routes_tool_prefix_to_tool() -> None:
    """A query starting with the `tool:` prefix should route to the tool node."""
    assert route_query({"rewritten_query": "tool: 2 + 2"}) == "tool"


def test_route_query_routes_calc_prefix_to_tool() -> None:
    """A query starting with the `calc:` prefix should route to the tool node."""
    assert route_query({"rewritten_query": "CALC: 2 + 2"}) == "tool"


def test_route_query_falls_back_to_empty_string_when_missing() -> None:
    """A missing `rewritten_query` should be treated as an empty string, routing to retrieval."""
    assert route_query({}) == "retrieve"


async def test_router_node_records_route_decision() -> None:
    """The router node should return the computed route under the `route` key."""
    result = await router_node({"rewritten_query": "tool: ping"})

    assert result == {"route": "tool"}
