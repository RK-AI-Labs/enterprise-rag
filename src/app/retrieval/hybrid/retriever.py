"""Hybrid retriever combining BM25 and dense retrieval via configurable weighted fusion."""

from typing import Protocol

from app.models.retrieval import RetrievedChunk
from app.retrieval.hybrid.fusion import fuse_scores


class _Bm25Search(Protocol):
    """Narrow interface for the sparse side of hybrid retrieval."""

    def search(self, query: str, limit: int) -> list[RetrievedChunk]:
        """Return the top-`limit` chunks ranked by lexical relevance to `query`."""
        ...


class _DenseSearch(Protocol):
    """Narrow interface for the dense side of hybrid retrieval."""

    async def search(self, query: str, limit: int) -> list[RetrievedChunk]:
        """Return the top-`limit` chunks ranked by vector similarity to `query`."""
        ...


class HybridRetriever:
    """Retrieves chunks using both BM25 and dense retrieval, fused by a configurable weight."""

    def __init__(
        self,
        bm25_retriever: _Bm25Search,
        dense_retriever: _DenseSearch,
        dense_weight: float = 0.5,
        candidate_pool_size: int = 20,
    ) -> None:
        self._bm25_retriever = bm25_retriever
        self._dense_retriever = dense_retriever
        self._dense_weight = dense_weight
        self._candidate_pool_size = candidate_pool_size

    async def search(self, query: str, limit: int = 5) -> list[RetrievedChunk]:
        """Return the top-`limit` chunks by fused BM25 + dense relevance to `query`."""
        pool = max(limit, self._candidate_pool_size)
        bm25_results = self._bm25_retriever.search(query, limit=pool)
        dense_results = await self._dense_retriever.search(query, limit=pool)
        fused = fuse_scores(bm25_results, dense_results, self._dense_weight)
        return fused[:limit]
