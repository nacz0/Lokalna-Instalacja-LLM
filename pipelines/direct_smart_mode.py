"""
title: Smart Mode
author: Ty
version: 2.3.2
"""

import sys
import os
import requests
import psutil
from datetime import datetime
from pydantic import BaseModel, Field

# --- UTILS INLINED ---

class ModelSelector:
    @staticmethod
    def get_mode(manual_mode: str = "auto"):
        if manual_mode != "auto":
            return manual_mode
        ram_gb = psutil.virtual_memory().total / (1024**3)
        if ram_gb < 8: return "light"
        elif ram_gb < 16: return "balanced"
        else: return "advanced"
    
    @staticmethod
    def get_settings_for_mode(mode: str, fallback_settings: dict = None):
        if mode == "light":
            return {"model": "phi3:mini", "max_tokens": 256, "temperature": 0.3}
        elif mode == "balanced":
            return {"model": "llama3:latest", "max_tokens": 512, "temperature": 0.5}
        elif mode == "advanced":
            return {"model": "llama3.1:latest", "max_tokens": 1024, "temperature": 0.7}
        return fallback_settings or {"model": "llama3", "max_tokens": 512, "temperature": 0.5}

# --- PIPELINE ---

class Pipeline:
    class Valves(BaseModel):
        mode: str = Field(default="auto", description="Tryb: auto, light, balanced, advanced")
        max_tokens: int = Field(default=512, description="Max tokens (nadpisywane przez mode)")
        temperature: float = Field(default=0.5, description="Temperature (nadpisywana przez mode)")
        ollama_url: str = Field(default="http://ollama:11434/api/chat", description="Adres API Ollama")

    def __init__(self):
        self.name = "Smart Mode"
        self.valves = self.Valves()

    async def on_startup(self):
        print(f"on_startup: {self.name}")

    def pipe(self, user_message: str, model_id: str, messages: list[dict], body: dict) -> str:
        mode = ModelSelector.get_mode(self.valves.mode)
        settings = ModelSelector.get_settings_for_mode(mode, fallback_settings={
            "model": "llama3:latest",
            "max_tokens": self.valves.max_tokens,
            "temperature": self.valves.temperature
        })
        
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_context = f"Current Date and Time: {current_date}. "

        if messages and messages[0].get("role") == "system":
            messages[0]["content"] += f"\n{system_context}"
        else:
            messages.insert(0, {"role": "system", "content": f"System Context: {system_context}"})

        try:
            r = requests.post(self.valves.ollama_url, json={
                "model": settings["model"],
                "messages": messages,
                "stream": False,
                "options": {"num_predict": settings["max_tokens"], "temperature": settings["temperature"]}
            }, timeout=60)
            r.raise_for_status()
            return r.json().get("message", {}).get("content", "")
        except Exception as e:
            return f"❌ Błąd: {str(e)}"
