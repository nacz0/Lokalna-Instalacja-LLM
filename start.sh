#!/bin/bash
# Skrypt startowy dla Lokalna-Instalacja-LLM
# Automatycznie wykrywa RAM hosta i przekazuje do kontenerów Docker

echo "?? Uruchamianie Lokalna-Instalacja-LLM..."

# Pobierz iloœæ RAM w GB
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    RAM_BYTES=$(sysctl -n hw.memsize)
else
    # Linux
    RAM_BYTES=$(grep MemTotal /proc/meminfo | awk '{print $2 * 1024}')
fi

RAM_GB=$(echo "scale=2; $RAM_BYTES / 1073741824" | bc)

echo "???  Wykryto RAM hosta: $RAM_GB GB"

# Eksportuj zmienn¹ œrodowiskow¹
export HOST_RAM_GB=$RAM_GB

# Okreœl tryb na podstawie RAM
if (( $(echo "$RAM_GB < 8" | bc -l) )); then
    MODE="light (phi3:mini)"
elif (( $(echo "$RAM_GB < 16" | bc -l) )); then
    MODE="balanced (llama3:latest)"
else
    MODE="advanced (llama3.1:latest)"
fi

echo "??  Wybrany tryb: $MODE"

# Uruchom docker-compose
echo ""
echo "?? Uruchamianie kontenerów Docker..."
docker-compose up -d

echo ""
echo "? Gotowe! OpenWebUI dostêpny pod: http://localhost:3000"
echo "   Pipelines API: http://localhost:9099"
echo "   Ollama API: http://localhost:11434"
