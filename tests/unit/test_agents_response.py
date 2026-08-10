"""Unit tests for the Response Agent node."""

import pytest

from app.agents.response import NotImplementedResponseGenerator, build_response_node
from app.models.retrieval import RetrievedChunk


class _FakeResponseGenerator:
    def __init__(self, answer: str) -> None:
        self._answer = answer
        self.last_query: str | None = None
        self.last_chunks: list[RetrievedChunk] | None = None

    async def generate(self, query: str, chunks: list[RetrievedChunk]) -> str:
        self.last_query = query
        self.last_chunks = chunks
        return self._answer


def _chunk(chunk_id: str) -> RetrievedChunk:
    return RetrievedChunk(chunk_id=chunk_id, content=f"content-{chunk_id}", score=1.0, source="s")


async def test_response_node_generates_from_retrieved_chunks() -> None:
    """When no tool result is present, the generator should receive the retrieved chunks."""
    generator = _FakeResponseGenerator("the answer")
    node = build_response_node(generator)
    chunks = [_chunk("a")]

    result = await node({"query": "raw", "rewritten_query": "clean", "retrieved_chunks": chunks})

    assert generator.last_query == "clean"
    assert generator.last_chunks == chunks
    assert result == {"answer": "the answer"}


async def test_response_node_wraps_tool_result_as_chunk() -> None:
    """When a tool result is present, it should be wrapped as a single `RetrievedChunk`."""
    generator = _FakeResponseGenerator("42")
    node = build_response_node(generator)

    result = await node({"query": "raw", "tool_result": "42"})

    assert generator.last_chunks is not None
    assert len(generator.last_chunks) == 1
    assert generator.last_chunks[0].content == "42"
    assert generator.last_chunks[0].source == "tool"
    assert result == {"answer": "42"}


async def test_response_node_falls_back_to_raw_query_when_not_rewritten() -> None:
    """When no rewritten query is present, the raw query should be used instead."""
    generator = _FakeResponseGenerator("ok")
    node = build_response_node(generator)

    await node({"query": "raw"})

    assert generator.last_query == "raw"


async def test_not_implemented_response_generator_raises() -> None:
    """The placeholder generator should always raise `NotImplementedError`."""
    generator = NotImplementedResponseGenerator()

    with pytest.raises(NotImplementedError):
        await generator.generate("query", [])
