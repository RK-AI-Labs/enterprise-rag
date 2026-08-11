"""Tests for the compiled Enterprise RAG agent graph."""

from app.graph.build import build_graph
from app.models.retrieval import RetrievedChunk


class _FakeRetriever:
    async def search(self, query: str, limit: int) -> list[RetrievedChunk]:
        return [RetrievedChunk(chunk_id="a", content=f"context for {query}", score=1.0, source="s")]


class _FakeToolExecutor:
    async def run(self, query: str) -> str:
        return f"tool-result for {query}"


class _FakeResponseGenerator:
    async def generate(self, query: str, chunks: list[RetrievedChunk]) -> str:
        citations = "".join(f"[{chunk.chunk_id}]" for chunk in chunks)
        joined = "|".join(chunk.content for chunk in chunks)
        return f"answer to {query} using {joined} {citations}"


def _build_test_graph():
    return build_graph(
        retriever=_FakeRetriever(),
        tool_executor=_FakeToolExecutor(),
        response_generator=_FakeResponseGenerator(),
        top_k=3,
    )


async def test_graph_routes_plain_query_through_retriever() -> None:
    """A plain query should flow query_understanding -> router -> retriever -> response."""
    graph = _build_test_graph()

    result = await graph.ainvoke({"query": "  what is RAG?  "})

    assert result["rewritten_query"] == "what is RAG?"
    assert result["route"] == "retrieve"
    assert result["retrieved_chunks"][0].chunk_id == "a"
    assert result["answer"] == "answer to what is RAG? using context for what is RAG? [a]"
    assert result["citations"][0].chunk_id == "a"
    assert "tool_result" not in result


async def test_graph_routes_tool_prefixed_query_through_tool() -> None:
    """A `tool:`-prefixed query should flow query_understanding -> router -> tool -> response."""
    graph = _build_test_graph()

    result = await graph.ainvoke({"query": "tool: 2 + 2"})

    assert result["rewritten_query"] == "tool: 2 + 2"
    assert result["route"] == "tool"
    assert result["tool_result"] == "tool-result for tool: 2 + 2"
    assert result["answer"] == (
        "answer to tool: 2 + 2 using tool-result for tool: 2 + 2 [tool-result]"
    )
    assert result["citations"] == []
    assert result["confidence"] == 1.0
    assert "retrieved_chunks" not in result
