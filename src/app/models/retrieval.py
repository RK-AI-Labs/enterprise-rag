"""Domain model for a single retrieval hit, independent of the retriever that produced it."""

from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """A chunk returned by a retriever, with provenance and a relevance score."""

    chunk_id: str
    content: str
    score: float
    source: str
    metadata: dict[str, object] = Field(default_factory=dict)
