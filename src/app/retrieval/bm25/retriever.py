"""Sparse lexical retrieval using the Okapi BM25 ranking function, in memory."""

import math
import re
from collections import Counter

from app.models.chunk import Chunk
from app.models.retrieval import RetrievedChunk

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    """Lowercase and split text into alphanumeric tokens."""
    return _TOKEN_PATTERN.findall(text.lower())


class BM25Retriever:
    """In-memory Okapi BM25 retriever over a corpus of `Chunk` documents.

    The corpus is held entirely in memory and must be (re)built via `index()` before searching.
    Chunks are identified by `"{document_id}:{chunk_index}"` for downstream fusion with other
    retrievers.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b
        self._chunks: list[Chunk] = []
        self._doc_freqs: list[Counter[str]] = []
        self._doc_lengths: list[int] = []
        self._avg_doc_length = 0.0
        self._term_doc_counts: Counter[str] = Counter()

    def index(self, chunks: list[Chunk]) -> None:
        """Build (or rebuild) the in-memory index from the given chunks."""
        self._chunks = list(chunks)
        doc_tokens = [_tokenize(chunk.content) for chunk in self._chunks]
        self._doc_freqs = [Counter(tokens) for tokens in doc_tokens]
        self._doc_lengths = [len(tokens) for tokens in doc_tokens]
        self._avg_doc_length = (
            sum(self._doc_lengths) / len(self._doc_lengths) if self._doc_lengths else 0.0
        )
        self._term_doc_counts = Counter()
        for freqs in self._doc_freqs:
            self._term_doc_counts.update(freqs.keys())

    def search(self, query: str, limit: int = 5) -> list[RetrievedChunk]:
        """Return the top-`limit` chunks ranked by BM25 relevance to `query`."""
        if not self._chunks:
            return []
        num_docs = len(self._chunks)
        avg_doc_length = self._avg_doc_length or 1.0
        scores = [0.0] * num_docs
        for term in set(_tokenize(query)):
            doc_freq = self._term_doc_counts.get(term, 0)
            if doc_freq == 0:
                continue
            idf = math.log((num_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
            for i, freqs in enumerate(self._doc_freqs):
                term_freq = freqs.get(term, 0)
                if term_freq == 0:
                    continue
                denom = term_freq + self._k1 * (
                    1 - self._b + self._b * self._doc_lengths[i] / avg_doc_length
                )
                scores[i] += idf * (term_freq * (self._k1 + 1)) / denom

        ranked_indices = sorted(range(num_docs), key=lambda i: scores[i], reverse=True)
        return [
            self._to_retrieved_chunk(i, scores[i]) for i in ranked_indices[:limit] if scores[i] > 0
        ]

    def _to_retrieved_chunk(self, index: int, score: float) -> RetrievedChunk:
        """Build a `RetrievedChunk` for the chunk at `index` with the given BM25 score."""
        chunk = self._chunks[index]
        return RetrievedChunk(
            chunk_id=f"{chunk.document_id}:{chunk.chunk_index}",
            content=chunk.content,
            score=score,
            source=chunk.source,
            metadata=chunk.metadata,
        )
