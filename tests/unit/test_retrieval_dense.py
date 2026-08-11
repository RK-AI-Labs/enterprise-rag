"""Unit tests for `DenseRetriever`."""

from app.models.vector import VectorPoint
from app.retrieval.dense.retriever import DenseRetriever


class _FakeEmbeddingProvider:
    """Deterministic fake embedding provider for tests."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text))] for text in texts]


class _FakeVectorRepository:
    """Fake `VectorRepository` returning a fixed set of points regardless of the query vector."""

    def __init__(self, points: list[VectorPoint]) -> None:
        self._points = points
        self.last_vector: list[float] | None = None
        self.last_limit: int | None = None

    async def upsert(self, points: list[VectorPoint]) -> None:
        raise NotImplementedError

    async def search(self, vector: list[float], limit: int = 5) -> list[VectorPoint]:
        self.last_vector = vector
        self.last_limit = limit
        return self._points[:limit]

    async def delete(self, point_ids: list[str]) -> None:
        raise NotImplementedError


async def test_search_embeds_query_and_maps_points_to_retrieved_chunks() -> None:
    """`DenseRetriever.search` should embed the query and map vector store hits to chunks."""
    points = [
        VectorPoint(
            id="p1",
            vector=[0.1],
            payload={"content": "hello world", "source": "a.pdf"},
            score=0.9,
        ),
        VectorPoint(
            id="p2",
            vector=[0.2],
            payload={"content": "another chunk", "source": "b.pdf"},
            score=0.4,
        ),
    ]
    embedding_provider = _FakeEmbeddingProvider()
    vector_repository = _FakeVectorRepository(points)
    retriever = DenseRetriever(embedding_provider, vector_repository)

    results = await retriever.search("hello", limit=2)

    assert vector_repository.last_vector == [5.0]
    assert vector_repository.last_limit == 2
    assert [r.chunk_id for r in results] == ["p1", "p2"]
    assert results[0].content == "hello world"
    assert results[0].source == "a.pdf"
    assert results[0].score == 0.9


async def test_search_defaults_missing_score_to_zero() -> None:
    """Points without a score (e.g. from upsert-only paths) should default to score 0.0."""
    points = [VectorPoint(id="p1", vector=[0.1], payload={})]
    retriever = DenseRetriever(_FakeEmbeddingProvider(), _FakeVectorRepository(points))

    results = await retriever.search("hello", limit=1)

    assert results[0].score == 0.0
    assert results[0].content == ""
    assert results[0].source == ""
