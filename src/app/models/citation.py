"""Domain model for a citation referencing a chunk that grounds part of an answer."""

from pydantic import BaseModel


class Citation(BaseModel):
    """A single grounding reference from an answer back to a retrieved chunk."""

    chunk_id: str
    source: str
    score: float
