"""Unit tests for the reranker abstraction stub."""

import pytest

from app.retrieval.reranker.base import NotImplementedReranker


async def test_not_implemented_reranker_raises() -> None:
    """`NotImplementedReranker.rerank` should always raise `NotImplementedError`."""
    with pytest.raises(NotImplementedError):
        await NotImplementedReranker().rerank("query", [], top_k=5)
