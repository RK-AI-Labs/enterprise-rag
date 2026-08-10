"""Unit tests for the loader registry."""

import pytest

from app.core.exceptions import ValidationError
from app.ingestion.csv_loader import CsvLoader
from app.ingestion.docx_loader import DocxLoader
from app.ingestion.excel_loader import ExcelLoader
from app.ingestion.pdf_loader import PdfLoader
from app.ingestion.pptx_loader import PptxLoader
from app.ingestion.registry import get_loader, load_document
from app.ingestion.text_loader import TextLoader


@pytest.mark.parametrize(
    ("filename", "expected_type"),
    [
        ("report.pdf", PdfLoader),
        ("report.PDF", PdfLoader),
        ("report.docx", DocxLoader),
        ("report.txt", TextLoader),
        ("report.md", TextLoader),
        ("report.csv", CsvLoader),
        ("report.xlsx", ExcelLoader),
        ("report.pptx", PptxLoader),
    ],
)
def test_get_loader_dispatches_by_extension(filename: str, expected_type: type) -> None:
    """`get_loader` should return the loader registered for the file's extension."""
    assert isinstance(get_loader(filename), expected_type)


def test_get_loader_raises_for_unsupported_extension() -> None:
    """`get_loader` should raise `ValidationError` for an unregistered extension."""
    with pytest.raises(ValidationError):
        get_loader("report.exe")


def test_load_document_uses_registered_loader() -> None:
    """`load_document` should dispatch to the loader matching the filename's extension."""
    loaded = load_document(b"plain text", "notes.txt")

    assert loaded.content_type == "text/plain"
    assert loaded.pages[0].text == "plain text"
