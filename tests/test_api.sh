#!/bin/bash
echo "Test API Ollama..."
curl localhost:11434/api/generate -d '{"model": "llama3", "prompt": "Hello"}'

echo -e "\nTest API completed."

#Test 2
echo "Test API with different prompt..."
curl localhost:11434/api/generate -d '{"model": "llama3", "prompt": "What is the capital of France?"}'
echo -e "\nTest API completed."

