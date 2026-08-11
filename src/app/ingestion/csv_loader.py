"""CSV document loader using the standard library `csv` module."""

import csv
import io

from app.ingestion.base import LoadedDocument, LoadedPage


class CsvLoader:
    """Loads CSV files, rendering each row as a line of comma-joined text."""

    def load(self, data: bytes, filename: str) -> LoadedDocument:
        """Read CSV rows from the given bytes and join them into a single text block."""
        text_stream = io.StringIO(data.decode("utf-8"))
        rows = csv.reader(text_stream)
        text = "\n".join(", ".join(row) for row in rows)
        return LoadedDocument(
            source=filename,
            content_type="text/csv",
            pages=[LoadedPage(text=text, page_number=None)],
        )
