# Dokumentacja Wewnętrzna Projektu

Ten dokument opisuje szczegóły implementacyjne, strukturę plików oraz mechanizmy działania systemu **Lokalna-Instalacja-LLM**.

## 1. Struktura Projektu

Główne katalogi projektu i ich przeznaczenie:

- `/pipelines`: Zawiera definicje pipelinów Open WebUI (np. Smart Mode, Safe Mode).
    - `/utils`: Moduły pomocnicze (logika moderacji, wyboru modelu, śledzenia aktywności).
- `/scripts`: Skrypty administracyjne i automatyzacyjne (auto-setup, migracje).
- `/customization`: Pliki do budowy zmodyfikowanej wersji Open WebUI (Dockerfile, CSS).
- `/docs`: Dokumentacja projektu (w tym ten plik).
- `/data`: Katalogi na dane wolumenów (Docker).

## 2. Opis Komponentów (Pipelines/Utils)

### 2.1 ModelSelector (`model_selector.py`)
Odpowiada za dynamiczny dobór modelu LLM na podstawie dostępnej pamięci RAM.
- **Funkcja**: `get_model_by_ram(ram_gb)`
- **Tryby**:
    - `Light`: gemma2:2b (RAM < 8GB)
    - `Balanced`: llama3:latest (RAM 8-16GB)
    - `Advanced`: llama3.1:latest (RAM > 16GB)

### 2.2 Moderator (`moderator.py`)
Zapewnia bezpieczeństwo interakcji poprzez filtrowanie treści.
- **Funkcje**:
    - `detect_pii(text)`: Wykrywa dane osobowe (PESEL, e-mail, telefon).
    - `check_banned_words(text)`: Blokuje wulgarne lub niedozwolone słownictwo.
    - `detect_jailbreak(text)`: Próba wykrycia złośliwych promptów hackingowych.

### 2.3 ActivityTracker (`activity_tracker.py`)
Monitoruje wydajność i statystyki użycia.
- **Dane**: Zapisuje czas odpowiedzi, liczbę tokenów, użyty model i datę.
- **Persystencja**: Plik `pipelines/activity_data.json`.

## 3. Infrastruktura (Docker)

System składa się z 5 usług:
1.  **ollama**: Główny backend modeli.
2.  **ollama-init**: Pobiera wymagane modele przy pierwszym uruchomieniu.
3.  **pipelines**: Silnik niestandardowych operacji pośredniczących.
4.  **open-webui**: Interfejs użytkownika z nałożonymi stylami CSS.
5.  **auto-setup**: Automatycznie tworzy użytkowników i konfiguruje system po starcie.

## 4. Konfiguracja Portów i Linków

- **Open WebUI**: [http://localhost:3000](http://localhost:3000)
- **Pipelines API**: [http://localhost:9099](http://localhost:9099)
- **Ollama API**: [http://localhost:11434](http://localhost:11434)

Standardowy klucz API dla pipelinów: `0p3n-w3bu1`.

## 5. Procedura Rozwoju
Aby dodać nową funkcjonalność:
1. Dodaj skrypt w `/pipelines`.
2. Jeśli potrzebuje nowych bibliotek, dopisz je do `pipelines/requirements.txt`.
3. Zrestartuj kontener `pipelines`: `docker-compose restart pipelines`.
