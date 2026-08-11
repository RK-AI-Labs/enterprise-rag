"""Unit tests for `ingest_document`, using a real SQLite-backed document repository."""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base
from app.ingestion.pipeline import ingest_document
from app.models.document import DocumentStatus
from app.models.vector import VectorPoint
from app.repositories.document_repository import SqlAlchemyDocumentRepository


class _FakeEmbeddingProvider:
    """Deterministic fake embedding provider for tests."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text))] for text in texts]


class _FakeVectorRepository:
    """Fake `VectorRepository` recording upserted points."""

    def __init__(self) -> None:
        self.upserted: list[VectorPoint] = []

    async def upsert(self, points: list[VectorPoint]) -> None:
        self.upserted.extend(points)

    async def search(self, vector: list[float], limit: int = 5) -> list[VectorPoint]:
        raise NotImplementedError

    async def delete(self, point_ids: list[str]) -> None:
        raise NotImplementedError


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


async def test_ingest_document_persists_and_embeds_chunks(session: AsyncSession) -> None:
    """Ingesting a text file should register the document and upsert one point per chunk."""
    document_repository = SqlAlchemyDocumentRepository(session)
    vector_repository = _FakeVectorRepository()

    document = await ingest_document(
        b"hello world, this is a test document.",
        "notes.txt",
        document_repository=document_repository,
        vector_repository=vector_repository,
        embedding_provider=_FakeEmbeddingProvider(),
        chunk_size=1000,
        chunk_overlap=0,
    )

    assert document.filename == "notes.txt"
    assert document.status == DocumentStatus.COMPLETED
    assert len(vector_repository.upserted) == 1
    assert (
        vector_repository.upserted[0].payload["content"] == "hello world, this is a test document."
    )


async def test_ingest_document_with_no_extractable_text_registers_with_no_chunks(
    session: AsyncSession,
) -> None:
    """A document with no extractable text should still be registered, with zero chunks."""
    document_repository = SqlAlchemyDocumentRepository(session)
    vector_repository = _FakeVectorRepository()

    document = await ingest_document(
        b"   ",
        "empty.txt",
        document_repository=document_repository,
        vector_repository=vector_repository,
        embedding_provider=_FakeEmbeddingProvider(),
        chunk_size=1000,
        chunk_overlap=0,
    )

    assert document.status == DocumentStatus.COMPLETED
    assert vector_repository.upserted == []
