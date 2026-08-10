"""Provider-agnostic embedding interface and batching helper."""

from collections.abc import Iterator, Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Turns text into dense vector embeddings, independent of the backing model/API."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts, returning one vector per input in the same order."""
        ...


def batch_texts(texts: Sequence[str], batch_size: int) -> Iterator[list[str]]:
    """Yield successive `batch_size`-sized slices of `texts`, preserving order."""
    for start in range(0, len(texts), batch_size):
        yield list(texts[start : start + batch_size])
