"""Unit tests for `OllamaEmbeddingProvider`."""

import json

import httpx
import pytest

from app.embedding.ollama_provider import OllamaEmbeddingProvider


async def test_embed_sends_batched_requests_and_concatenates_vectors() -> None:
    """Texts should be split into batches, each posted to `/api/embed`, and results merged."""
    requests: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        parsed = json.loads(request.read())
        requests.append(parsed)
        vectors = [[float(len(text))] for text in parsed["input"]]
        return httpx.Response(200, json={"embeddings": vectors})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OllamaEmbeddingProvider(
        base_url="http://localhost:11434",
        model="nomic-embed-text",
        batch_size=2,
        client=client,
    )

    result = await provider.embed(["a", "bb", "ccc"])

    assert result == [[1.0], [2.0], [3.0]]
    assert len(requests) == 2
    assert requests[0] == {"model": "nomic-embed-text", "input": ["a", "bb"]}
    assert requests[1] == {"model": "nomic-embed-text", "input": ["ccc"]}
    await client.aclose()


async def test_embed_raises_on_http_error_status() -> None:
    """An HTTP error response should propagate as an `httpx.HTTPStatusError`."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OllamaEmbeddingProvider(
        base_url="http://localhost:11434",
        model="nomic-embed-text",
        batch_size=10,
        client=client,
    )

    with pytest.raises(httpx.HTTPStatusError):
        await provider.embed(["a"])
    await client.aclose()
