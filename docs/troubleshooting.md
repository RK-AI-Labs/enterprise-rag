# Troubleshooting

Real issues hit while building and running this project, and how they were diagnosed and fixed.

## Ollama `/api/embed` returns 404

**Symptom:** embedding requests fail with a 404 from Ollama, which looks like a connectivity or
routing problem.

**Root cause:** Ollama returns 404 when the requested model isn't pulled locally — not just on
bad connectivity. The original `docker/ollama/entrypoint.sh` only pulled the chat model
(`OLLAMA_MODEL`), never the embedding model (`EMBEDDING_MODEL`), so the first embedding call
always 404'd on a fresh container.

**Fix:** the entrypoint now pulls both models on startup. If you hit this on an existing
container, pull it manually and restart:

```bash
docker exec enterprise-rag-ollama ollama pull nomic-embed-text
docker exec enterprise-rag-ollama ollama list   # confirm it's present
```

## Chainlit fails to bind port 8001

**Symptom:** `uv run chainlit run chainlit/main.py -w` fails with an address-already-in-use error
on port 8001.

**Root cause:** the dockerized `chainlit` Compose service already publishes host port 8001
(`${CHAINLIT_PORT:-8001}:8000`) by default, colliding with a locally-run dev server on the same
port.

**Fix:** stop the containerized instance while developing locally:

```bash
docker compose stop chainlit
```

Restart it any time with `docker compose up -d chainlit`.

## Chainlit entrypoint named `app.py` collides with the `app` package

**Symptom:** `chainlit run` fails or behaves unexpectedly when the entrypoint script is named
`chainlit/app.py`.

**Root cause:** the Chainlit CLI loads the target script as a top-level module keyed by its file
stem in `sys.modules`. Naming it `app.py` collides with `sys.modules["app"]`, the actual `app`
package imported throughout the codebase.

**Fix:** the entrypoint is named `chainlit/main.py` instead. For the same reason, `chainlit/` is
excluded from the repo-wide `mypy` run (`[tool.mypy] exclude` in `pyproject.toml`) — mypy's own
module-name inference hits an equivalent collision for a directory-based `app` package with no
`__init__.py` conflict resolution. `chainlit/` still passes `ruff` and is verified by actually
running `chainlit run` (a static type-checker pass alone would not have caught the runtime
collision).

## LangGraph node factory + mypy

**Symptom:** mypy rejects a node-factory function passed to `graph.add_node()` even though it
returns an async callable matching LangGraph's expected node signature.

**Root cause:** annotating the factory's return type explicitly as
`Callable[[GraphState], Awaitable[GraphState]]` (or similar) makes mypy's structural check
against LangGraph's internal node-signature protocol fail.

**Fix:** don't annotate the factory's return type explicitly — let mypy infer it from the
`async def` closure body. See `app/agents/*.py`'s `build_*_node()` factories for the pattern.
