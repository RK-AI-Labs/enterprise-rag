"""Async SQLAlchemy engine and session factory, configured from application settings."""

from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import Settings, get_settings


def create_engine(settings: Settings | None = None) -> AsyncEngine:
    """Build a new async engine from settings. Caller owns the engine's lifecycle."""
    settings = settings or get_settings()
    return create_async_engine(settings.postgres_dsn, pool_pre_ping=True)


@lru_cache
def get_engine() -> AsyncEngine:
    """Return a process-wide cached async engine built from cached settings."""
    return create_engine(get_settings())


def get_session_factory(engine: AsyncEngine | None = None) -> async_sessionmaker[AsyncSession]:
    """Build a session factory bound to the given engine, or the default cached engine."""
    return async_sessionmaker(engine or get_engine(), expire_on_commit=False)
