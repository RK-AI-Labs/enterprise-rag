"""Unit tests for `LlmResponseGenerator`."""

from app.llm.base import ChatMessage
from app.llm.response_generator import LlmResponseGenerator
from app.models.retrieval import RetrievedChunk


class _FakeLlmClient:
    """Fake `LlmClient` that records the messages it was called with."""

    def __init__(self, reply: str) -> None:
        self._reply = reply
        self.last_messages: list[ChatMessage] | None = None

    async def generate(self, messages: list[ChatMessage]) -> str:
        self.last_messages = messages
        return self._reply


def _chunk(chunk_id: str, content: str) -> RetrievedChunk:
    return RetrievedChunk(chunk_id=chunk_id, content=content, score=1.0, source="s")


async def test_generate_includes_system_prompt_and_formatted_context() -> None:
    """The generator should send a system message plus a user message with context/question."""
    llm_client = _FakeLlmClient("the answer")
    generator = LlmResponseGenerator(llm_client)
    chunks = [_chunk("c1", "hello world")]

    answer = await generator.generate("what is it?", chunks)

    assert answer == "the answer"
    assert llm_client.last_messages is not None
    assert llm_client.last_messages[0]["role"] == "system"
    user_message = llm_client.last_messages[1]
    assert user_message["role"] == "user"
    assert "[c1] hello world" in user_message["content"]
    assert "what is it?" in user_message["content"]


async def test_generate_handles_empty_chunks() -> None:
    """With no retrieved chunks, the prompt should note there is no context."""
    llm_client = _FakeLlmClient("I don't know")
    generator = LlmResponseGenerator(llm_client)

    await generator.generate("a question", [])

    assert llm_client.last_messages is not None
    assert "(no context retrieved)" in llm_client.last_messages[1]["content"]
