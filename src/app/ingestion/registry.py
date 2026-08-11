"""Loader registry: dispatches document bytes to the loader for a given file extension."""

from pathlib import PurePosixPath

from app.core.exceptions import ValidationError
from app.ingestion.base import DocumentLoader, LoadedDocument
from app.ingestion.csv_loader import CsvLoader
from app.ingestion.docx_loader import DocxLoader
from app.ingestion.excel_loader import ExcelLoader
from app.ingestion.pdf_loader import PdfLoader
from app.ingestion.pptx_loader import PptxLoader
from app.ingestion.text_loader import TextLoader

_LOADERS_BY_EXTENSION: dict[str, DocumentLoader] = {
    ".pdf": PdfLoader(),
    ".docx": DocxLoader(),
    ".txt": TextLoader(content_type="text/plain"),
    ".md": TextLoader(content_type="text/markdown"),
    ".csv": CsvLoader(),
    ".xlsx": ExcelLoader(),
    ".pptx": PptxLoader(),
}


def get_loader(filename: str) -> DocumentLoader:
    """Return the loader registered for the given filename's extension.

    Raises `ValidationError` if the extension is not supported.
    """
    extension = PurePosixPath(filename).suffix.lower()
    loader = _LOADERS_BY_EXTENSION.get(extension)
    if loader is None:
        raise ValidationError(f"Unsupported document extension: {extension or '(none)'}")
    return loader


def load_document(data: bytes, filename: str) -> LoadedDocument:
    """Load the given file bytes using the loader registered for its extension."""
    return get_loader(filename).load(data, filename)
