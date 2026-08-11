"""Unit tests for `get_session`, backed by an in-memory SQLite database."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import session as session_module


@pytest.fixture
def session_factory() -> async_sessionmaker:  # type: ignore[type-arg]
    """Build a session factory bound to a fresh in-memory SQLite engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    return async_sessionmaker(engine, expire_on_commit=False)


async def test_get_session_yields_usable_session_and_commits(
    monkeypatch: pytest.MonkeyPatch,
    session_factory: async_sessionmaker,  # type: ignore[type-arg]
) -> None:
    """`get_session` should yield a working session and commit when the block succeeds."""
    monkeypatch.setattr(session_module, "get_session_factory", lambda: session_factory)

    async for db_session in session_module.get_session():
        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1


async def test_get_session_rolls_back_and_reraises_on_error(
    monkeypatch: pytest.MonkeyPatch,
    session_factory: async_sessionmaker,  # type: ignore[type-arg]
) -> None:
    """`get_session` should roll back and propagate any exception raised in the block."""
    monkeypatch.setattr(session_module, "get_session_factory", lambda: session_factory)

    with pytest.raises(RuntimeError, match="boom"):
        async for _db_session in session_module.get_session():
            raise RuntimeError("boom")
