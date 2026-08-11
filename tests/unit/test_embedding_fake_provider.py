"""Unit tests demonstrating the `EmbeddingProvider` protocol with a fake implementation."""

from app.embedding.base import EmbeddingProvider


class FakeEmbeddingProvider:
    """A minimal in-memory `EmbeddingProvider` for testing code that depends on the interface."""

    def __init__(self, dimensions: int = 3) -> None:
        self._dimensions = dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return a deterministic vector per text, based on its length."""
        return [[float(len(text))] * self._dimensions for text in texts]


async def test_fake_embedding_provider_satisfies_protocol() -> None:
    """A structurally-compatible fake should be recognized as an `EmbeddingProvider`."""
    provider: EmbeddingProvider = FakeEmbeddingProvider()

    assert isinstance(provider, EmbeddingProvider)

    vectors = await provider.embed(["ab", "abcd"])

    assert vectors == [[2.0, 2.0, 2.0], [4.0, 4.0, 4.0]]
