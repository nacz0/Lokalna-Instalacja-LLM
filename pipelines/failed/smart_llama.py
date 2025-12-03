"""
title: Llama 3 + Smart Mode Selector
author: Ty
version: 2.0
"""

import requests
import json
import psutil
from datetime import datetime
from pydantic import BaseModel, Field

class Pipeline:
    class Valves(BaseModel):
        # Auto-wykrywanie trybu lub ręczne ustawienie
        mode: str = Field(default="auto", description="Tryb: auto, light, balanced, advanced")
        target_model: str = Field(default="llama3:latest", description="Model docelowy w Ollama (nadpisywany przez mode)")
        max_tokens: int = Field(default=512, description="Max tokens (nadpisywane przez mode)")
        temperature: float = Field(default=0.5, description="Temperature (nadpisywana przez mode)")

    def __init__(self):
        self.name = "Llama 3 + Smart Mode"
        self.valves = self.Valves()

    async def on_startup(self):
        print(f"on_startup: {self.name}")
    
    def get_mode(self):
        """Wykrywa tryb na podstawie dostępnej pamięci RAM."""
        if self.valves.mode != "auto":
            return self.valves.mode
        
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        if ram_gb < 8:
            return "light"
        elif ram_gb < 16:
            return "balanced"
        else:
            return "advanced"
    
    def get_settings_for_mode(self, mode):
        """Zwraca ustawienia dla danego trybu."""
        if mode == "light":
            return {
                "model": "llama3:latest",
                "max_tokens": 256,
                "temperature": 0.3
            }
        elif mode == "balanced":
            return {
                "model": "llama3:latest",
                "max_tokens": 512,
                "temperature": 0.5
            }
        elif mode == "advanced":
            return {
                "model": "llama3:latest",
                "max_tokens": 1024,
                "temperature": 0.7
            }
        else:
            # Fallback - użyj ustawień z valves
            return {
                "model": self.valves.target_model,
                "max_tokens": self.valves.max_tokens,
                "temperature": self.valves.temperature
            }

    def pipe(self, user_message: str, model_id: str, messages: list[dict], body: dict) -> str:
        # 1. Wykryj tryb i pobierz ustawienia
        mode = self.get_mode()
        settings = self.get_settings_for_mode(mode)
        
        ram_gb = psutil.virtual_memory().total / (1024**3)
        print(f"🖥️  RAM: {ram_gb:.2f} GB → Tryb: {mode}")
        print(f"⚙️  Ustawienia: model={settings['model']}, max_tokens={settings['max_tokens']}, temp={settings['temperature']}")

        # 2. Przygotuj aktualną datę
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_context = f"Current Date and Time: {current_date}. "

        # 3. Modyfikujemy wiadomości - dodajemy datę do System Promptu
        if messages and messages[0].get("role") == "system":
            messages[0]["content"] += f"\n{system_context}"
        else:
            messages.insert(0, {"role": "system", "content": f"System Context: {system_context}"})

        # 4. Wysyłamy zapytanie do Ollama z ustawieniami z trybu
        payload = {
            "model": settings["model"],
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": settings["max_tokens"],
                "temperature": settings["temperature"]
            }
        }

        print(f"📤 Wysyłam zapytanie do Ollamy...")
        
        try:
            r = requests.post("http://ollama:11434/api/chat", json=payload)
            r.raise_for_status()
            response_json = r.json()
            
            # Wyciągamy odpowiedź
            ai_response = response_json.get("message", {}).get("content", "")
            return ai_response

        except Exception as e:
            return f"Error connecting to Ollama: {e}"