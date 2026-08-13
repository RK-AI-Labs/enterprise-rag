"""Citation extraction, confidence scoring, and grounding verification for generated answers.

Applied to the Response Agent's output (see `app/agents/response.py`) before it's surfaced to
the user: answers must cite chunk IDs that were actually retrieved, or they're replaced with a
fallback message rather than risking an unverifiable/hallucinated claim.
"""

import re
from typing import NamedTuple

from app.models.citation import Citation
from app.models.retrieval import RetrievedChunk

FALLBACK_ANSWER = "I don't have enough information to answer that."

_CITATION_PATTERN = re.compile(r"\[([^\[\]]+)\]")


class GroundedAnswer(NamedTuple):
    """The final answer text plus its supporting citations and confidence score."""

    answer: str
    citations: list[Citation]
    confidence: float


def extract_citations(answer: str, chunks: list[RetrievedChunk]) -> list[Citation]:
    """Return `Citation`s for chunk IDs referenced in `answer` that were actually retrieved.

    Citation markers are `[chunk_id]` substrings. IDs not present in `chunks` (i.e. not
    actually retrieved) are ignored, so citations can never point to invented sources.
    """
    chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}
    seen: set[str] = set()
    citations: list[Citation] = []
    for chunk_id in _CITATION_PATTERN.findall(answer):
        chunk = chunks_by_id.get(chunk_id)
        if chunk is None or chunk_id in seen:
            continue
        seen.add(chunk_id)
        citations.append(Citation(chunk_id=chunk.chunk_id, source=chunk.source, score=chunk.score))
    return citations


def compute_confidence(citations: list[Citation]) -> float:
    """Return the mean retrieval score of cited chunks, or 0.0 if nothing was cited."""
    if not citations:
        return 0.0
    return sum(citation.score for citation in citations) / len(citations)


def ground_answer(answer: str, chunks: list[RetrievedChunk]) -> GroundedAnswer:
    """Verify `answer` is grounded in `chunks`, falling back to a safe message if not.

    An answer is considered grounded if it already declares itself unanswerable (the exact
    `FALLBACK_ANSWER` text), or if it cites at least one chunk that was actually retrieved.
    Any other case — chunks were retrieved but the answer cites none of them, or no chunks
    were retrieved at all — is treated as an unverifiable claim and replaced with the
    fallback message.
    """
    if answer.strip() == FALLBACK_ANSWER:
        print("Answer is already the fallback answer; returning as grounded.")
        return GroundedAnswer(answer=FALLBACK_ANSWER, citations=[], confidence=0.0)
    if not chunks:
        print("No chunks were retrieved; returning fallback answer.")
        return GroundedAnswer(answer=FALLBACK_ANSWER, citations=[], confidence=0.0)
    citations = extract_citations(answer, chunks)
    if not citations:
        print("Answer cites no retrieved chunks; returning fallback answer.")
        return GroundedAnswer(answer=FALLBACK_ANSWER, citations=[], confidence=0.0)
    return GroundedAnswer(
        answer=answer, citations=citations, confidence=compute_confidence(citations)
    )
