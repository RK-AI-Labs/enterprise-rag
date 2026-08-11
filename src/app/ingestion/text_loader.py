"""Plain text and Markdown document loader. Both are treated as a single logical page."""

from app.ingestion.base import LoadedDocument, LoadedPage


class TextLoader:
    """Loads raw text from `.txt`/`.md` files, decoding as UTF-8."""

    def __init__(self, content_type: str) -> None:
        self._content_type = content_type

    def load(self, data: bytes, filename: str) -> LoadedDocument:
        """Decode the given bytes as UTF-8 text."""
        text = data.decode("utf-8")
        return LoadedDocument(
            source=filename,
            content_type=self._content_type,
            pages=[LoadedPage(text=text, page_number=None)],
        )
