#!/bin/sh
# Starts the Ollama server and pulls the configured model before serving requests.
set -e

ollama serve &
server_pid=$!

until ollama list >/dev/null 2>&1; do
  sleep 1
done

ollama pull "${OLLAMA_MODEL:-qwen3}"

# Also pull the embedding model, since it's a separate model from the chat model above.
if [ -n "${EMBEDDING_MODEL:-nomic-embed-text}" ]; then
  ollama pull "${EMBEDDING_MODEL:-nomic-embed-text}"
fi

wait "$server_pid"
