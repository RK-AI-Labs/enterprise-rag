"""Unit tests for the embedding batching helper."""

from app.embedding.base import batch_texts


def test_batch_texts_splits_into_fixed_size_batches() -> None:
    """Batches should be `batch_size` long except for a shorter final batch."""
    texts = [str(i) for i in range(5)]

    batches = list(batch_texts(texts, batch_size=2))

    assert batches == [["0", "1"], ["2", "3"], ["4"]]


def test_batch_texts_single_batch_when_input_smaller_than_batch_size() -> None:
    """A single batch should be yielded when all texts fit under `batch_size`."""
    texts = ["a", "b"]

    batches = list(batch_texts(texts, batch_size=10))

    assert batches == [["a", "b"]]


def test_batch_texts_empty_input_yields_no_batches() -> None:
    """No batches should be yielded for an empty input list."""
    assert list(batch_texts([], batch_size=4)) == []
