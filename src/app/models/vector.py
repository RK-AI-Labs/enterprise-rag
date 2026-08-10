"""Domain model for a single vector-store record (embedding + payload metadata)."""

from pydantic import BaseModel, Field


class VectorPoint(BaseModel):
    """A single point stored in the vector index: an embedding plus arbitrary payload metadata."""

    id: str
    vector: list[float]
    payload: dict[str, object] = Field(default_factory=dict)
    score: float | None = None
