"""
title: Safe Mode
author: Ty
version: 2.1.3
"""

import sys
import os
import requests
import re
import psutil
from typing import List, Union, Generator, Iterator
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

class Moderator:
    def __init__(self):
        self.banned_words = {
            "violence": ["zabij", "morderstwo", "bomba", "terror", "broń", "pistolet", "ataki"],
            "hacking": ["hack", "exploit", "sql injection", "phishing", "malware", "wirus"],
            "hate": ["nienawiść", "rasizm", "dyskryminacja"],
            "sensitive": ["hasło", "klucz prywatny", "ssn", "pesel"]
        }
        self.pii_patterns = [r"\b\d{11}\b", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", r"\b(?:\+48\s?)?\d{9}\b"]
        self.jailbreak_patterns = [r"ignore all previous instructions", r"you are now in developer mode", r"dan mode"]

    def check_message(self, message: str) -> dict:
        msg_lower = message.lower()
        for category, words in self.banned_words.items():
            for word in words:
                if word in msg_lower: return {"safe": False, "reason": f"Wykryto słowo naruszające zasady ({category}): '{word}'"}
        for pattern in self.pii_patterns:
            if re.search(pattern, message): return {"safe": False, "reason": "Wykryto potencjalne dane osobowe."}
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, msg_lower): return {"safe": False, "reason": "Wykryto próbę manipulacji modelem."}
        return {"safe": True, "reason": None}

    def get_safe_mode_system_prompt(self) -> str:
        return "You are a safe, helpful, and friendly AI assistant. Strictly follow safety guidelines."

# --- PIPELINE ---

class Pipeline:
    class Valves(BaseModel):
        mode: str = Field(default="auto", description="Tryb: auto, light, balanced, advanced")
        ollama_url: str = Field(default="http://ollama:11434/api/chat", description="Adres API Ollama")

    def __init__(self):
        self.name = "Safe Mode"
        self.valves = self.Valves()
        self.moderator = Moderator()

    async def on_startup(self):
        print(f"on_startup: {self.name}")

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        res = self.moderator.check_message(user_message)
        if not res["safe"]:
            return f'<div class="safe-mode-block">🛡️ <b>BLOKADA:</b> {res["reason"]}</div>'

        mode = ModelSelector.get_mode(self.valves.mode)
        settings = ModelSelector.get_settings_for_mode(mode)

        system_prompt = self.moderator.get_safe_mode_system_prompt()
        if messages and messages[0].get("role") == "system":
            messages[0]["content"] = f"{system_prompt}\n\n{messages[0]['content']}"
        else:
            messages.insert(0, {"role": "system", "content": system_prompt})

        try:
            response = requests.post(self.valves.ollama_url, json={
                "model": settings["model"],
                "messages": messages,
                "stream": False,
                "options": {"num_predict": settings["max_tokens"], "temperature": settings["temperature"]}
            }, timeout=60)
            response.raise_for_status()
            ai_response = response.json().get("message", {}).get("content", "")
            
            out_res = self.moderator.check_message(ai_response)
            if not out_res["safe"]:
                return f'<div class="safe-mode-block">🛡️ <b>BLOKADA WYJŚCIA:</b> Naruszenie zasad.</div>'

            # --- 6. FORMATOWANIE "FRIENDLY" ---
            # Używamy tabeli Markdown dla bezpiecznego i ładnego renderowania
            formatted_response = (
                f"| 🛡️ **Safe Mode Active** |\n"
                f"| :--- |\n"
                f"| {ai_response} |\n\n"
                f"*Twoje bezpieczeństwo jest naszym priorytetem.*"
            )

            return formatted_response
        except Exception as e:
            return f"❌ Błąd: {str(e)}"
