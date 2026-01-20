# Skrypty Instalacyjne

Ten katalog zawiera skrypty do instalacji i konfiguracji środowiska.

## Zawartość

Tutaj znajdziesz:
- Skrypty instalacyjne dla różnych systemów operacyjnych
- Skrypty konfiguracyjne
- Narzędzia do automatyzacji setupu środowiska

## Automatyczny dobór modelu

Skrypty w tym katalogu obsługują automatyczny dobór modelu LLM na podstawie ilości pamięci RAM:

| RAM | Tryb | Model |
|-----|------|-------|
| < 8 GB | light | gemma2:2b |
| 8-16 GB | balanced | llama3:latest |
| > 16 GB | advanced | llama3.1:latest |

### Parametry modeli

Każdy tryb ma zoptymalizowane parametry dostosowane do charakterystyki modelu:

| Parametr | light (gemma2:2b) | balanced (llama3) | advanced (llama3.1) | Opis |
|----------|-------------------|-------------------|---------------------|------|
| **temperature** | 0.3 | 0.5 | 0.7 | Kreatywność odpowiedzi (0.0-1.0) |
| **top_p** | 0.85 | 0.9 | 0.92 | Nucleus sampling - kumulatywne prawdopodobieństwo |
| **top_k** | 30 | 40 | 50 | Liczba tokenów rozważanych przy każdym kroku |
| **repeat_penalty** | 1.15 | 1.1 | 1.05 | Kara za powtórzenia (1.0 = brak) |
| **num_ctx** | 2048 | 4096 | 8192 | Rozmiar okna kontekstu (tokeny) |
| **max_tokens** | 256 | 512 | 1024 | Maksymalna długość odpowiedzi |

**Uzasadnienie doboru parametrów:**

- **light (gemma2:2b)**: Niższa temperatura i mniejszy top_k dla stabilniejszych odpowiedzi na mniejszym modelu. Wyższy repeat_penalty zapobiega zapętlaniu. Mniejszy kontekst dla lepszej wydajności.

- **balanced (llama3)**: Zbalansowane parametry dla typowych zastosowań. Umiarkowana kreatywność z dobrą spójnością.

- **advanced (llama3.1)**: Wyższa temperatura pozwala na bardziej kreatywne odpowiedzi. Większy kontekst dla złożonych zadań. Niższy repeat_penalty - model lepiej radzi sobie z naturalnym językiem.

### run_ollama_with_mode.py

Skrypt do uruchamiania Ollama z automatycznym wyborem trybu:

```bash
python scripts/run_ollama_with_mode.py "Twoje pytanie"
```

### llama_mode_selector.py

Moduł pomocniczy z funkcją `get_settings_for_mode()` do pobierania ustawień dla danego trybu.
