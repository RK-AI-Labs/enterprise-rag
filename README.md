# Enterprise RAG

> A production-grade Retrieval-Augmented Generation platform: hybrid retrieval, LangGraph
> agentic orchestration, grounded/cited answers, and a Chainlit chat UI — built on FastAPI,
> Postgres, Qdrant, and Ollama.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![uv](https://img.shields.io/badge/Package%20Manager-uv-blueviolet)
![Ruff](https://img.shields.io/badge/Linter-Ruff-orange)
![Pytest](https://img.shields.io/badge/Testing-pytest-green)
![Coverage](https://img.shields.io/badge/Coverage-96%25-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Overview

Enterprise RAG is an end-to-end Retrieval-Augmented Generation system, built as a portfolio
demonstration of production AI engineering practices rather than a notebook prototype:

* **Hybrid retrieval** — BM25 (sparse) + dense vector search (Qdrant), combined via weighted
  score fusion, behind a pluggable reranker interface.
* **Agentic orchestration** — a LangGraph `StateGraph` routes each query through query
  understanding, retrieval-or-tool routing, and response generation nodes.
* **Grounded, cited answers** — every retrieval-backed answer is verified against the chunks it
  cites; ungrounded claims are replaced with an explicit "I don't have enough information"
  fallback rather than surfaced as fact.
* **Multi-format ingestion** — PDF, DOCX, TXT, Markdown, CSV, XLSX, and PPTX documents are
  loaded, chunked with page/source metadata, embedded, and persisted (Postgres + Qdrant).
* **Chainlit UI** — a working chat front end with streaming, document upload, and citation
  side-panels, backed by the same graph used by the API.
* **Production discipline** — typed configuration (Pydantic Settings), structured logging with
  correlation IDs, layered/hexagonal architecture, 96%+ test coverage, and a CI pipeline
  (lint, type-check, test, Docker build) on every PR.

See [docs/diagrams/architecture.md](docs/diagrams/architecture.md) for the component architecture
and [docs/diagrams/sequence.md](docs/diagrams/sequence.md) for request-flow and agentic-graph
diagrams.

---

# Technology Stack

| Category            | Tool                        |
| ------------------- | --------------------------- |
| Language            | Python 3.13                 |
| Package Manager     | uv                          |
| API Framework       | FastAPI                     |
| Agent Orchestration | LangGraph                   |
| Chat UI             | Chainlit                    |
| LLM / Embeddings    | Ollama (Qwen3, nomic-embed) — OpenAI-compatible |
| Vector Store        | Qdrant                      |
| Metadata Store      | PostgreSQL (async SQLAlchemy) |
| Retrieval           | BM25 (in-memory) + dense (Qdrant), weighted fusion |
| Config              | Pydantic Settings           |
| Logging             | structlog (structured, correlation IDs) |
| Formatter / Linter  | Ruff                        |
| Type Checking       | mypy                        |
| Testing             | pytest, pytest-cov          |
| Git Hooks           | pre-commit                  |
| Containers          | Docker / Docker Compose     |
| CI                  | GitHub Actions              |

---

# Project Structure

```text
.
├── .github/workflows/ci.yml   # lint, type-check, test+coverage, Docker build
├── chainlit/                  # Chainlit chat UI (main.py)
├── docker/                    # per-service Dockerfiles (fastapi, chainlit, postgres, qdrant, ollama)
├── docs/
│   ├── diagrams/              # architecture & sequence diagrams (Mermaid)
│   ├── setup.md
│   ├── developer-guide.md
│   ├── deployment.md
│   └── troubleshooting.md
├── src/app/
│   ├── agents/ graph/         # LangGraph nodes + graph assembly
│   ├── api/                   # FastAPI routes, middleware, exception handling
│   ├── config/                # Pydantic Settings
│   ├── database/ vectorstore/ repositories/  # Postgres + Qdrant persistence layer
│   ├── embedding/ llm/ prompts/               # provider abstractions + externalized prompts
│   ├── ingestion/ parsing/    # document loaders + chunking
│   ├── logging/                # structlog setup + correlation ID middleware
│   ├── models/                # domain entities (Pydantic)
│   ├── retrieval/              # bm25/, dense/, hybrid/, reranker/
│   └── services/               # grounding / citation verification
├── tests/
│   ├── api/                   # FastAPI TestClient integration tests
│   └── unit/                  # unit tests (>96% coverage)
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── README.md
```

---

# Prerequisites

* Python 3.13+
* uv
* Git
* Docker (for Postgres/Qdrant/Ollama; optional if running those services elsewhere)
* VS Code (recommended)

---

# Getting Started

Clone the repository.

```bash
git clone <repository-url>
cd enterprise-rag
```

Install dependencies.

```bash
uv sync
```

Copy the environment template and fill in any secrets (e.g. `OPENAI_API_KEY` if using OpenAI).

```bash
cp .env.example .env
```

Bring up Postgres, Qdrant, and Ollama (see [Docker](#docker) below), then run the Chainlit UI
(see [Running the Chainlit UI](#running-the-chainlit-ui)) or the FastAPI app:

```bash
uv run python main.py
```

For a full walkthrough (first-run model pulls, environment variables, verifying the stack is
healthy), see [docs/setup.md](docs/setup.md).

---

# Development

Run tests.

```bash
uv run pytest
```

Run tests with a coverage report (gated at 80% minimum via `pyproject.toml`).

```bash
uv run pytest --cov=app --cov-report=term-missing
```

Lint the project.

```bash
uv run ruff check .
```

Format the project.

```bash
uv run ruff format .
```

Run pre-commit hooks.

```bash
uv run pre-commit run --all-files
```

---

# Make Commands

```bash
make setup
make lint
make format
make test
make run
make up
make down
make logs
```

---

# Docker

The stack is defined as multiple Docker Compose services: `api` (FastAPI), `postgres`,
`qdrant`, `ollama`, and an optional `redis` cache. Copy `.env.example` to `.env` first.

Bring up the core stack (api, postgres, qdrant, ollama).

```bash
docker compose up -d --build
```

Include the optional Redis cache.

```bash
docker compose --profile cache up -d --build
```

Tail logs or stop the stack.

```bash
docker compose logs -f
docker compose down
```

Per-service Dockerfiles and config live under `docker/{fastapi,postgres,qdrant,ollama}/`.

---

# Database & Vector Store

Postgres (document/metadata registry) and Qdrant (vector store) connections are fully
configurable via `Settings` (`src/app/config/settings.py`) — see `POSTGRES_*`/`QDRANT_*` in
`.env.example`. `POSTGRES_HOST`/`QDRANT_HOST` default to `localhost` for host-side development
against the ports published by `docker-compose.yml`; the `api` container overrides them to the
`postgres`/`qdrant` service names so it can resolve them on the Compose network.

## Initialize the document registry

After starting Postgres, create the `documents` table once before uploading documents:

```bash
docker compose exec postgres psql -U enterprise_rag -d enterprise_rag
```

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## View Postgres with Adminer

Connect the Postgres container to the `pg-net` Docker network, then run Adminer on port 8080:

```bash
docker network connect pg-net enterprise-rag-postgres
docker run --rm --net pg-net -p 8080:8080 adminer
```

Open `http://localhost:8080` and connect with server `enterprise-rag-postgres`, using the
`POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` values from `.env`.

## View Qdrant collections

Open the Qdrant dashboard at `http://localhost:6333/dashboard#/collections`.

## Code base

* `app/database/` — async SQLAlchemy engine, session factory, and ORM models.
* `app/vectorstore/` — async Qdrant client factory and collection management helpers.
* `app/repositories/` — repository interfaces plus Postgres/Qdrant implementations, used by
  `services/` in later phases without depending on infrastructure clients directly.

---

# Document Ingestion

`app/ingestion/` loads PDF, DOCX, TXT, Markdown, CSV, Excel, and PowerPoint files into raw text
via a `DocumentLoader` protocol, dispatched by file extension (`app/ingestion/registry.py`).
Loaders use PyMuPDF, python-docx, openpyxl, and python-pptx directly for a lean, purpose-built
dependency footprint. An `OcrProvider` interface is defined in `app/ingestion/ocr.py` for future
scanned-document support but is not implemented in the MVP.

`app/parsing/chunker.py` splits loaded documents into overlapping text chunks, tagged with
document ID, source filename, page number, and content type. Chunk size/overlap are configurable
via `CHUNK_SIZE`/`CHUNK_OVERLAP` in `.env.example`.

---

# Embedding Pipeline

`app/embedding/` defines an `EmbeddingProvider` protocol implemented by `OllamaEmbeddingProvider`
(default, targets a local/remote Ollama server's `/api/embed` endpoint) and
`OpenAiEmbeddingProvider` (targets any OpenAI-compatible `/embeddings` endpoint). Both batch
requests (`EMBEDDING_BATCH_SIZE`) and are fully async. `get_embedding_provider()`
(`app/embedding/factory.py`) selects and configures the provider from `Settings` based on
`EMBEDDING_PROVIDER` (`ollama` or `openai`) — see the Embedding section of `.env.example` for all
configurable settings.

---

# Hybrid Retrieval

`app/retrieval/` combines sparse and dense retrieval behind narrow protocol interfaces:

* `bm25/` — an in-memory Okapi BM25 retriever (`BM25Retriever`) over a corpus of `Chunk`s;
  `BM25_K1`/`BM25_B` tune term-frequency saturation and length normalization.
* `dense/` — `DenseRetriever` embeds the query via an `EmbeddingProvider` and searches
  `VectorRepository`, which now surfaces Qdrant's similarity `score` on `VectorPoint`.
* `hybrid/` — `fuse_scores()` combines BM25 and dense results via min-max normalized, weighted
  score fusion (`RETRIEVAL_DENSE_WEIGHT`, 0 = BM25-only, 1 = dense-only); `HybridRetriever`
  queries both sides and returns the top `RETRIEVAL_TOP_K` fused results.
* `reranker/` — a `Reranker` protocol with a `NotImplementedReranker` stub; a concrete
  cross-encoder/Cohere/BGE reranker is deferred to future work.

---

# Agentic Orchestration

`app/agents/` and `app/graph/` implement the query-answering flow as a LangGraph `StateGraph`
over a shared `GraphState`:

* `query_understanding_node` — normalizes the raw query (whitespace stripping); a placeholder for
  future LLM-based query rewriting.
* `router_node` — routes to retrieval or a tool using a deterministic `"tool:"`/`"calc:"` prefix
  heuristic; a placeholder for a future LLM-based classifier.
* `build_retriever_node()` — wraps any `Retriever` (e.g. `HybridRetriever`) to fetch candidate
  chunks for the (rewritten) query.
* `build_tool_node()` — wraps a `ToolExecutor`; `NotImplementedToolExecutor` is the MVP default
  since no concrete SQL/Web/KG tool is required yet.
* `build_response_node()` — wraps a `ResponseGenerator` to synthesize the final answer from
  retrieved chunks (or the tool result, wrapped as a chunk); `NotImplementedResponseGenerator` is
  the MVP default pending Phase 10's LLM integration.

`app/graph/build.py`'s `build_graph()` wires these into a compiled graph: query understanding →
router → (retriever | tool) → response, with the router branch selected via a conditional edge.

---

# LLM Integration

`app/llm/` defines an `LlmClient` protocol and `OpenAiCompatibleLlmClient`, a single
implementation that posts chat messages to any OpenAI-compatible `/chat/completions` endpoint —
Ollama's OpenAI-compatible API and OpenAI's own API share the same wire format, so only
`base_url`/`model`/`api_key` differ between backends. `get_llm_client()`
(`app/llm/factory.py`) selects and configures the client from `Settings` based on `LLM_PROVIDER`
(`ollama` or `openai`) — see the LLM section of `.env.example` for all configurable settings.

`app/prompts/` externalizes prompt text as `.txt` templates (`system`, `retriever`, `answer`,
`critique`, `evaluation`) under `app/prompts/templates/`, loaded via `load_prompt(name)`
(`app/prompts/loader.py`), so prompt copy never lives inline in application code.

---

# Chainlit UI

The top-level `chainlit/main.py` is a working chat UI wiring together retrieval, the LLM, and the
LangGraph agent graph:

* **Chat** — each session builds a `DenseRetriever` (embedding provider + `QdrantVectorRepository`),
  an `LlmResponseGenerator` (`app/llm/response_generator.py` — a concrete `ResponseGenerator`
  combining `LlmClient` and the externalized prompt templates), and `NotImplementedToolExecutor`
  into a compiled graph via `build_graph()`. Messages are answered by invoking the graph;
  tool-routed queries surface a friendly "not supported yet" message instead of crashing.
* **Document upload** — files attached to a chat message are ingested via `ingest_document()`
  (`app/ingestion/pipeline.py`): load → chunk → embed → persist (Postgres document registry +
  Qdrant vectors), reusing the Phase 6/7 ingestion and embedding pipelines.
* **Citations** — retrieved chunks are attached to each answer as `cl.Text` side-panel elements,
  labeled with their chunk ID and source.
* **Streaming** — answers are rendered progressively via `stream_token()`. This simulates
  streaming by chunking the completed answer text; `LlmClient.generate()` returns a single
  completed string rather than a true token stream, so real token-level streaming is future work.
* **Scope note** — retrieval is dense-only (no BM25/hybrid fusion), since combining it with a
  live Chainlit session would need a reusable corpus-loading/indexing service that doesn't exist
  yet; this is a deliberate simplification, not a regression.

## Running the Chainlit UI

With the `postgres`, `qdrant`, and `ollama` services up (`make up` or `docker compose up -d`):

```bash
uv run chainlit run chainlit/main.py -w
```

Open the printed local URL, ask a question, or attach a document to add it to the knowledge base.

---

# Citations & Grounded Answers

`app/services/grounding.py`'s `ground_answer()` verifies every retrieval-backed answer before
it's returned:

* **Citations** — `extract_citations()` parses `[chunk_id]` markers from the answer and keeps
  only ones matching a chunk that was actually retrieved, so a citation can never point to an
  invented source.
* **Confidence** — `compute_confidence()` averages the retrieval scores of the cited chunks.
* **Fallback** — if no chunks were retrieved, or the answer cites none of them, the answer is
  replaced with a fixed "I don't have enough information to answer that." message rather than
  surfacing an unverifiable claim.

The Response Agent node (`app/agents/response.py`) applies this to the retrieval path and
threads the result into two new `GraphState` fields, `citations` and `confidence`
(`app/models/citation.py`). The tool-executor path is exempt (tool output is deterministic, not
retrieved context) and reports full confidence with no citations.

---

# Documentation

* [docs/setup.md](docs/setup.md) — first-run setup, environment variables, verifying the stack.
* [docs/developer-guide.md](docs/developer-guide.md) — architecture conventions, adding a new
  loader/provider/retriever, running the test suite.
* [docs/deployment.md](docs/deployment.md) — Docker Compose deployment, configuration reference,
  CI/CD pipeline.
* [docs/troubleshooting.md](docs/troubleshooting.md) — real issues hit while building this
  project and how they were diagnosed/fixed.
* [docs/diagrams/architecture.md](docs/diagrams/architecture.md) — component architecture and
  layering rules.
* [docs/diagrams/sequence.md](docs/diagrams/sequence.md) — request-flow, retrieval pipeline, and
  agentic graph diagrams.

---

# Continuous Integration

`.github/workflows/ci.yml` runs on every push and pull request:

* Install Python + uv, `uv sync`
* `ruff check .` / `ruff format --check .`
* `mypy .`
* `pytest --cov=app --cov-report=term-missing` (fails below 80% coverage)
* Docker build of `docker/fastapi/Dockerfile` (build-only, catches Dockerfile breakage pre-merge)

---

# Engineering Highlights

| Dimension | What was built |
|---|---|
| Production architecture | Layered/hexagonal design (`api → agents/services → repositories → infra`), every infra dependency behind a `Protocol` interface |
| AI engineering depth | Hybrid (BM25 + dense) retrieval with weighted fusion, LangGraph agentic orchestration, grounded/cited answers with confidence scoring |
| Retrieval quality | Citation verification rejects invented sources; unverifiable answers fall back explicitly instead of hallucinating |
| Observability | structlog structured logging, correlation IDs propagated end-to-end via middleware |
| Testing | 134 tests, 96%+ coverage, gated at 80% in CI; fully hermetic (no live services required) |
| Maintainability | Typed configuration (no magic numbers/hardcoded paths), externalized prompts, narrow interfaces per provider |
| Developer experience | `uv`-based tooling, pre-commit hooks, Make targets, Docker Compose one-command stack |
| MLOps / CI/CD | GitHub Actions: lint, format-check, type-check, coverage-gated tests, Docker build — on every PR |
| Documentation | This README + [docs/](docs/) (setup, developer guide, deployment, troubleshooting, diagrams) |

---

# Project Phases

Built incrementally, one reviewed phase at a time, each gated on lint + type-check + tests:

| # | Phase | # | Phase |
|---|-------|---|-------|
| 1 | Repository structure & configuration | 9 | LangGraph agentic orchestration |
| 2 | Structured logging & observability | 10 | Ollama LLM integration |
| 3 | FastAPI application skeleton | 11 | Chainlit UI |
| 4 | Docker Compose infrastructure | 12 | Citations & grounded answers |
| 5 | Postgres + Qdrant integration | 13 | Comprehensive test hardening (96%+ coverage) |
| 6 | Document ingestion pipeline | 14 | GitHub Actions CI/CD |
| 7 | Embedding pipeline | 15 | Documentation & architecture diagrams |
| 8 | Hybrid retrieval (BM25 + dense) | | |

**Deliberately out of scope for this MVP** (see [docs/developer-guide.md](docs/developer-guide.md)
for how to extend towards them): authentication, Redis caching, SQL/web-search/knowledge-graph
tool agents, multi-tenancy, Kubernetes/cloud deployment, monitoring dashboards, and concrete
reranker providers beyond the `Reranker` interface.

---

# Contributing

Contributions, issues, and feature requests are welcome.

Please open an issue before submitting major changes.

---

# License

This project is licensed under the MIT License.

---

## Author

**Rajesh Kanna Vaidyanathan**

Senior AI Engineer | Data Scientist

GitHub: https://github.com/vrajeshtrichy
