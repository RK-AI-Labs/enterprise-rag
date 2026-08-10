"""Query Understanding node: normalizes the raw user query before routing/retrieval."""

from app.agents.state import GraphState


async def query_understanding_node(state: GraphState) -> GraphState:
    """Normalize the raw query. Placeholder for future LLM-based query rewriting (Phase 10+)."""
    return {"rewritten_query": state["query"].strip()}
