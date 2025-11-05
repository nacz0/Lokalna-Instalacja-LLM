#!/bin/bash
echo "Test API Ollama..."
curl localhost:11434/api/generate -d '{"model": "llama3", "prompt": "Hello"}'
