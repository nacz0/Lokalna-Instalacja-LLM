#!/usr/bin/env python3
"""
Skrypt do wywoływania Ollama z automatycznym wyborem trybu na podstawie RAM.
"""

import os
import sys
import time
import requests
import json

# Import z pipelines/utils
pipelines_utils_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pipelines', 'utils')
sys.path.insert(0, pipelines_utils_path)

from model_selector import ModelSelector



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
            "top_p": settings.get("top_p", 0.9),
            "top_k": settings.get("top_k", 40),
            "repeat_penalty": settings.get("repeat_penalty", 1.1),
            "num_ctx": settings.get("num_ctx", 2048)
        }
    }
    
    print(f"📤 Wysyłam zapytanie do Ollama (streaming)...")
    print(f"   Model: {settings['model']}")
    print(f"   Max tokens: {settings['max_tokens']}")
    print(f"   Temperature: {settings['temperature']}")
    print(f"   Top-P: {settings.get('top_p', 0.9)}")
    print(f"   Top-K: {settings.get('top_k', 40)}")
    print(f"   Repeat Penalty: {settings.get('repeat_penalty', 1.1)}\n")
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
    mode = ModelSelector.get_mode()
    
    # 2. Pobierz ustawienia dla trybu
    settings = ModelSelector.get_settings_for_mode(mode)
    
    # 3. Przykładowy prompt
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Napisz krótką historię o programiście, który nauczył się używać AI."
    
    print(f"\n📝 Prompt: {prompt}\n")
    
    # 4. Wywołaj Ollama
    response = call_ollama_streaming(prompt, settings)


if __name__ == "__main__":
    main()
