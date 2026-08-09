"""Repository interfaces (ports) decoupling services from persistence infrastructure."""

import uuid
from typing import Protocol

from app.models.document import Document, DocumentStatus
from app.models.vector import VectorPoint


class DocumentRepository(Protocol):
    """Persistence abstraction for document registry metadata (Postgres-backed)."""

    async def create(self, *, filename: str, content_type: str, size_bytes: int) -> Document:
        """Create and persist a new document registry entry."""
        ...

    async def get(self, document_id: uuid.UUID) -> Document | None:
        """Return the document with the given ID, or None if it does not exist."""
        ...

    async def list(self) -> list[Document]:
        """Return all documents in the registry, oldest first."""
        ...

    async def update_status(
        self, document_id: uuid.UUID, status: DocumentStatus
    ) -> Document | None:
        """Update a document's lifecycle status, returning the updated entity or None."""
        ...

    async def delete(self, document_id: uuid.UUID) -> bool:
        """Delete a document by ID, returning True if a row was removed."""
        ...


class VectorRepository(Protocol):
    """Persistence abstraction for vector-store records (Qdrant-backed)."""

    async def upsert(self, points: list[VectorPoint]) -> None:
        """Insert or update the given points in the vector index."""
        ...

    async def search(self, vector: list[float], limit: int = 5) -> list[VectorPoint]:
        """Return the nearest points to the given query vector."""
        ...

    async def delete(self, point_ids: list[str]) -> None:
        """Remove points by ID from the vector index."""
        ...
