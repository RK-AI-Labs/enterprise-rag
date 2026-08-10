"""Retriever Agent node: fetches candidate chunks for the current query via hybrid retrieval."""

from typing import Protocol

from app.agents.state import GraphState
from app.models.retrieval import RetrievedChunk


class Retriever(Protocol):
    """Narrow interface for whatever retrieval strategy backs the Retriever Agent node."""

    async def search(self, query: str, limit: int) -> list[RetrievedChunk]:
        """Return the top-`limit` chunks relevant to `query`."""
        ...


# Note: the returned closure is intentionally left without an explicit `Callable[...]` return
# annotation. LangGraph's `StateGraph.add_node` overloads match against the closure's own
# precise inferred type; wrapping it in a `Callable[[GraphState], Coroutine[...]]` alias breaks
# that overload resolution under mypy (verified against langgraph 1.2.10).
def build_retriever_node(retriever: Retriever, top_k: int):
    """Build the Retriever Agent node bound to the given retriever and result limit."""

    async def retriever_node(state: GraphState) -> GraphState:
        """Retrieve candidate chunks for the (rewritten) query."""
        query = state.get("rewritten_query") or state["query"]
        chunks = await retriever.search(query, top_k)
        return {"retrieved_chunks": chunks}

    return retriever_node
