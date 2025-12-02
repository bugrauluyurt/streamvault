#!/bin/bash
set -e

ollama serve &
pid=$!

echo "Waiting for Ollama server to start..."
sleep 5

until ollama list &>/dev/null; do
    echo "Ollama server not ready, waiting..."
    sleep 2
done

echo "Ollama server is ready"

IFS=',' read -ra MODELS <<< "$OLLAMA_MODELS"
for model in "${MODELS[@]}"; do
    model=$(echo "$model" | xargs)
    if [ -n "$model" ]; then
        echo "Pulling model: $model"
        ollama pull "$model"
    fi
done

echo "All models pulled successfully"

wait $pid
