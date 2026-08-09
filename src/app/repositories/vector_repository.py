"""Qdrant-backed implementation of the vector-store repository."""

from typing import Any, cast

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct

from app.models.vector import VectorPoint


class QdrantVectorRepository:
    """`VectorRepository` implementation backed by a single Qdrant collection."""

    def __init__(self, client: AsyncQdrantClient, collection_name: str) -> None:
        self._client = client
        self._collection_name = collection_name

    async def upsert(self, points: list[VectorPoint]) -> None:
        """Insert or update the given points in the vector index."""
        await self._client.upsert(
            collection_name=self._collection_name,
            points=[
                PointStruct(id=point.id, vector=point.vector, payload=point.payload)
                for point in points
            ],
        )

    async def search(self, vector: list[float], limit: int = 5) -> list[VectorPoint]:
        """Return the nearest points to the given query vector."""
        response = await self._client.query_points(
            collection_name=self._collection_name,
            query=vector,
            limit=limit,
            with_vectors=True,
        )
        return [
            VectorPoint(
                id=str(point.id),
                vector=cast("list[float]", point.vector) if point.vector else [],
                payload=point.payload or {},
            )
            for point in response.points
        ]

    async def delete(self, point_ids: list[str]) -> None:
        """Remove points by ID from the vector index."""
        await self._client.delete(
            collection_name=self._collection_name,
            points_selector=cast("list[Any]", point_ids),
        )
