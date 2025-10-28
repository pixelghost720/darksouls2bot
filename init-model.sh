#!/bin/bash
set -e

echo "Waiting for Ollama service to be ready..."
until curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do
    sleep 2
    echo "Waiting for Ollama..."
done

echo "Ollama service is ready!"

echo "Checking app.py..."
if [ -f "/app/app.py" ]; then
    echo "app.py found at /app/app.py"
    echo "First few lines of app.py:"
    head -5 /app/app.py
else
    echo "ERROR: app.py not found at /app/app.py"
    ls -la /app/
    exit 1
fi

echo "Checking Python syntax..."
python -u -m py_compile /app/app.py
if [ $? -eq 0 ]; then
    echo "Python syntax check passed"
else
    echo "ERROR: Python syntax error in app.py"
    exit 1
fi

echo "Starting Discord bot..."
echo "Running: python -u /app/app.py"
exec python -u /app/app.py
