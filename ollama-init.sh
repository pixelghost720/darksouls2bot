#!/bin/bash

/bin/ollama serve &

echo "Waiting for Ollama to start..."
until ollama list > /dev/null 2>&1; do
    sleep 2
done

echo "Ollama started!"

echo "Checking for GGUF file..."
ls -lah /models/qwen/ || echo "Directory /models/qwen/ not found!"
echo ""

if [ -f "/models/qwen/qwen3-8b-q8_0.gguf" ]; then
    echo "Found GGUF file: /models/qwen/qwen3-8b-q8_0.gguf"
else
    echo "X GGUF file not found at /models/qwen/qwen3-8b-q8_0.gguf"
    echo "Available files in /models:"
    ls -lah /models/ || echo "Cannot access /models/"
    exit 1
fi

if ollama list | grep -q "qwen"; then
    echo "Model qwen already exists."
else
    echo "Creating model qwen from GGUF file..."

    cat > /tmp/Modelfile << 'EOF'
FROM /models/qwen/qwen3-8b-q8_0.gguf

TEMPLATE """<|im_start|>system
{{ .System }}<|im_end|>
<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""

PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER top_k 20
PARAMETER presence_penalty 1.5
EOF
    echo "Modelfile contents:"
    cat /tmp/Modelfile
    echo ""

    echo "Running: ollama create qwen -f /tmp/Modelfile"
    ollama create qwen -f /tmp/Modelfile

    echo "Completed model creation script."
fi

echo "Available models:"
ollama list

wait
