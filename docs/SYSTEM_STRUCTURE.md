# Struktura Systemu - Schematy Graficzne

Ten dokument zawiera wizualną reprezentację architektury systemu **Lokalna-Instalacja-LLM**.

## 1. Architektura Wysokopoziomowa

Ogólny schemat połączeń między głównymi komponentami systemu.

```mermaid
graph TB
    subgraph Sieć_Lokalna [Sieć Lokalna / Docker Network]
        direction TB
        OW[Open WebUI]
        PL[Pipelines API]
        OL[Ollama Server]
        
        OW ---|Zpytania HTTP| PL
        PL ---|API Call| OL
        OW ---|Bezpośrednie| OL
    end

    U[Użytkownik] -->|Przeglądarka :3000| OW
```

## 2. Interakcja Kontenerów i Wolumenów

Szczegółowy widok usług Docker oraz ich powiązań z systemem plików (wolumenami).

```mermaid
graph LR
    subgraph Kontenery_Docker [Kontenery Docker]
        direction TB
        c_ow[open-webui]
        c_pl[pipelines]
        c_ol[ollama]
        c_as[auto-setup]
        c_in[ollama-init]
    end

    subgraph Wolumeny_Danych [Trwałe Dane]
        v_ow[(open-webui-data)]
        v_pl[(pipelines-data)]
        v_ol[(ollama-data)]
    end

    c_ow --> v_ow
    c_pl --> v_pl
    c_ol --> v_ol
    
    c_as -.->|Skrypty| c_ow
    c_in -.->|Setup| c_ol
```

## 3. Przepływ Zapytania (Data Flow)

Sekwencja zdarzeń od momentu wysłania pytania przez użytkownika do otrzymania odpowiedzi.

```mermaid
sequenceDiagram
    participant U as Użytkownik
    participant OW as Open WebUI
    participant PL as Pipeline (np. Safe Mode)
    participant MOD as Moderator
    participant Sel as ModelSelector
    participant OL as Ollama

    U->>OW: Wpisanie promptu
    OW->>PL: POST /chat/completions
    PL->>Sel: Pobierz optymalny model (na podst. RAM)
    Sel-->>PL: Zwróć ID modelu
    PL->>MOD: Sprawdź prompt (Moderacja)
    MOD-->>PL: OK / Ostrzeżenie
    PL->>OL: Przekaż do LLM
    OL-->>PL: Odpowiedź tekstowa
    PL->>MOD: Sprawdź odpowiedź (opcjonalnie)
    PL-->>OW: Zwróć przefiltrowaną odpowiedź
    OW-->>U: Wyświetlenie na UI
```

## 4. Diagram Komponentów Utils

Relacje między modułami pomocniczymi wewnątrz folderu `pipelines/utils`.

```mermaid
classDiagram
    class Pipeline {
        +process_request()
    }
    class ModelSelector {
        +get_model_by_ram()
    }
    class Moderator {
        +check_pii()
        +check_banned_words()
    }
    class ActivityTracker {
        +log_activity()
        +save_to_json()
    }

    Pipeline --> ModelSelector : dobiera model
    Pipeline --> Moderator : filtruje treść
    Pipeline --> ActivityTracker : zapisuje statystyki
```
