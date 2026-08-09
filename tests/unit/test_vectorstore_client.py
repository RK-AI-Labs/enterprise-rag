"""Unit tests for Qdrant collection management helpers and client factory."""

from qdrant_client import AsyncQdrantClient

from app.config.settings import Settings
from app.vectorstore.client import create_qdrant_client, get_qdrant_client
from app.vectorstore.collections import ensure_collection


def test_create_qdrant_client_returns_client_for_settings_url() -> None:
    """The factory should build an `AsyncQdrantClient` targeting the settings' Qdrant URL."""
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    client = create_qdrant_client(settings)

    assert isinstance(client, AsyncQdrantClient)


def test_get_qdrant_client_is_cached() -> None:
    """`get_qdrant_client` should return the same cached instance across calls."""
    assert get_qdrant_client() is get_qdrant_client()


async def test_ensure_collection_is_idempotent() -> None:
    """Calling `ensure_collection` twice should not raise and should leave one collection."""
    client = AsyncQdrantClient(location=":memory:")

    await ensure_collection(client, "idempotent", vector_size=4)
    await ensure_collection(client, "idempotent", vector_size=4)

    assert await client.collection_exists("idempotent")
    await client.close()
