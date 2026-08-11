"""Provider-agnostic LLM client interface for chat-style text generation."""

from typing import Literal, Protocol, TypedDict, runtime_checkable


class ChatMessage(TypedDict):
    """A single OpenAI-compatible chat message."""

    role: Literal["system", "user", "assistant"]
    content: str


@runtime_checkable
class LlmClient(Protocol):
    """Generates a chat completion from a sequence of messages."""

    async def generate(self, messages: list[ChatMessage]) -> str:
        """Return the assistant's text completion for the given message history."""
        ...
