"""Unit tests for the document chunker."""

import uuid

from app.ingestion.base import LoadedDocument, LoadedPage
from app.parsing.chunker import chunk_document


def test_chunk_document_splits_page_with_overlap() -> None:
    """A page longer than `chunk_size` should be split into overlapping chunks."""
    document = LoadedDocument(
        source="sample.txt",
        content_type="text/plain",
        pages=[LoadedPage(text="a" * 25, page_number=1)],
    )
    document_id = uuid.uuid4()

    chunks = chunk_document(document, document_id, chunk_size=10, chunk_overlap=2)

    assert [c.content for c in chunks] == ["a" * 10, "a" * 10, "a" * 9]
    assert [c.chunk_index for c in chunks] == [0, 1, 2]
    assert all(c.document_id == document_id for c in chunks)
    assert all(c.source == "sample.txt" for c in chunks)
    assert all(c.page_number == 1 for c in chunks)
    assert all(c.metadata == {"content_type": "text/plain"} for c in chunks)


def test_chunk_document_preserves_page_numbers_across_pages() -> None:
    """Chunk indices should be sequential across pages, and page numbers preserved."""
    document = LoadedDocument(
        source="sample.pdf",
        content_type="application/pdf",
        pages=[
            LoadedPage(text="first page text", page_number=1),
            LoadedPage(text="second page text", page_number=2),
        ],
    )

    chunks = chunk_document(document, uuid.uuid4(), chunk_size=100, chunk_overlap=0)

    assert len(chunks) == 2
    assert chunks[0].chunk_index == 0
    assert chunks[0].page_number == 1
    assert chunks[0].content == "first page text"
    assert chunks[1].chunk_index == 1
    assert chunks[1].page_number == 2
    assert chunks[1].content == "second page text"


def test_chunk_document_skips_empty_pages() -> None:
    """Pages with only whitespace should produce no chunks."""
    document = LoadedDocument(
        source="sample.txt",
        content_type="text/plain",
        pages=[
            LoadedPage(text="   ", page_number=1),
            LoadedPage(text="real content", page_number=2),
        ],
    )

    chunks = chunk_document(document, uuid.uuid4(), chunk_size=100, chunk_overlap=0)

    assert len(chunks) == 1
    assert chunks[0].page_number == 2
