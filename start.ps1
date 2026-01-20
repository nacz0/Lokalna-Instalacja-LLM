# Skrypt startowy dla Lokalna-Instalacja-LLM
# Automatycznie wykrywa RAM hosta i przekazuje do kontenerów Docker

Write-Host "?? Uruchamianie Lokalna-Instalacja-LLM..." -ForegroundColor Green

# Pobierz iloœæ RAM w GB
$ramBytes = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$ramGB = [math]::Round($ramBytes / 1GB, 2)

Write-Host "???  Wykryto RAM hosta: $ramGB GB" -ForegroundColor Cyan

# Ustaw zmienn¹ œrodowiskow¹
$env:HOST_RAM_GB = $ramGB

# Okreœl tryb na podstawie RAM
if ($ramGB -lt 8) {
    $mode = "light (phi3:mini)"
} elseif ($ramGB -lt 16) {
    $mode = "balanced (llama3:latest)"
} else {
    $mode = "advanced (llama3.1:latest)"
}

Write-Host "??  Wybrany tryb: $mode" -ForegroundColor Yellow

# Uruchom docker-compose
Write-Host "`n?? Uruchamianie kontenerów Docker..." -ForegroundColor Green
docker-compose up -d

Write-Host "`n? Gotowe! OpenWebUI dostêpny pod: http://localhost:3000" -ForegroundColor Green
Write-Host "   Pipelines API: http://localhost:9099" -ForegroundColor Gray
Write-Host "   Ollama API: http://localhost:11434" -ForegroundColor Gray
