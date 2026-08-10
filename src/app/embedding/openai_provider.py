"""Embedding provider backed by the OpenAI (or OpenAI-compatible) embeddings API."""

import httpx

from app.embedding.base import batch_texts


class OpenAiEmbeddingProvider:
    """Embeds text via an OpenAI-compatible `/embeddings` endpoint, batching requests."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        batch_size: int,
        timeout: float = 60.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._batch_size = batch_size
        self._timeout = timeout
        self._client = client

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts in batches, returning one vector per input in the same order."""
        if self._client is not None:
            return await self._embed_with(self._client, texts)
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            return await self._embed_with(client, texts)

    async def _embed_with(self, client: httpx.AsyncClient, texts: list[str]) -> list[list[float]]:
        """Send batched embedding requests using the given client."""
        vectors: list[list[float]] = []
        headers = {"Authorization": f"Bearer {self._api_key}"}
        for batch in batch_texts(texts, self._batch_size):
            response = await client.post(
                f"{self._base_url}/embeddings",
                json={"model": self._model, "input": batch},
                headers=headers,
            )
            response.raise_for_status()
            vectors.extend(item["embedding"] for item in response.json()["data"])
        return vectors
