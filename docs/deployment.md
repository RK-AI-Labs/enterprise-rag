# Deployment Guide

## Docker Compose stack

`docker-compose.yml` defines five services: `api` (FastAPI), `chainlit`, `postgres`, `qdrant`,
and `ollama`, plus an optional `redis` cache behind the `cache` profile.

```bash
cp .env.example .env
docker compose up -d --build          # api, chainlit, postgres, qdrant, ollama
docker compose --profile cache up -d --build   # + redis
```

Each service defines a `healthcheck`; `api` waits on `postgres`/`qdrant` reporting healthy
before starting. Tail logs or tear down:

```bash
docker compose logs -f
docker compose down
```

Per-service Dockerfiles live under `docker/{fastapi,chainlit,postgres,qdrant,ollama}/`. Only
`docker/fastapi/Dockerfile` is currently built and validated in CI (`docker-build` job in
`.github/workflows/ci.yml`); the others use upstream images or aren't yet part of a published
build artifact.

## Configuration reference

All configuration is environment-driven via Pydantic Settings (`src/app/config/settings.py`) —
see `.env.example` for the full list, grouped by concern:

| Group | Variables | Notes |
|---|---|---|
| App | `APP_NAME`, `ENVIRONMENT`, `DEBUG`, `LOG_LEVEL`, `API_HOST`, `API_PORT` | |
| Postgres | `POSTGRES_HOST/USER/PASSWORD/DB/PORT` | `HOST` defaults to `localhost`; the `api` container overrides it to the `postgres` Compose service name |
| Qdrant | `QDRANT_HOST/PORT/GRPC_PORT/COLLECTION` | same host-override pattern as Postgres |
| Ollama | `OLLAMA_HOST/PORT/MODEL` | entrypoint auto-pulls `OLLAMA_MODEL` + `EMBEDDING_MODEL` |
| Embedding | `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_BATCH_SIZE`, `OPENAI_*` | `ollama` or `openai` |
| LLM | `LLM_PROVIDER`, `LLM_TEMPERATURE`, `OPENAI_LLM_MODEL` | `ollama` or `openai` |
| Retrieval | `RETRIEVAL_TOP_K`, `RETRIEVAL_DENSE_WEIGHT`, `BM25_K1`, `BM25_B` | fusion weight: 0 = BM25-only, 1 = dense-only |
| Ingestion | `CHUNK_SIZE`, `CHUNK_OVERLAP` | |
| Chainlit | `CHAINLIT_PORT` | defaults to 8001; conflicts with a locally-run `chainlit run -w` — see [troubleshooting.md](troubleshooting.md) |

No secrets or connection strings are hardcoded anywhere in the codebase; production deployments
should inject `.env` values via their platform's secret manager rather than committing a `.env`
file (already covered by `.gitignore`).

## CI/CD pipeline

`.github/workflows/ci.yml` runs on every push (`main`, `develop`) and pull request
(`main`, `feature/enterprise-rag-v1`):

1. **`test` job** — `uv sync`, `ruff check`, `ruff format --check`, `mypy .`,
   `pytest --cov=app --cov-report=term-missing` (fails below 80% coverage).
2. **`docker-build` job** — builds `docker/fastapi/Dockerfile` (build-only, no push), catching
   Dockerfile breakage before merge.

Both jobs must pass before a PR can merge.

## Production considerations (not yet implemented — see README's "Deliberately out of scope")

* No authentication/authorization layer yet — do not expose the API/Chainlit UI publicly without
  adding one.
* No Redis caching wired in beyond the optional Compose service definition.
* No Kubernetes manifests or cloud (Azure/AWS) deployment configuration.
* No metrics/dashboarding (Prometheus/Grafana) — only structured logs with correlation IDs today.
