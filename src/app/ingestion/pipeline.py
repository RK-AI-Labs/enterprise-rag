"""End-to-end orchestration: load, chunk, embed, and persist a single uploaded document."""

import uuid

from app.embedding.base import EmbeddingProvider
from app.ingestion.registry import load_document
from app.models.document import Document, DocumentStatus
from app.models.vector import VectorPoint
from app.parsing.chunker import chunk_document
from app.repositories.interfaces import DocumentRepository, VectorRepository


async def ingest_document(
    data: bytes,
    filename: str,
    *,
    document_repository: DocumentRepository,
    vector_repository: VectorRepository,
    embedding_provider: EmbeddingProvider,
    chunk_size: int,
    chunk_overlap: int,
) -> Document:
    """Load, chunk, embed, and persist `data` as a new document, returning the final record.

    Registers the document first (status `pending`), then chunks and embeds its text, upserts
    the resulting vectors, and marks the document `completed`. Documents with no extractable
    text are still registered and marked `completed` with zero chunks.
    """
    loaded = load_document(data, filename)
    document = await document_repository.create(
        filename=filename, content_type=loaded.content_type, size_bytes=len(data)
    )
    chunks = chunk_document(loaded, document.id, chunk_size, chunk_overlap)
    if chunks:
        vectors = await embedding_provider.embed([chunk.content for chunk in chunks])
        points = [
            VectorPoint(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "content": chunk.content,
                    "source": chunk.source,
                    "document_id": str(chunk.document_id),
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        await vector_repository.upsert(points)
    updated = await document_repository.update_status(document.id, DocumentStatus.COMPLETED)
    return updated or document
