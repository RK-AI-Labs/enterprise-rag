"""Unit tests for `SqlAlchemyDocumentRepository`, backed by an in-memory SQLite database."""

import uuid
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base
from app.models.document import DocumentStatus
from app.repositories.document_repository import SqlAlchemyDocumentRepository


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    """Provide an `AsyncSession` bound to a fresh in-memory SQLite database per test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db_session:
        yield db_session
    await engine.dispose()


async def test_create_persists_and_returns_document(session: AsyncSession) -> None:
    """Creating a document should persist it and return a matching domain entity."""
    repo = SqlAlchemyDocumentRepository(session)

    document = await repo.create(
        filename="report.pdf", content_type="application/pdf", size_bytes=1024
    )

    assert document.filename == "report.pdf"
    assert document.content_type == "application/pdf"
    assert document.size_bytes == 1024
    assert document.status == DocumentStatus.PENDING


async def test_get_returns_none_for_missing_document(session: AsyncSession) -> None:
    """`get` should return None when no document with the given ID exists."""
    repo = SqlAlchemyDocumentRepository(session)

    assert await repo.get(uuid.uuid4()) is None


async def test_get_returns_created_document(session: AsyncSession) -> None:
    """`get` should return the previously created document by ID."""
    repo = SqlAlchemyDocumentRepository(session)
    created = await repo.create(filename="a.txt", content_type="text/plain", size_bytes=5)

    fetched = await repo.get(created.id)

    assert fetched is not None
    assert fetched.id == created.id


async def test_list_returns_all_documents_oldest_first() -> None:
    """`list` should return all documents ordered by creation time."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db_session:
        repo = SqlAlchemyDocumentRepository(db_session)
        first = await repo.create(filename="1.txt", content_type="text/plain", size_bytes=1)
        second = await repo.create(filename="2.txt", content_type="text/plain", size_bytes=2)

        documents = await repo.list()

        assert [d.id for d in documents] == [first.id, second.id]
    await engine.dispose()


async def test_update_status_changes_status(session: AsyncSession) -> None:
    """`update_status` should persist the new status and return the updated entity."""
    repo = SqlAlchemyDocumentRepository(session)
    created = await repo.create(filename="a.txt", content_type="text/plain", size_bytes=5)

    updated = await repo.update_status(created.id, DocumentStatus.COMPLETED)

    assert updated is not None
    assert updated.status == DocumentStatus.COMPLETED


async def test_update_status_returns_none_for_missing_document(session: AsyncSession) -> None:
    """`update_status` should return None when the document does not exist."""
    repo = SqlAlchemyDocumentRepository(session)

    assert await repo.update_status(uuid.uuid4(), DocumentStatus.FAILED) is None


async def test_delete_removes_document(session: AsyncSession) -> None:
    """`delete` should remove the document and return True."""
    repo = SqlAlchemyDocumentRepository(session)
    created = await repo.create(filename="a.txt", content_type="text/plain", size_bytes=5)

    assert await repo.delete(created.id) is True
    assert await repo.get(created.id) is None


async def test_delete_returns_false_for_missing_document(session: AsyncSession) -> None:
    """`delete` should return False when no matching document exists."""
    repo = SqlAlchemyDocumentRepository(session)

    assert await repo.delete(uuid.uuid4()) is False
