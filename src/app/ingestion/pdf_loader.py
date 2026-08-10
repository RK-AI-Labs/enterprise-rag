"""PDF document loader using PyMuPDF, extracting text per page."""

import pymupdf

from app.ingestion.base import LoadedDocument, LoadedPage


class PdfLoader:
    """Loads text from PDF files, preserving page boundaries."""

    def load(self, data: bytes, filename: str) -> LoadedDocument:
        """Extract per-page text from the given PDF bytes."""
        with pymupdf.open(stream=data, filetype="pdf") as document:
            pages = [
                LoadedPage(text=page.get_text(), page_number=index + 1)
                for index, page in enumerate(document)
            ]
        return LoadedDocument(source=filename, content_type="application/pdf", pages=pages)
