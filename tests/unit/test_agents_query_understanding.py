"""Unit tests for `query_understanding_node`."""

from app.agents.query_understanding import query_understanding_node


async def test_query_understanding_node_strips_whitespace() -> None:
    """The rewritten query should be the stripped raw query."""
    result = await query_understanding_node({"query": "  what is RAG?  "})

    assert result == {"rewritten_query": "what is RAG?"}


async def test_query_understanding_node_preserves_already_clean_query() -> None:
    """A query with no surrounding whitespace should be returned unchanged."""
    result = await query_understanding_node({"query": "hello"})

    assert result == {"rewritten_query": "hello"}
