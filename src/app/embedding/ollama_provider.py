"""Embedding provider backed by a local/remote Ollama server."""

import httpx

from app.embedding.base import batch_texts


class OllamaEmbeddingProvider:
    """Embeds text via Ollama's `/api/embed` endpoint, batching requests."""

    def __init__(
        self,
        base_url: str,
        model: str,
        batch_size: int,
        timeout: float = 60.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
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
        for batch in batch_texts(texts, self._batch_size):
            response = await client.post(
                f"{self._base_url}/api/embed",
                json={"model": self._model, "input": batch},
            )
            response.raise_for_status()
            vectors.extend(response.json()["embeddings"])
        return vectors
