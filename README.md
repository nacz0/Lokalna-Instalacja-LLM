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

## Instrukcja uruchomienia

### 1. Uruchom kontenery Docker
```powershell
docker-compose up -d
```

### 2. Pobierz modele AI
```powershell
# Modele dla automatycznego wyboru trybu (na podstawie RAM):
docker exec ollama ollama pull phi3:mini        # Light mode (< 8 GB RAM) - 2.2 GB
docker exec ollama ollama pull llama3:latest    # Balanced mode (8-16 GB RAM) - 4.7 GB
docker exec ollama ollama pull llama3.1:latest  # Advanced mode (> 16 GB RAM) - 4.9 GB
```

### 3. Otwórz aplikację
- **Open WebUI**: http://localhost:3000
- **Ollama API**: http://localhost:11434
- **Pipelines**: http://localhost:9099

## Automatyczny wybór trybu

Projekt automatycznie dostosowuje model do ilości dostępnej pamięci RAM:

| Tryb | RAM | Model | Rozmiar | Max Tokens | Temperature |
|------|-----|-------|---------|------------|-------------|
| **Light** | < 8 GB | `phi3:mini` | 2.2 GB | 256 | 0.3 |
| **Balanced** | 8-16 GB | `llama3:latest` | 4.7 GB | 512 | 0.5 |
| **Advanced** | > 16 GB | `llama3.1:latest` | 4.9 GB | 1024 | 0.7 |

## Testowanie z terminala

```powershell
# Zainstaluj wymagane pakiety Python
pip install psutil requests

# Test automatycznego wyboru trybu
python tests\test_ollama_mode.py

# Własne zapytanie
python scripts\run_ollama_with_mode.py "Twoje pytanie tutaj"
```
