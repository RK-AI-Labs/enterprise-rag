"""OCR abstraction — future-ready interface, not implemented for the MVP.

Image-based documents (scanned PDFs, photos) are out of scope until a concrete OCR
provider (e.g. Tesseract, cloud OCR API) is selected post-MVP. The interface is defined
now so `app/ingestion/registry.py` and callers can be wired against it ahead of time.
"""

from typing import Protocol


class OcrProvider(Protocol):
    """Extracts text from image bytes (scanned pages, photos, etc.)."""

    def extract_text(self, data: bytes) -> str:
        """Return the text recognized in the given image bytes."""
        ...


class NotImplementedOcrProvider:
    """Placeholder `OcrProvider` that always raises; no OCR backend is wired up yet."""

    def extract_text(self, data: bytes) -> str:
        """Raise `NotImplementedError` — OCR is not implemented in the MVP."""
        raise NotImplementedError("OCR text extraction is not implemented in the MVP.")
