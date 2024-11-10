#!/bin/bash

#pull llama
if [ ! -d "/root/.ollama/models/llama-3.1-7b" ]; then
    echo "Pulling the llama-3.1-7b model..."
    ollama pull llama-3.1-7b
else
    echo "Model llama-3.1-7b already exists, skipping pull."
fi

# Start the Ollama server
exec ollama serve
