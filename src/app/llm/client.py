"""LLM client backed by an OpenAI-compatible `/chat/completions` endpoint (Ollama or OpenAI)."""

import httpx

from app.llm.base import ChatMessage


class OpenAiCompatibleLlmClient:
    """Generates chat completions via any OpenAI-compatible `/chat/completions` API."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str | None = None,
        temperature: float = 0.0,
        timeout: float = 120.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._temperature = temperature
        self._timeout = timeout
        self._client = client

    async def generate(self, messages: list[ChatMessage]) -> str:
        """Send `messages` to the chat completions endpoint and return the reply text."""
        if self._client is not None:
            return await self._generate_with(self._client, messages)
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            return await self._generate_with(client, messages)

    async def _generate_with(self, client: httpx.AsyncClient, messages: list[ChatMessage]) -> str:
        """Post `messages` using the given client and extract the completion text."""
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        response = await client.post(
            f"{self._base_url}/chat/completions",
            json={
                "model": self._model,
                "messages": list(messages),
                "temperature": self._temperature,
            },
            headers=headers,
        )
        response.raise_for_status()
        return str(response.json()["choices"][0]["message"]["content"])
