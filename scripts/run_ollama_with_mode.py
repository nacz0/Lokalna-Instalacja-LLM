#!/usr/bin/env python3
"""
Skrypt do wywoływania Ollama z automatycznym wyborem trybu na podstawie RAM.
"""

import psutil
import requests
import json
import sys


def get_mode():
    """Wybiera tryb na podstawie dostępnej pamięci RAM."""
    ram_gb = psutil.virtual_memory().total / (1024**3)
    
    if ram_gb < 8:
        mode = "light"
    elif ram_gb < 16:
        mode = "balanced"
    else:
        mode = "advanced"
    
    print(f"🖥️  Wykryto {ram_gb:.2f} GB RAM → Tryb: {mode}")
    return mode


def get_settings_for_mode(mode):
"""
Zwraca ustawienia dla danego trybu.
    
Parametry:
- model: nazwa modelu Ollama
- max_tokens (num_predict): maksymalna liczba tokenów w odpowiedzi
- temperature: kreatywność (0.0 = deterministyczne, 1.0 = bardzo kreatywne)
- top_p: nucleus sampling - prawdopodobieństwo kumulatywne (0.0-1.0)
- top_k: liczba tokenów do rozważenia przy każdym kroku
- repeat_penalty: kara za powtarzanie tokenów (1.0 = brak kary)
- num_ctx: rozmiar okna kontekstu (w tokenach)
"""
if mode == "light":
    # gemma2:2b - mały model, wymaga bardziej restrykcyjnych parametrów
    # Niska temperatura dla stabilności, mniejszy kontekst dla wydajności
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
    # llama3:latest - zbalansowany model dla większości zastosowań
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
    # llama3.1:latest - zaawansowany model z większymi możliwościami
    # Wyższa temperatura dla kreatywności, duży kontekst
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
    raise ValueError(f"Nieznany tryb: {mode}. Dostępne: light, balanced, advanced")


def call_ollama(prompt, settings, ollama_url="http://localhost:11434"):
    """
    Wywołuje API Ollama z podanymi ustawieniami.
    
    Args:
        prompt: Tekst promptu
        settings: Słownik z ustawieniami (model, max_tokens, temperature)
        ollama_url: URL do API Ollama
    """
    url = f"{ollama_url}/api/generate"
    
    payload = {
        "model": settings["model"],
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": settings["max_tokens"],
            "temperature": settings["temperature"],
            "top_p": settings["top_p"],
            "top_k": settings["top_k"],
            "repeat_penalty": settings["repeat_penalty"],
            "num_ctx": settings["num_ctx"]
        }
    }
    
    print(f"📤 Wysyłam zapytanie do Ollama...")
    print(f"   Model: {settings['model']}")
    print(f"   Max tokens: {settings['max_tokens']}")
    print(f"   Temperature: {settings['temperature']}")
    print(f"   Top-p: {settings['top_p']}, Top-k: {settings['top_k']}")
    print(f"   Repeat penalty: {settings['repeat_penalty']}")
    print(f"   Context size: {settings['num_ctx']} tokens\n")
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
    except requests.exceptions.ConnectionError:
        print("❌ Błąd: Nie można połączyć się z Ollama.")
        print("   Upewnij się, że Ollama działa: docker-compose up -d")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ Błąd: Timeout - zapytanie trwało zbyt długo.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Błąd: {e}")
        sys.exit(1)


def call_ollama_streaming(prompt, settings, ollama_url="http://localhost:11434"):
    """
    Wywołuje API Ollama ze streamingiem odpowiedzi.
    """
    url = f"{ollama_url}/api/generate"
    
    payload = {
        "model": settings["model"],
        "prompt": prompt,
        "stream": True,
        "options": {
            "num_predict": settings["max_tokens"],
            "temperature": settings["temperature"],
            "top_p": settings["top_p"],
            "top_k": settings["top_k"],
            "repeat_penalty": settings["repeat_penalty"],
            "num_ctx": settings["num_ctx"]
        }
    }
    
    print(f"📤 Wysyłam zapytanie do Ollama (streaming)...")
    print(f"   Model: {settings['model']}")
    print(f"   Max tokens: {settings['max_tokens']}")
    print(f"   Temperature: {settings['temperature']}")
    print(f"   Top-p: {settings['top_p']}, Top-k: {settings['top_k']}")
    print(f"   Repeat penalty: {settings['repeat_penalty']}")
    print(f"   Context size: {settings['num_ctx']} tokens\n")
    print("💬 Odpowiedź:\n")
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    text = chunk["response"]
                    print(text, end="", flush=True)
                    full_response += text
        
        print("\n")
        return full_response
    
    except requests.exceptions.ConnectionError:
        print("❌ Błąd: Nie można połączyć się z Ollama.")
        print("   Upewnij się, że Ollama działa: docker-compose up -d")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Błąd: {e}")
        sys.exit(1)


def main():
    # 1. Wykryj tryb na podstawie RAM
    mode = get_mode()
    
    # 2. Pobierz ustawienia dla trybu
    settings = get_settings_for_mode(mode)
    
    # 3. Przykładowy prompt
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Napisz krótką historię o programiście, który nauczył się używać AI."
    
    print(f"\n📝 Prompt: {prompt}\n")
    
    # 4. Wywołaj Ollama (wybierz streaming lub nie)
    # response = call_ollama(prompt, settings)
    response = call_ollama_streaming(prompt, settings)
    
    # print("\n💬 Odpowiedź:")
    # print(response)


if __name__ == "__main__":
    main()
