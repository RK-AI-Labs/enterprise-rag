"""Unit tests for `BM25Retriever`."""

import uuid

from app.models.chunk import Chunk
from app.retrieval.bm25.retriever import BM25Retriever

DOC_ID = uuid.uuid4()


def _chunk(index: int, content: str, source: str = "sample.txt") -> Chunk:
    return Chunk(document_id=DOC_ID, chunk_index=index, content=content, source=source)


def test_search_ranks_more_relevant_chunk_higher() -> None:
    """A chunk with more query-term occurrences should rank above a less relevant one."""
    retriever = BM25Retriever()
    retriever.index(
        [
            _chunk(0, "the quick brown fox jumps over the lazy dog"),
            _chunk(1, "cats and dogs are common pets"),
            _chunk(2, "quick quick quick fox fox fox"),
        ]
    )

    results = retriever.search("quick fox", limit=3)

    assert [result.chunk_id for result in results][0] == f"{DOC_ID}:2"
    assert all(result.score > 0 for result in results)


def test_search_returns_empty_list_for_empty_index() -> None:
    """Searching before `index()` has been called should return no results."""
    retriever = BM25Retriever()

    assert retriever.search("anything") == []


def test_search_excludes_chunks_with_no_matching_terms() -> None:
    """Chunks that share no terms with the query should be excluded from results."""
    retriever = BM25Retriever()
    retriever.index(
        [
            _chunk(0, "apples and oranges"),
            _chunk(1, "completely unrelated content"),
        ]
    )

    results = retriever.search("apples", limit=5)

    assert len(results) == 1
    assert results[0].chunk_id == f"{DOC_ID}:0"


def test_search_respects_limit() -> None:
    """No more than `limit` results should be returned."""
    retriever = BM25Retriever()
    retriever.index([_chunk(i, "shared keyword content") for i in range(5)])

    results = retriever.search("shared keyword", limit=2)

    assert len(results) == 2


def test_bm25_parameters_affect_scoring() -> None:
    """Different k1/b parameters should produce different scores for the same corpus/query."""
    chunks = [
        _chunk(0, "keyword " * 10),
        _chunk(1, "keyword once"),
    ]
    default_retriever = BM25Retriever()
    default_retriever.index(chunks)
    tuned_retriever = BM25Retriever(k1=0.1, b=0.1)
    tuned_retriever.index(chunks)

    default_scores = {r.chunk_id: r.score for r in default_retriever.search("keyword", limit=2)}
    tuned_scores = {r.chunk_id: r.score for r in tuned_retriever.search("keyword", limit=2)}

    assert default_scores != tuned_scores
