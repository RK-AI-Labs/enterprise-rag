"""Domain model for a chunk of extracted document text, ready for embedding."""

import uuid

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """A single chunk of text extracted from a document, with provenance metadata."""

    document_id: uuid.UUID
    chunk_index: int
    content: str
    source: str
    page_number: int | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
