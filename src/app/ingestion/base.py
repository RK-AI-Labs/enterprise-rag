"""Shared types and the loader interface for document ingestion."""

from typing import Protocol

from pydantic import BaseModel


class LoadedPage(BaseModel):
    """A single page or logical unit of raw text extracted from a source document."""

    text: str
    page_number: int | None = None


class LoadedDocument(BaseModel):
    """Raw text extracted from a source document, before chunking."""

    source: str
    content_type: str
    pages: list[LoadedPage]


class DocumentLoader(Protocol):
    """Extracts raw text (with page boundaries where applicable) from document bytes."""

    def load(self, data: bytes, filename: str) -> LoadedDocument:
        """Parse the given file bytes into a `LoadedDocument`."""
        ...
