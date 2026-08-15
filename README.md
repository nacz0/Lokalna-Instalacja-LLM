# Lokalna-Instalacja-LLM
Projekt na przedmiot Inżynieria Oprogramowania

## Struktura projektu

```
/docs          → dokumentacja
/scripts       → instalacja środowiska
/tests         → testy UI / API
/data          → dane treningowe / testowe
```

### Katalogi

- **`/docs`** - Dokumentacja projektu (instrukcje, przewodniki, architektura)
- **`/scripts`** - Skrypty instalacyjne i konfiguracyjne środowiska
- **`/tests`** - Testy UI, API oraz testy integracyjne
- **`/data`** - Dane treningowe i testowe dla modelu

## Sposoby uruchomienia

Projekt można uruchomić przez:

- Docker Compose — najprostszy wariant developerski,
- Kubernetes — wariant z orkiestracją, health checkami i trwałymi wolumenami.

Szczegółowa instrukcja Kubernetes znajduje się w [docs/KUBERNETES.md](docs/KUBERNETES.md).

## Uruchomienie przez Docker Compose

Skopiuj `.env.example` jako `.env` i ustaw własne klucze. Nie commituj pliku `.env`.

### 1. Uruchom kontenery Docker
```powershell
docker-compose up -d
```

### 2. Pobierz modele AI
```powershell
# Modele dla automatycznego wyboru trybu (na podstawie RAM):
docker exec ollama ollama pull gemma2:2b        # Light mode (< 8 GB RAM) - 2.2 GB
docker exec ollama ollama pull llama3:latest    # Balanced mode (8-16 GB RAM) - 4.7 GB
docker exec ollama ollama pull llama3.1:latest  # Advanced mode (> 16 GB RAM) - 4.9 GB
```

### 3. Otwórz aplikację
- **Open WebUI**: http://localhost:3000
- **Ollama API**: http://localhost:11434
- **Pipelines**: http://localhost:9099

## Szybki start Kubernetes

Wymagane są Docker, aktywny lokalny klaster Kubernetes i `kubectl`.

```powershell
Copy-Item .env.k8s.example .env.k8s
# Uzupełnij wartości w .env.k8s

.\scripts\k8s-up.ps1
.\scripts\k8s-port-forward.ps1
```

Następnie otwórz http://localhost:3000.

```powershell
# Stan środowiska
.\scripts\k8s-status.ps1

# Zatrzymanie bez usuwania danych PVC
.\scripts\k8s-down.ps1
```

## Automatyczny wybór trybu

Projekt automatycznie dostosowuje model do ilości dostępnej pamięci RAM:

| Tryb | RAM | Model | Rozmiar | Max Tokens | Temperature | Top-P | Top-K |
|------|-----|-------|---------|------------|-------------|-------|-------|
| **Light** | < 8 GB | `gemma2:2b` | 1.6 GB | 512 | 0.4 | 0.9 | 40 |
| **Balanced** | 8-16 GB | `llama3:latest` | 4.7 GB | 1024 | 0.5 | 0.9 | 40 |
| **Advanced** | > 16 GB | `llama3.1:latest` | 4.9 GB | 2048 | 0.6 | 0.95 | 50 |

## Testowanie z terminala

```powershell
# Zainstaluj wymagane pakiety Python
pip install psutil requests

# Test automatycznego wyboru trybu
python tests\test_ollama_mode.py

# Własne zapytanie
python scripts\run_ollama_with_mode.py "Twoje pytanie tutaj"
```
