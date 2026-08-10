"""Unit tests for `OpenAiCompatibleLlmClient`."""

import json

import httpx
import pytest

from app.llm.client import OpenAiCompatibleLlmClient


async def test_generate_posts_messages_and_returns_completion_text() -> None:
    """The client should POST the messages/model/temperature and return the reply content."""
    requests: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.read()))
        return httpx.Response(200, json={"choices": [{"message": {"content": "the answer"}}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    llm_client = OpenAiCompatibleLlmClient(
        base_url="http://localhost:11434/v1",
        model="qwen3",
        temperature=0.2,
        client=client,
    )
    messages = [{"role": "user", "content": "hello"}]

    result = await llm_client.generate(messages)  # type: ignore[arg-type]

    assert result == "the answer"
    assert requests == [{"model": "qwen3", "messages": messages, "temperature": 0.2}]
    await client.aclose()


async def test_generate_sends_bearer_auth_header_when_api_key_set() -> None:
    """When an API key is configured, requests should include a Bearer auth header."""
    seen_headers: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_headers.append(request.headers.get("authorization"))
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    llm_client = OpenAiCompatibleLlmClient(
        base_url="https://api.openai.com/v1",
        model="gpt-4o-mini",
        api_key="sk-test",
        client=client,
    )

    await llm_client.generate([{"role": "user", "content": "hi"}])

    assert seen_headers == ["Bearer sk-test"]
    await client.aclose()


async def test_generate_raises_on_http_error_status() -> None:
    """An HTTP error response should propagate as an `httpx.HTTPStatusError`."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    llm_client = OpenAiCompatibleLlmClient(
        base_url="http://localhost:11434/v1", model="qwen3", client=client
    )

    with pytest.raises(httpx.HTTPStatusError):
        await llm_client.generate([{"role": "user", "content": "hi"}])
    await client.aclose()
