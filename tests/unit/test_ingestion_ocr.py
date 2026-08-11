"""Unit tests for the OCR abstraction stub."""

import pytest

from app.ingestion.ocr import NotImplementedOcrProvider


def test_not_implemented_ocr_provider_raises() -> None:
    """The placeholder OCR provider should always raise `NotImplementedError`."""
    provider = NotImplementedOcrProvider()

    with pytest.raises(NotImplementedError):
        provider.extract_text(b"fake image bytes")
