# Developer Guide

## Architecture conventions

See [diagrams/architecture.md](diagrams/architecture.md) for the full component diagram and
layering rules. In short: `api/` → `agents/`/`graph/` → `retrieval/`/`services/` →
`repositories/` → `database/`/`vectorstore/`. Every infrastructure dependency (Qdrant, Postgres,
Ollama) sits behind a `Protocol` interface, with a concrete implementation and, where a phase
hasn't reached it yet, a `NotImplementedXxx` stub — never a half-wired dependency.

## Adding a new document loader

1. Implement the `DocumentLoader` protocol (`app/ingestion/base.py`) for the new format.
2. Register the extension → loader mapping in `app/ingestion/registry.py`.
3. Add a fixture file and a unit test in `tests/unit/test_ingestion_loaders.py`.

## Adding a new embedding or LLM provider

1. Implement `EmbeddingProvider` (`app/embedding/base.py`) or `LlmClient` (`app/llm/base.py`).
2. Wire it into `get_embedding_provider()` / `get_llm_client()` (the respective `factory.py`),
   selected by a new `Settings` value (never hardcode which provider is active).
3. Follow the existing pattern: accept an optional injected `httpx.AsyncClient` in `__init__` so
   tests can substitute a fake/mock transport instead of hitting the network.

## Adding a new retriever or reranker

Implement the narrow `Protocol` in `app/retrieval/<kind>/` and wire it in via
`build_retriever_node()` (`app/agents/retriever.py`) or `HybridRetriever`. A concrete reranker
(cross-encoder/Cohere/BGE) is the main documented gap left behind the `Reranker` interface —
implement `app/retrieval/reranker/base.py`'s protocol and swap `NotImplementedReranker` for it.

## Testing conventions

* Tests are fully hermetic — no network calls, no external services required.
* Async I/O boundaries (Postgres, Qdrant, Ollama/OpenAI HTTP) are faked via an in-memory SQLite
  engine (`sqlalchemy+aiosqlite`) or an injected `httpx.AsyncClient`/`httpx.MockTransport`.
* LangGraph nodes are tested against `GraphState` fakes, not a live graph, unless testing
  `graph/build.py` itself end-to-end with fake node dependencies.
* Run the full suite with coverage:

  ```bash
  uv run pytest --cov=app --cov-report=term-missing
  ```

  Coverage is gated at 80% (`[tool.coverage.report] fail_under` in `pyproject.toml`); current
  coverage is 96%+. Remaining gaps are documented in `ARCHITECTURE.md`'s Phase 13 status entry:
  `Protocol`/abstract stub method bodies (no logic to test directly) and the "no injected HTTP
  client" default-construction branch in the embedding/LLM clients.

## Linting & type-checking

```bash
uv run ruff check .        # lint
uv run ruff format .       # format
uv run mypy .               # type-check
```

`chainlit/` is excluded from the mypy run (`[tool.mypy] exclude` in `pyproject.toml`): the
Chainlit CLI loads its entrypoint script into `sys.modules` keyed by file stem, which collides
with mypy's own module-name inference for a directory-based `app` package. It still passes
`ruff` and is smoke-tested by actually running `chainlit run`.

## LangGraph mypy gotcha

Node-factory closures passed to `graph.add_node()` must **not** carry an explicit
`Callable[..., Awaitable[...]]` return-type annotation on the factory function itself — mypy's
structural matching against LangGraph's node signature fails otherwise. Let mypy infer the
closure's type from the `async def` body instead.
