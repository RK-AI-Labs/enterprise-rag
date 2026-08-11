"""Postgres-backed implementation of the document registry repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import DocumentRecord
from app.models.document import Document, DocumentStatus


class SqlAlchemyDocumentRepository:
    """`DocumentRepository` implementation backed by a SQLAlchemy async session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, filename: str, content_type: str, size_bytes: int) -> Document:
        """Create and persist a new document registry entry."""
        record = DocumentRecord(filename=filename, content_type=content_type, size_bytes=size_bytes)
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return Document.model_validate(record)

    async def get(self, document_id: uuid.UUID) -> Document | None:
        """Return the document with the given ID, or None if it does not exist."""
        record = await self._session.get(DocumentRecord, document_id)
        return Document.model_validate(record) if record is not None else None

    async def list(self) -> list[Document]:
        """Return all documents in the registry, oldest first."""
        result = await self._session.scalars(
            select(DocumentRecord).order_by(DocumentRecord.created_at)
        )
        return [Document.model_validate(record) for record in result]

    async def update_status(
        self, document_id: uuid.UUID, status: DocumentStatus
    ) -> Document | None:
        """Update a document's lifecycle status, returning the updated entity or None."""
        record = await self._session.get(DocumentRecord, document_id)
        if record is None:
            return None
        record.status = status.value
        await self._session.flush()
        await self._session.refresh(record)
        return Document.model_validate(record)

    async def delete(self, document_id: uuid.UUID) -> bool:
        """Delete a document by ID, returning True if a row was removed."""
        record = await self._session.get(DocumentRecord, document_id)
        if record is None:
            return False
        await self._session.delete(record)
        await self._session.flush()
        return True
