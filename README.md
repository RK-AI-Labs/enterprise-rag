# AI Template Python

> A modern, production-ready Python template for AI, Machine Learning, Data Science, and backend engineering projects.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![uv](https://img.shields.io/badge/Package%20Manager-uv-blueviolet)
![Ruff](https://img.shields.io/badge/Linter-Ruff-orange)
![Pytest](https://img.shields.io/badge/Testing-pytest-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Overview

This repository provides a clean, reusable foundation for modern Python development.

It is designed to be the starting point for:

* AI & Generative AI applications
* Machine Learning projects
* Data Science projects
* FastAPI services
* LangGraph workflows
* RAG applications
* Automation scripts
* Research projects

Instead of repeatedly configuring development tools for every new project, this template provides a standardized engineering foundation.

---

# Features

* Python 3.13+
* uv package & dependency management
* Ruff linting and formatting
* pytest testing
* pre-commit hooks
* Docker support
* Dev Container support
* GitHub Actions CI
* VS Code configuration
* WSL2 optimized
* Modern `src` project layout

---

# Technology Stack

| Category        | Tool        |
| --------------- | ----------- |
| Language        | Python 3.13 |
| Package Manager | uv          |
| Formatter       | Ruff        |
| Linter          | Ruff        |
| Testing         | pytest      |
| Type Checking   | mypy        |
| Git Hooks       | pre-commit  |
| Containers      | Docker      |
| IDE             | VS Code     |
| Development     | WSL2 Ubuntu |

---

# Project Structure

```text
.
├── .devcontainer/
├── .github/
│   ├── workflows/
│   └── ISSUE_TEMPLATE/
├── .vscode/
├── assets/
├── configs/
├── data/
│   ├── external/
│   ├── processed/
│   └── raw/
├── docs/
├── examples/
├── models/
├── notebooks/
├── scripts/
├── src/
│   └── ai_template_python/
├── tests/
├── Dockerfile
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
* Docker (optional)
* VS Code (recommended)
* WSL2 Ubuntu (recommended for Windows)

---

# Getting Started

Clone the repository.

```bash
git clone <repository-url>
cd ai-template-python
```

Install dependencies.

```bash
uv sync
```

Activate the virtual environment.

```bash
source .venv/bin/activate
```

Run the application.

```bash
uv run python main.py
```

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

# Continuous Integration

GitHub Actions automatically:

* Install Python
* Install uv
* Install dependencies
* Run Ruff
* Run pytest

on every push and pull request.

---

# Roadmap

Future template repositories built from this foundation:

* FastAPI Template
* LangGraph Template
* Enterprise RAG Template
* Data Science Template
* Machine Learning Template
* Agentic AI Template

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
