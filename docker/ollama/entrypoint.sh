#!/bin/sh
# Starts the Ollama server and pulls the configured model before serving requests.
set -e

ollama serve &
server_pid=$!

until ollama list >/dev/null 2>&1; do
  sleep 1
done

ollama pull "${OLLAMA_MODEL:-qwen3}"

wait "$server_pid"
