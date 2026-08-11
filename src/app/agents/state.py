"""Shared LangGraph state schema for the Enterprise RAG agent graph."""

from typing import TypedDict

from app.models.citation import Citation
from app.models.retrieval import RetrievedChunk


class GraphState(TypedDict, total=False):
    """State threaded through the LangGraph nodes for a single query."""

    query: str
    rewritten_query: str
    route: str
    retrieved_chunks: list[RetrievedChunk]
    tool_result: str | None
    answer: str
    citations: list[Citation]
    confidence: float
