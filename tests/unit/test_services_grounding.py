"""Unit tests for `app.services.grounding`."""

from app.models.citation import Citation
from app.models.retrieval import RetrievedChunk
from app.services.grounding import FALLBACK_ANSWER, extract_citations, ground_answer

_CHUNK_A = RetrievedChunk(chunk_id="a", content="chunk a", score=0.9, source="doc-a")
_CHUNK_B = RetrievedChunk(chunk_id="b", content="chunk b", score=0.5, source="doc-b")


def test_extract_citations_returns_cited_chunks_only() -> None:
    """Only chunk IDs both cited in the answer and present in `chunks` should be returned."""
    citations = extract_citations("see [a] and [missing]", [_CHUNK_A, _CHUNK_B])

    assert citations == [Citation(chunk_id="a", source="doc-a", score=0.9)]


def test_extract_citations_deduplicates_repeated_ids() -> None:
    """Citing the same chunk ID twice should only produce one `Citation`."""
    citations = extract_citations("[a] again [a]", [_CHUNK_A])

    assert citations == [Citation(chunk_id="a", source="doc-a", score=0.9)]


def test_ground_answer_keeps_answer_when_citations_present() -> None:
    """A properly cited answer should pass through unchanged, with computed confidence."""
    grounded = ground_answer("the answer [a]", [_CHUNK_A, _CHUNK_B])

    assert grounded.answer == "the answer [a]"
    assert grounded.citations == [Citation(chunk_id="a", source="doc-a", score=0.9)]
    assert grounded.confidence == 0.9


def test_ground_answer_averages_confidence_across_multiple_citations() -> None:
    """Confidence should be the mean retrieval score across all cited chunks."""
    grounded = ground_answer("the answer [a] and [b]", [_CHUNK_A, _CHUNK_B])

    assert grounded.confidence == 0.7


def test_ground_answer_falls_back_when_no_chunks_retrieved() -> None:
    """With no retrieved chunks, any answer should be replaced with the fallback message."""
    grounded = ground_answer("a confident-sounding answer", [])

    assert grounded.answer == FALLBACK_ANSWER
    assert grounded.citations == []
    assert grounded.confidence == 0.0


def test_ground_answer_falls_back_when_answer_cites_nothing() -> None:
    """Chunks were retrieved but the answer cites none of them: treat it as ungrounded."""
    grounded = ground_answer("an uncited answer", [_CHUNK_A])

    assert grounded.answer == FALLBACK_ANSWER
    assert grounded.citations == []
    assert grounded.confidence == 0.0


def test_ground_answer_passes_through_explicit_fallback_unchanged() -> None:
    """When the model already declares it can't answer, that response is itself grounded."""
    grounded = ground_answer(FALLBACK_ANSWER, [_CHUNK_A])

    assert grounded.answer == FALLBACK_ANSWER
    assert grounded.citations == []
    assert grounded.confidence == 0.0
