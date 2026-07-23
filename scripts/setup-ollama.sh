#!/bin/bash
set -e

echo "Setting up Ollama..."

# Wait for Ollama to be ready
until curl -s http://ollama:11434/api/tags > /dev/null; do
    echo "Waiting for Ollama..."
    sleep 5
done

# Pull default model
echo "Pulling llama3.1:8b model..."
curl -X POST http://ollama:11434/api/pull -d '{"name": "llama3.1:8b"}'

echo "Ollama setup complete!"
