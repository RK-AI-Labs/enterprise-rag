"""Domain model for an ingested document (registry metadata, independent of persistence)."""

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class DocumentStatus(StrEnum):
    """Lifecycle state of a document within the ingestion pipeline."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(BaseModel):
    """Domain entity representing a document tracked in the metadata registry."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    status: DocumentStatus = DocumentStatus.PENDING
    created_at: datetime
    updated_at: datetime
