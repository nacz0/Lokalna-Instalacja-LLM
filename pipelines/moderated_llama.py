"""
title: Smart Safe Llama
author: Ty
version: 1.0.0
"""

from typing import List, Union, Generator, Iterator
import requests
import os

class Pipeline:
    def __init__(self):
        self.name = "Smart Safe Llama"
        
        # --- KONFIGURACJA ---
        # 1. Adres Ollamy. Wypróbuj te opcje w kolejności, jeśli nie działa:
        # Opcja A: Jeśli Ollama też jest w Dockerze (w tej samej sieci co WebUI)
        self.ollama_url = "http://ollama:11434/api/generate"
        
        # Opcja B: Jeśli Ollama działa na Windows/Mac "luzem", a WebUI w Dockerze
        # self.ollama_url = "http://host.docker.internal:11434/api/generate"
        
        # Opcja C: Linux "host mode" lub instalacja bez Dockera
        # self.ollama_url = "http://localhost:11434/api/generate"

        # 2. Model docelowy (musi być zainstalowany w Ollamie, np. llama3, mistral, gemma)
        self.target_model = "llama3" 
        
        # 3. Słowa zakazane
        self.banned_words = ["bomba", "hack", "exploit", "zabij"]

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        
        print(f"Smart Llama processing: {user_message}")

        # --- 1. MODERACJA WEJŚCIA ---
        msg_lower = user_message.lower()
        for word in self.banned_words:
            if word in msg_lower:
                return f"🛡️ BLOKADA: Twoje zapytanie zawiera niedozwolone słowo: '{word}'."

        # --- 2. PRZYGOTOWANIE ZAPYTANIA DO OLLAMY ---
        # Budujemy payload ręcznie, podobnie jak w przykładzie Spotify budowano 'params'
        
        payload = {
            "model": self.target_model,  # Musimy podać konkretny model, np. 'llama3'
            "prompt": user_message,      # Przekazujemy treść pytania
            "stream": False,             # Wyłączamy strumieniowanie dla weryfikacji
            "options": {
                "num_predict": 150,      # LIMIT: Maksymalna długość odpowiedzi
                "temperature": 0.3       # LIMIT: Kreatywność
            }
        }
        
        # --- 3. WYWOŁANIE OLLAMY ---
        try:
            # Wywołanie POST (w Spotify było GET, ale Ollama wymaga POST)
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            
            if response.status_code != 200:
                return f"❌ Błąd API Ollama ({response.status_code}): {response.text}"
            
            data = response.json()
            ai_response = data.get("response", "")

            if not ai_response:
                return "⚠️ Model zwrócił pustą odpowiedź."

            # --- 4. MODERACJA WYJŚCIA ---
            for word in self.banned_words:
                if word in ai_response.lower():
                    return "🛡️ BLOKADA WYJŚCIA: Model wygenerował treść naruszającą zasady."

            return ai_response

        except requests.exceptions.ConnectionError:
            return (f"❌ Nie można połączyć się z Ollamą pod adresem: {self.ollama_url}\n"
                    "Sprawdź w kodzie pliku 'pipelines/smart_llama.py' zmienną self.ollama_url.")
        except Exception as e:
            return f"❌ Wystąpił nieoczekiwany błąd: {str(e)}"