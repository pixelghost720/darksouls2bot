#!/bin/bash
set -e

echo "Waiting for Ollama service to be ready..."
until curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do
    sleep 2
    echo "Waiting for Ollama..."
done

echo "Ollama service is ready!"

echo "Starting Discord bot..."
exec python /app/app.py
