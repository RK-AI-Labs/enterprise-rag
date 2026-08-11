"""Unit tests for `OpenAiEmbeddingProvider`."""

import json

import httpx
import pytest

from app.embedding.openai_provider import OpenAiEmbeddingProvider


async def test_embed_sends_batched_requests_with_auth_header() -> None:
    """Texts should be split into batches, posted to `/embeddings` with a bearer token."""
    requests: list[dict[str, object]] = []
    auth_headers: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        parsed = json.loads(request.read())
        requests.append(parsed)
        auth_headers.append(request.headers.get("authorization"))
        data = [{"embedding": [float(len(text))]} for text in parsed["input"]]
        return httpx.Response(200, json={"data": data})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OpenAiEmbeddingProvider(
        base_url="https://api.openai.com/v1",
        api_key="sk-test",
        model="text-embedding-3-small",
        batch_size=2,
        client=client,
    )

    result = await provider.embed(["a", "bb", "ccc"])

    assert result == [[1.0], [2.0], [3.0]]
    assert len(requests) == 2
    assert requests[0] == {"model": "text-embedding-3-small", "input": ["a", "bb"]}
    assert requests[1] == {"model": "text-embedding-3-small", "input": ["ccc"]}
    assert all(header == "Bearer sk-test" for header in auth_headers)
    await client.aclose()


async def test_embed_raises_on_http_error_status() -> None:
    """An HTTP error response should propagate as an `httpx.HTTPStatusError`."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "unauthorized"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OpenAiEmbeddingProvider(
        base_url="https://api.openai.com/v1",
        api_key="sk-bad",
        model="text-embedding-3-small",
        batch_size=10,
        client=client,
    )

    with pytest.raises(httpx.HTTPStatusError):
        await provider.embed(["a"])
    await client.aclose()
