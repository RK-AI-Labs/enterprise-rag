"""Response Agent node: synthesizes the final answer from retrieved context (or tool output).

No concrete LLM-backed generator is implemented yet — that lands in Phase 10 (`app/llm/`).
`NotImplementedResponseGenerator` is a placeholder so the graph is wireable end-to-end.
"""

from typing import Protocol

from app.agents.state import GraphState
from app.models.retrieval import RetrievedChunk


class ResponseGenerator(Protocol):
    """Narrow interface for whatever synthesizes the final answer text."""

    async def generate(self, query: str, chunks: list[RetrievedChunk]) -> str:
        """Return a grounded answer to `query` given the supporting `chunks`."""
        ...


class NotImplementedResponseGenerator:
    """Placeholder `ResponseGenerator`; a real LLM-backed implementation is future work."""

    async def generate(self, query: str, chunks: list[RetrievedChunk]) -> str:
        """Always raise, since no response generator is implemented in the MVP."""
        raise NotImplementedError("Response generation is not implemented in the MVP.")


def _tool_result_as_chunk(tool_result: str) -> RetrievedChunk:
    """Wrap a tool's textual result as a `RetrievedChunk` so it can feed the response generator."""
    return RetrievedChunk(chunk_id="tool-result", content=tool_result, score=1.0, source="tool")


# Note: the returned closure is intentionally left without an explicit `Callable[...]` return
# annotation. LangGraph's `StateGraph.add_node` overloads match against the closure's own
# precise inferred type; wrapping it in a `Callable[[GraphState], Coroutine[...]]` alias breaks
# that overload resolution under mypy (verified against langgraph 1.2.10).
def build_response_node(response_generator: ResponseGenerator):
    """Build the Response Agent node bound to the given response generator."""

    async def response_node(state: GraphState) -> GraphState:
        """Synthesize the final answer from retrieved chunks, or the tool result if present."""
        query = state.get("rewritten_query") or state["query"]
        tool_result = state.get("tool_result")
        chunks = (
            [_tool_result_as_chunk(tool_result)]
            if tool_result is not None
            else state.get("retrieved_chunks", [])
        )
        answer = await response_generator.generate(query, chunks)
        return {"answer": answer}

    return response_node
