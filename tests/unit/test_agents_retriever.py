"""Unit tests for the Retriever Agent node."""

from app.agents.retriever import build_retriever_node
from app.models.retrieval import RetrievedChunk


class _FakeRetriever:
    def __init__(self, results: list[RetrievedChunk]) -> None:
        self._results = results
        self.last_query: str | None = None
        self.last_limit: int | None = None

    async def search(self, query: str, limit: int) -> list[RetrievedChunk]:
        self.last_query = query
        self.last_limit = limit
        return self._results


def _chunk(chunk_id: str) -> RetrievedChunk:
    return RetrievedChunk(chunk_id=chunk_id, content=f"content-{chunk_id}", score=1.0, source="s")


async def test_retriever_node_uses_rewritten_query_and_top_k() -> None:
    """The node should search using the rewritten query and the configured top_k."""
    retriever = _FakeRetriever([_chunk("a"), _chunk("b")])
    node = build_retriever_node(retriever, top_k=2)

    result = await node({"query": "raw", "rewritten_query": "clean"})

    assert retriever.last_query == "clean"
    assert retriever.last_limit == 2
    assert result == {"retrieved_chunks": [_chunk("a"), _chunk("b")]}


async def test_retriever_node_falls_back_to_raw_query_when_not_rewritten() -> None:
    """When no rewritten query is present, the raw query should be used instead."""
    retriever = _FakeRetriever([])
    node = build_retriever_node(retriever, top_k=5)

    await node({"query": "raw"})

    assert retriever.last_query == "raw"
