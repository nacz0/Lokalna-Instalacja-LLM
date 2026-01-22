# Architektura Systemu Lokalna-Instalacja-LLM

## 1. Przeglad Systemu

System **Lokalna-Instalacja-LLM** to lokalne srodowisko uruchomieniowe dla modeli jezykowych (LLM), zbudowane w oparciu o architekture kontenerowa Docker.

---

## 2. Schematy Graficzne

### 2.1 Architektura Kontenerow Docker

```mermaid
graph TB
    subgraph Docker
        OI[Open WebUI - Port 3000]
        PL[Pipelines - Port 9099]
        OL[Ollama - Port 11434]
        OI_INIT[Ollama-Init]
        AS[Auto-Setup]
    end

    subgraph Volumes
        V1[(open-webui)]
        V2[(pipelines)]
        V3[(ollama)]
        V4[(scripts)]
    end

    USER[Uzytkownik] --> OI
    OI --> PL
    OI --> OL
    PL --> OL
    OI_INIT --> OL
    AS --> OI

    OI --> V1
    PL --> V2
    OL --> V3
    AS --> V4
```

### 2.2 Przeplyw Danych

```mermaid
sequenceDiagram
    participant U as Uzytkownik
    participant OW as Open WebUI
    participant PL as Pipeline
    participant MS as ModelSelector
    participant MOD as Moderator
    participant OL as Ollama
    participant AT as ActivityTracker

    U->>OW: Wysyla zapytanie
    OW->>PL: Przekazuje do pipeline
    PL->>MS: Pobierz tryb
    MS-->>PL: Ustawienia modelu
    PL->>OL: Wyslij zapytanie
    OL-->>PL: Odpowiedz AI
    PL->>AT: Zapisz statystyki
    PL-->>OW: Zwroc odpowiedz
    OW-->>U: Wyswietl odpowiedz
```

### 2.3 Diagram Komponentow

```mermaid
graph LR
    subgraph Pipelines
        SM[Smart Mode]
        SAF[Safe Mode]
        PA[Pipeline Activity]
        SP[Spotify]
    end

    subgraph Utils
        MS[ModelSelector]
        MOD[Moderator]
        AT[ActivityTracker]
    end

    SM --> MS
    SM --> AT
    SAF --> MS
    SAF --> MOD
    SAF --> AT
    PA --> AT
```

---

## 3. Uslugi Docker

### 3.1 Ollama
- **Image**: ollama/ollama:latest
- **Port**: 11434
- **Modele**: gemma2:2b, llama3:latest, llama3.1:latest

### 3.2 Pipelines
- **Image**: ghcr.io/open-webui/pipelines:main
- **Port**: 9099

### 3.3 Open WebUI
- **Image**: open-webui-custom:latest
- **Port**: 3000

---

## 4. Tryby Operacyjne

| Tryb | RAM | Model | Max Tokens | Temperature |
|------|-----|-------|------------|-------------|
| Light | < 8 GB | gemma2:2b | 512 | 0.4 |
| Balanced | 8-16 GB | llama3:latest | 1024 | 0.5 |
| Advanced | > 16 GB | llama3.1:latest | 2048 | 0.6 |

---

## 5. Moduly Utils

### ModelSelector
Automatyczny dobor modelu na podstawie RAM.

### Moderator
Moderacja tresci dla Safe Mode - banned words, PII, jailbreak detection.

### ActivityTracker
Sledzenie aktywnosci pipelinow z persystencja do JSON.

---

## 6. Uruchomienie

```powershell
docker-compose up -d
```

- Open WebUI: http://localhost:3000
- Ollama API: http://localhost:11434
- Pipelines: http://localhost:9099
