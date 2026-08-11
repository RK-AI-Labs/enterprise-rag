"""Unit tests for `HybridRetriever`."""

from app.models.retrieval import RetrievedChunk
from app.retrieval.hybrid.retriever import HybridRetriever


class _FakeBm25Retriever:
    def __init__(self, results: list[RetrievedChunk]) -> None:
        self._results = results
        self.last_limit: int | None = None

    def search(self, query: str, limit: int) -> list[RetrievedChunk]:
        self.last_limit = limit
        return self._results[:limit]


class _FakeDenseRetriever:
    def __init__(self, results: list[RetrievedChunk]) -> None:
        self._results = results
        self.last_limit: int | None = None

    async def search(self, query: str, limit: int) -> list[RetrievedChunk]:
        self.last_limit = limit
        return self._results[:limit]


def _chunk(chunk_id: str, score: float) -> RetrievedChunk:
    return RetrievedChunk(chunk_id=chunk_id, content=f"content-{chunk_id}", score=score, source="s")


async def test_search_fuses_bm25_and_dense_results_and_respects_limit() -> None:
    """The hybrid retriever should fuse both sides and truncate to the requested limit."""
    bm25 = _FakeBm25Retriever([_chunk("a", 10.0), _chunk("b", 1.0), _chunk("c", 5.0)])
    dense = _FakeDenseRetriever([_chunk("a", 0.9), _chunk("c", 0.8)])
    retriever = HybridRetriever(bm25, dense, dense_weight=0.5, candidate_pool_size=20)

    results = await retriever.search("query", limit=2)

    assert len(results) == 2
    assert results[0].chunk_id == "a"


async def test_search_uses_candidate_pool_size_for_underlying_retrievers() -> None:
    """Underlying retrievers should be queried with the configured candidate pool size."""
    bm25 = _FakeBm25Retriever([_chunk("a", 1.0)])
    dense = _FakeDenseRetriever([_chunk("a", 1.0)])
    retriever = HybridRetriever(bm25, dense, dense_weight=0.5, candidate_pool_size=15)

    await retriever.search("query", limit=3)

    assert bm25.last_limit == 15
    assert dense.last_limit == 15


async def test_search_pool_size_grows_with_limit_when_larger_than_default() -> None:
    """The candidate pool should never be smaller than the requested limit."""
    bm25 = _FakeBm25Retriever([_chunk("a", 1.0)])
    dense = _FakeDenseRetriever([_chunk("a", 1.0)])
    retriever = HybridRetriever(bm25, dense, dense_weight=0.5, candidate_pool_size=5)

    await retriever.search("query", limit=10)

    assert bm25.last_limit == 10
    assert dense.last_limit == 10
