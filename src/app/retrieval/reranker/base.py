"""Reranker abstraction for reordering retrieved chunks (interface only for the MVP)."""

from typing import Protocol

from app.models.retrieval import RetrievedChunk


class Reranker(Protocol):
    """Reorders a candidate set of retrieved chunks by finer-grained relevance to the query."""

    async def rerank(
        self, query: str, results: list[RetrievedChunk], top_k: int
    ) -> list[RetrievedChunk]:
        """Return up to `top_k` results from `results`, reordered by relevance to `query`."""
        ...


class NotImplementedReranker:
    """Placeholder `Reranker`; a real cross-encoder/Cohere/BGE reranker is future work."""

    async def rerank(
        self, query: str, results: list[RetrievedChunk], top_k: int
    ) -> list[RetrievedChunk]:
        """Always raise, since no reranker is implemented in the MVP."""
        raise NotImplementedError("Reranking is not implemented in the MVP.")
