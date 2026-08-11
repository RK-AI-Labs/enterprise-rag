"""Unit tests for `fuse_scores` weighted BM25/dense fusion."""

from app.models.retrieval import RetrievedChunk
from app.retrieval.hybrid.fusion import fuse_scores


def _chunk(chunk_id: str, score: float) -> RetrievedChunk:
    return RetrievedChunk(chunk_id=chunk_id, content=f"content-{chunk_id}", score=score, source="s")


def test_fuse_scores_pure_dense_weight_orders_by_dense_only() -> None:
    """With dense_weight=1.0, ranking should match dense results only."""
    bm25_results = [_chunk("a", 10.0), _chunk("b", 1.0)]
    dense_results = [_chunk("b", 0.9), _chunk("a", 0.1)]

    fused = fuse_scores(bm25_results, dense_results, dense_weight=1.0)

    assert [c.chunk_id for c in fused] == ["b", "a"]


def test_fuse_scores_pure_bm25_weight_orders_by_bm25_only() -> None:
    """With dense_weight=0.0, ranking should match BM25 results only."""
    bm25_results = [_chunk("a", 10.0), _chunk("b", 1.0)]
    dense_results = [_chunk("b", 0.9), _chunk("a", 0.1)]

    fused = fuse_scores(bm25_results, dense_results, dense_weight=0.0)

    assert [c.chunk_id for c in fused] == ["a", "b"]


def test_fuse_scores_balanced_weight_combines_both_signals() -> None:
    """With dense_weight=0.5, a chunk strong in both signals should rank first."""
    bm25_results = [_chunk("a", 10.0), _chunk("b", 1.0), _chunk("c", 5.0)]
    dense_results = [_chunk("a", 0.9), _chunk("c", 0.2)]

    fused = fuse_scores(bm25_results, dense_results, dense_weight=0.5)

    assert fused[0].chunk_id == "a"


def test_fuse_scores_includes_chunks_present_in_only_one_side() -> None:
    """Chunks appearing in only one result set should still be included in the fused output."""
    bm25_results = [_chunk("only_bm25", 5.0)]
    dense_results = [_chunk("only_dense", 0.5)]

    fused = fuse_scores(bm25_results, dense_results, dense_weight=0.5)

    assert {c.chunk_id for c in fused} == {"only_bm25", "only_dense"}


def test_fuse_scores_handles_empty_inputs() -> None:
    """Fusing two empty result sets should return an empty list without error."""
    assert fuse_scores([], [], dense_weight=0.5) == []


def test_fuse_scores_single_result_per_side_normalizes_to_one() -> None:
    """A lone result in a side should normalize to 1.0 rather than raising a division error."""
    bm25_results = [_chunk("a", 3.0)]
    dense_results = [_chunk("a", 0.7)]

    fused = fuse_scores(bm25_results, dense_results, dense_weight=0.5)

    assert fused[0].score == 1.0
