def get_settings_for_mode(mode):
"""
Zwraca ustawienia dla danego trybu.
    
Parametry:
- model: nazwa modelu Ollama
- max_tokens (num_predict): maksymalna liczba tokenów w odpowiedzi
- temperature: kreatywnoœæ (0.0 = deterministyczne, 1.0 = bardzo kreatywne)
- top_p: nucleus sampling - prawdopodobieñstwo kumulatywne (0.0-1.0)
- top_k: liczba tokenów do rozwa¿enia przy ka¿dym kroku
- repeat_penalty: kara za powtarzanie tokenów (1.0 = brak kary)
- num_ctx: rozmiar okna kontekstu (w tokenach)
"""
if mode == "light":
    # gemma2:2b - ma³y model, wymaga bardziej restrykcyjnych parametrów
    # Niska temperatura dla stabilnoœci, mniejszy kontekst dla wydajnoœci
    return {
        "model": "gemma2:2b",
        "max_tokens": 256,
        "temperature": 0.3,
        "top_p": 0.85,
        "top_k": 30,
        "repeat_penalty": 1.15,
        "num_ctx": 2048
    }

elif mode == "balanced":
    # llama3:latest - zbalansowany model dla wiêkszoœci zastosowañ
    # Umiarkowana temperatura, standardowe parametry
    return {
        "model": "llama3:latest",
        "max_tokens": 512,
        "temperature": 0.5,
        "top_p": 0.9,
        "top_k": 40,
        "repeat_penalty": 1.1,
        "num_ctx": 4096
    }

elif mode == "advanced":
    # llama3.1:latest - zaawansowany model z wiêkszymi mo¿liwoœciami
    # Wy¿sza temperatura dla kreatywnoœci, du¿y kontekst
    return {
        "model": "llama3.1:latest",
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.92,
        "top_k": 50,
        "repeat_penalty": 1.05,
        "num_ctx": 8192
    }

else:
    raise ValueError(f"Nieznany tryb: {mode}. Dostêpne: light, balanced, advanced")
