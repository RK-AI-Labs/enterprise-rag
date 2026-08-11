"""Chunking of loaded documents into overlapping, metadata-tagged text chunks."""

import uuid

from app.ingestion.base import LoadedDocument
from app.models.chunk import Chunk


def chunk_document(
    document: LoadedDocument,
    document_id: uuid.UUID,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    """Split a loaded document's pages into overlapping chunks, preserving page numbers.

    Chunking is character-based: each page's text is split into windows of `chunk_size`
    characters, advancing by `chunk_size - chunk_overlap` each step. Empty pages produce no
    chunks. `chunk_index` is assigned sequentially across the whole document.
    """
    step = chunk_size - chunk_overlap
    chunks: list[Chunk] = []
    for page in document.pages:
        text = page.text.strip()
        if not text:
            continue
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(
                Chunk(
                    document_id=document_id,
                    chunk_index=len(chunks),
                    content=text[start:end],
                    source=document.source,
                    page_number=page.page_number,
                    metadata={"content_type": document.content_type},
                )
            )
            if end == len(text):
                break
            start += step
    return chunks
