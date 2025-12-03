# Jak wywołać Ollama z automatycznym wyborem trybu

## Przygotowanie

1. **Upewnij się, że Docker działa:**
```powershell
docker-compose up -d
```

2. **Zainstaluj wymagane pakiety Python:**
```powershell
pip install psutil requests
```

## Metoda 1: Bezpośrednie wywołanie przez API (skrypt Python)

### Użycie podstawowe:
```powershell
python scripts\run_ollama_with_mode.py
```

### Z własnym promptem:
```powershell
python scripts\run_ollama_with_mode.py "Napisz wiersz o sztucznej inteligencji"
```

### Jak to działa:
- Skrypt automatycznie wykrywa ilość RAM
- Wybiera odpowiedni tryb (light/balanced/advanced)
- Ustawia parametry modelu (max_tokens, temperature)
- Wysyła zapytanie do Ollama API
- Wyświetla odpowiedź ze streamingiem

## Metoda 2: Przez Open-WebUI (Pipeline)

### 1. Uruchom całe środowisko:
```powershell
docker-compose up -d
```

### 2. Otwórz Open-WebUI:
```
http://localhost:3000
```

### 3. Skonfiguruj Pipeline:
- Przejdź do Settings → Pipelines
- Znajdź "Llama 3 + Smart Mode"
- W ustawieniach (Valves) możesz:
  - Zostawić `mode: auto` (automatyczny wybór)
  - Lub ustawić ręcznie: `light`, `balanced`, `advanced`

### 4. Użyj w czacie:
- Pipeline automatycznie wykryje RAM i dobierze ustawienia
- Możesz normalnie pisać w czacie
- System będzie używał odpowiednich parametrów

## Tryby pracy

| Tryb | RAM | Model | Max Tokens | Temperature | Opis |
|------|-----|-------|------------|-------------|------|
| **light** | < 8 GB | llama3:latest | 256 | 0.3 | Szybkie, krótkie odpowiedzi |
| **balanced** | 8-16 GB | llama3:latest | 512 | 0.5 | Zbalansowane odpowiedzi |
| **advanced** | > 16 GB | llama3:latest | 1024 | 0.7 | Długie, kreatywne odpowiedzi |

## Przykłady użycia API

### Python (prosty przykład):
```python
import requests

# Wywołanie z konkretnymi ustawieniami
response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3:latest",
    "prompt": "Co to jest Python?",
    "stream": False,
    "options": {
        "num_predict": 512,
        "temperature": 0.5
    }
})

print(response.json()["response"])
```

### PowerShell (curl):
```powershell
$body = @{
    model = "llama3:latest"
    prompt = "Co to jest Python?"
    stream = $false
    options = @{
        num_predict = 512
        temperature = 0.5
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json"
```

## Testowanie

### Sprawdź czy Ollama działa:
```powershell
curl http://localhost:11434/api/tags
```

### Sprawdź wykrywanie RAM:
```powershell
python -c "import psutil; print(f'{psutil.virtual_memory().total / (1024**3):.2f} GB')"
```

### Przetestuj skrypt:
```powershell
python scripts\run_ollama_with_mode.py "Test"
```

## Troubleshooting

### Błąd: "Nie można połączyć się z Ollama"
```powershell
# Sprawdź czy kontenery działają
docker-compose ps

# Zrestartuj kontenery
docker-compose restart

# Zobacz logi
docker-compose logs ollama
```

### Błąd: "ModuleNotFoundError: No module named 'psutil'"
```powershell
pip install psutil requests
```

### Pipeline nie działa w Open-WebUI
```powershell
# Sprawdź logi pipelines
docker-compose logs pipelines

# Zrestartuj pipelines
docker-compose restart pipelines
```

## Dostosowywanie ustawień

### W skrypcie Python:
Edytuj `scripts\run_ollama_with_mode.py` i zmień wartości w funkcji `get_settings_for_mode()`.

### W Pipeline:
Edytuj `pipelines\smart_llama.py` i zmień wartości w funkcji `get_settings_for_mode()`.

### Zmiana progów RAM:
```python
def get_mode():
    ram_gb = psutil.virtual_memory().total / (1024**3)
    
    if ram_gb < 8:      # Zmień na swoją wartość
        mode = "light"
    elif ram_gb < 16:   # Zmień na swoją wartość
        mode = "balanced"
    else:
        mode = "advanced"
```
