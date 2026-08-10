"""Weighted score fusion of BM25 and dense retrieval results."""

from app.models.retrieval import RetrievedChunk


def _normalize(results: list[RetrievedChunk]) -> dict[str, float]:
    """Min-max normalize scores to [0, 1], keyed by chunk_id."""
    if not results:
        return {}
    scores = [result.score for result in results]
    lo, hi = min(scores), max(scores)
    if hi == lo:
        return dict.fromkeys((result.chunk_id for result in results), 1.0)
    return {result.chunk_id: (result.score - lo) / (hi - lo) for result in results}


def fuse_scores(
    bm25_results: list[RetrievedChunk],
    dense_results: list[RetrievedChunk],
    dense_weight: float,
) -> list[RetrievedChunk]:
    """Combine BM25 and dense results via min-max normalized, weighted score fusion.

    Chunks are matched across result sets by `chunk_id`. A chunk present in only one result set
    is scored using only that set's normalized score, weighted accordingly. Returns all chunks
    sorted by descending fused score.
    """
    bm25_norm = _normalize(bm25_results)
    dense_norm = _normalize(dense_results)
    chunks_by_id = {result.chunk_id: result for result in [*bm25_results, *dense_results]}

    fused = [
        chunk.model_copy(
            update={
                "score": (
                    dense_weight * dense_norm.get(chunk_id, 0.0)
                    + (1 - dense_weight) * bm25_norm.get(chunk_id, 0.0)
                )
            }
        )
        for chunk_id, chunk in chunks_by_id.items()
    ]
    fused.sort(key=lambda result: result.score, reverse=True)
    return fused
