"""Helpers for managing Qdrant collections."""

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams


async def ensure_collection(
    client: AsyncQdrantClient,
    name: str,
    vector_size: int,
    distance: Distance = Distance.COSINE,
) -> None:
    """Create the collection if it does not already exist. Idempotent and safe to call repeatedly."""
    if not await client.collection_exists(name):
        await client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=distance),
        )
