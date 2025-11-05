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

### Instrukcja uruchomienia
docker-compose up -d
docker exec -it ollama ollama pull llama3

Link do Open WebUI: http://localhost:3000
