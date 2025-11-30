"""
title: Llama 3 + Date (Wrapper)
author: Ty
version: 1.0
"""

import requests
import json
from datetime import datetime
from pydantic import BaseModel, Field

class Pipeline:
    class Valves(BaseModel):
        # Tu wpisz nazwę modelu, który masz w Ollamie (np. llama3:latest)
        target_model: str = Field(default="llama3:latest", description="Model docelowy w Ollama")

    def __init__(self):
        self.name = "Llama 3 + Date"
        self.valves = self.Valves()

    async def on_startup(self):
        print(f"on_startup: {self.name}")

    def pipe(self, user_message: str, model_id: str, messages: list[dict], body: dict) -> str:
        print(f"Wrapper otrzymał wiadomość. Przygotowuję datę...")

        # 1. Przygotuj aktualną datę
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_context = f"Current Date and Time: {current_date}. "

        # 2. Modyfikujemy wiadomości - dodajemy datę do System Promptu
        # (Ollama API oczekuje pełnej historii rozmowy)
        
        # Sprawdzamy czy pierwsza wiadomość to system, jak nie to dodajemy
        if messages and messages[0].get("role") == "system":
            messages[0]["content"] += f"\n{system_context}"
        else:
            messages.insert(0, {"role": "system", "content": f"System Context: {system_context}"})

        # 3. Wysyłamy zapytanie do Twojego kontenera Ollama
        # Używamy adresu http://ollama:11434, bo kontenery się widzą
        payload = {
            "model": self.valves.target_model,
            "messages": messages,
            "stream": False # Na razie bez streamingu dla uproszczenia
        }

        print(f"Wysyłam zapytanie do Ollamy ({self.valves.target_model})...")
        
        try:
            r = requests.post("http://ollama:11434/api/chat", json=payload)
            r.raise_for_status()
            response_json = r.json()
            
            # Wyciągamy odpowiedź
            ai_response = response_json.get("message", {}).get("content", "")
            return ai_response

        except Exception as e:
            return f"Error connecting to Ollama: {e}"