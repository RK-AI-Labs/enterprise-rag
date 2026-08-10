"""Chainlit front end for Enterprise RAG: chat, document upload, and citation display.

Wires the compiled LangGraph agent graph (see `app/graph/build.py`) to a Chainlit UI:

- Retrieval uses `DenseRetriever` only. Hybrid (dense + BM25) retrieval needs a reusable
  corpus-loading/indexing service that does not exist yet (see `app/retrieval/hybrid/`);
  building that is out of scope for this phase.
- Answer generation uses `LlmResponseGenerator` (`app/llm/response_generator.py`), backed by
  the configured LLM provider (Ollama by default).
- Tool routing remains `NotImplementedToolExecutor` (see `app/agents/tool.py`); tool-routed
  queries surface a friendly "not supported yet" message instead of crashing the session.
- "Streaming" is simulated by progressively rendering the completed answer text, since
  `LlmClient.generate()` (Phase 10) returns a single completed string rather than a token
  stream. Real token-level streaming is future work.

Run with: `uv run chainlit run chainlit/app.py -w`
"""

from pathlib import Path

import chainlit as cl
from app.agents.tool import NotImplementedToolExecutor
from app.config.settings import Settings, get_settings
from app.database.engine import get_session_factory
from app.embedding.factory import get_embedding_provider
from app.graph.build import build_graph
from app.ingestion.pipeline import ingest_document
from app.llm.factory import get_llm_client
from app.llm.response_generator import LlmResponseGenerator
from app.models.retrieval import RetrievedChunk
from app.repositories.document_repository import SqlAlchemyDocumentRepository
from app.repositories.vector_repository import QdrantVectorRepository
from app.retrieval.dense.retriever import DenseRetriever
from app.vectorstore.client import get_qdrant_client
from app.vectorstore.collections import ensure_collection

_ACCEPTED_EXTENSIONS = (".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx", ".pptx")
_STREAM_CHUNK_WORDS = 8


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialize per-session settings, retriever, and compiled graph."""
    settings = get_settings()
    embedding_provider = get_embedding_provider(settings)
    qdrant_client = get_qdrant_client()

    [probe_vector] = await embedding_provider.embed(["dimension probe"])
    await ensure_collection(
        qdrant_client, settings.qdrant_collection, vector_size=len(probe_vector)
    )

    vector_repository = QdrantVectorRepository(qdrant_client, settings.qdrant_collection)
    retriever = DenseRetriever(embedding_provider, vector_repository)
    response_generator = LlmResponseGenerator(get_llm_client(settings))
    graph = build_graph(
        retriever,
        NotImplementedToolExecutor(),
        response_generator,
        top_k=settings.retrieval_top_k,
    )

    cl.user_session.set("settings", settings)
    cl.user_session.set("embedding_provider", embedding_provider)
    cl.user_session.set("vector_repository", vector_repository)
    cl.user_session.set("graph", graph)

    await cl.Message(
        content=(
            "Enterprise RAG is ready. Ask a question, or upload a document "
            f"({', '.join(_ACCEPTED_EXTENSIONS)}) to add it to the knowledge base."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Handle a chat message: ingest any attached files, then answer via the agent graph."""
    uploads = [element for element in message.elements if isinstance(element, cl.File)]
    for upload in uploads:
        await _ingest_upload(upload)

    if not message.content.strip():
        return

    graph = cl.user_session.get("graph")
    try:
        result = await graph.ainvoke({"query": message.content})
    except NotImplementedError as exc:
        await cl.Message(content=f"That isn't supported yet: {exc}").send()
        return

    answer = result.get("answer") or "I don't have an answer for that."
    await _send_answer(answer, result.get("retrieved_chunks", []))


async def _ingest_upload(upload: cl.File) -> None:
    """Ingest an uploaded file into the document registry and vector store."""
    settings: Settings = cl.user_session.get("settings")
    embedding_provider = cl.user_session.get("embedding_provider")
    vector_repository = cl.user_session.get("vector_repository")

    if upload.path is None:
        await cl.Message(content=f"Could not read the uploaded file **{upload.name}**.").send()
        return

    data = Path(upload.path).read_bytes()
    session_factory = get_session_factory()
    async with session_factory() as session:
        document_repository = SqlAlchemyDocumentRepository(session)
        document = await ingest_document(
            data,
            upload.name,
            document_repository=document_repository,
            vector_repository=vector_repository,
            embedding_provider=embedding_provider,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        await session.commit()

    await cl.Message(
        content=f"Ingested **{upload.name}** ({document.status.value}, id `{document.id}`)."
    ).send()


async def _send_answer(answer: str, chunks: list[RetrievedChunk]) -> None:
    """Progressively render the answer and attach citation elements for the retrieved chunks."""
    msg = cl.Message(content="", elements=_citation_elements(chunks))
    words = answer.split(" ")
    for start in range(0, len(words), _STREAM_CHUNK_WORDS):
        batch = " ".join(words[start : start + _STREAM_CHUNK_WORDS])
        await msg.stream_token(batch + " ")
    await msg.send()


def _citation_elements(chunks: list[RetrievedChunk]) -> list[cl.Text]:
    """Render retrieved chunks as side-panel `cl.Text` citation elements."""
    return [
        cl.Text(name=f"[{chunk.chunk_id}] {chunk.source}", content=chunk.content, display="side")
        for chunk in chunks
    ]
