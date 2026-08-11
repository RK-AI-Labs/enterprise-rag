# Setup Guide

## Prerequisites

* Python 3.13+
* [uv](https://docs.astral.sh/uv/) (package/dependency manager)
* Docker + Docker Compose (for Postgres, Qdrant, Ollama)
* Git

## 1. Clone and install

```bash
git clone <repository-url>
cd enterprise-rag
uv sync
```

## 2. Configure environment

```bash
cp .env.example .env
```

Defaults work out of the box for local development against the Docker Compose stack. Only
`OPENAI_API_KEY` is required if you set `LLM_PROVIDER=openai` or `EMBEDDING_PROVIDER=openai`
instead of the default Ollama-backed providers. See `.env.example` for every configurable
setting (Postgres, Qdrant, Ollama, chunking, retrieval fusion weights, etc.), each documented
inline with the module that reads it.

## 3. Bring up infrastructure

```bash
docker compose up -d postgres qdrant ollama
```

`ollama`'s entrypoint (`docker/ollama/entrypoint.sh`) automatically pulls both the chat model
(`OLLAMA_MODEL`, default `qwen3`) and the embedding model (`EMBEDDING_MODEL`, default
`nomic-embed-text`) on first start — this can take a few minutes depending on your connection.
Watch progress with:

```bash
docker compose logs -f ollama
```

Verify all three are healthy:

```bash
docker compose ps
```

## 4. Run the application

Either the Chainlit chat UI:

```bash
uv run chainlit run chainlit/main.py -w
```

or the FastAPI service directly:

```bash
uv run python main.py
# then: curl http://localhost:8000/health
```

> Both cannot bind the same port at once if you also run `chainlit` as a Docker Compose service
> (`docker compose up -d chainlit`) — see [troubleshooting.md](troubleshooting.md) if you hit a
> port-already-in-use error.

## 5. Verify the test suite

```bash
uv run pytest --cov=app --cov-report=term-missing
```

Should report 134+ tests passing at 95%+ coverage without needing any of the Docker services
running — the suite is fully hermetic (in-memory SQLite, fake providers/transports).

## Next steps

* [developer-guide.md](developer-guide.md) — architecture conventions, adding new providers.
* [deployment.md](deployment.md) — full Docker Compose reference, CI/CD pipeline.
* [troubleshooting.md](troubleshooting.md) — real issues hit building this project.
