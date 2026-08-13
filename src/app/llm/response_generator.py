"""Concrete `ResponseGenerator` (see `app/agents/response.py`) backed by an `LlmClient`.

Structurally satisfies the `ResponseGenerator` protocol without importing `app.agents`, keeping
`app/llm/` independent of the agent-orchestration layer.
"""

from app.llm.base import ChatMessage, LlmClient
from app.models.retrieval import RetrievedChunk
from app.prompts.loader import load_prompt


def _format_context(chunks: list[RetrievedChunk]) -> str:
    """Render retrieved chunks as a numbered, chunk-ID-tagged context block."""
    if not chunks:
        return "(no context retrieved)"
    return "\n\n".join(f"[{chunk.chunk_id}] {chunk.content}" for chunk in chunks)


class LlmResponseGenerator:
    """Generates grounded answers via an `LlmClient`, using the externalized prompt templates."""

    def __init__(self, llm_client: LlmClient) -> None:
        self._llm_client = llm_client

    async def generate(self, query: str, chunks: list[RetrievedChunk]) -> str:
        """Return the LLM's answer to `query`, grounded in the supplied `chunks`."""
        print(f"Generating response for query: {query} with {len(chunks)} chunks")
        prompt_name = "answer" if chunks else "no_context"
        prompt = load_prompt(prompt_name).format(context=_format_context(chunks), question=query)
        messages: list[ChatMessage] = [
            {"role": "system", "content": load_prompt("system")},
            {"role": "user", "content": prompt},
        ]
        return await self._llm_client.generate(messages)
