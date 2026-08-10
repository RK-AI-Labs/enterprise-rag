"""Unit tests for `QdrantVectorRepository`, backed by Qdrant's in-memory mode."""

from collections.abc import AsyncGenerator

import pytest
from qdrant_client import AsyncQdrantClient

from app.models.vector import VectorPoint
from app.repositories.vector_repository import QdrantVectorRepository
from app.vectorstore.collections import ensure_collection

COLLECTION = "test-collection"
POINT_ID = "11111111-1111-1111-1111-111111111111"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncQdrantClient]:
    """Provide an in-memory Qdrant client with a ready test collection."""
    qdrant_client = AsyncQdrantClient(location=":memory:")
    await ensure_collection(qdrant_client, COLLECTION, vector_size=3)
    yield qdrant_client
    await qdrant_client.close()


async def test_upsert_and_search_returns_matching_point(client: AsyncQdrantClient) -> None:
    """A point upserted into the index should be returned by a search for a similar vector."""
    repo = QdrantVectorRepository(client, COLLECTION)
    point = VectorPoint(id=POINT_ID, vector=[0.1, 0.2, 0.3], payload={"source": "a.pdf"})

    await repo.upsert([point])
    results = await repo.search([0.1, 0.2, 0.3], limit=5)

    assert len(results) == 1
    assert results[0].id == POINT_ID
    assert results[0].payload == {"source": "a.pdf"}
    assert len(results[0].vector) == 3
    assert results[0].score is not None


async def test_delete_removes_point(client: AsyncQdrantClient) -> None:
    """Deleting a point by ID should remove it from subsequent search results."""
    repo = QdrantVectorRepository(client, COLLECTION)
    await repo.upsert([VectorPoint(id=POINT_ID, vector=[0.1, 0.2, 0.3])])

    await repo.delete([POINT_ID])
    results = await repo.search([0.1, 0.2, 0.3], limit=5)

    assert results == []
