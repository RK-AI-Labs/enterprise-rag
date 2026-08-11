"""Qdrant async client factory, configured from application settings."""

from functools import lru_cache

from qdrant_client import AsyncQdrantClient

from app.config.settings import Settings, get_settings


def create_qdrant_client(settings: Settings | None = None) -> AsyncQdrantClient:
    """Build a new async Qdrant client from settings. Caller owns the client's lifecycle."""
    settings = settings or get_settings()
    return AsyncQdrantClient(url=settings.qdrant_url)


@lru_cache
def get_qdrant_client() -> AsyncQdrantClient:
    """Return a process-wide cached async Qdrant client built from cached settings."""
    return create_qdrant_client(get_settings())
