"""
title: Smart Mode
author: Ty
version: 2.3.2
"""

import sys
import os
import time
import requests
from datetime import datetime
from pydantic import BaseModel, Field

# Import z utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
from model_selector import ModelSelector
from activity_tracker import tracker

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
        self._use_generate_endpoint = False  # Fallback flag

    def _call_ollama(self, model: str, messages: list, settings: dict) -> str:
        """Call Ollama API with fallback to /api/generate if /api/chat returns 404."""
        base_url = self.valves.ollama_url.rsplit('/api/', 1)[0]
        
        # Budowanie opcji z wszystkich parametrów z model_selector
        options = {
            "num_predict": settings["max_tokens"],
            "temperature": settings["temperature"],
            "top_p": settings.get("top_p", 0.9),
            "top_k": settings.get("top_k", 40),
            "repeat_penalty": settings.get("repeat_penalty", 1.1),
            "num_ctx": settings.get("num_ctx", 4096)
        }
        
        # DEBUG: Wyświetl opcje w logach
        print(f"[{self.name}] Wysyłam do Ollama z opcjami: {options}", flush=True)
        
        # Try /api/chat first (unless we already know it doesn't work)
        if not self._use_generate_endpoint:
            try:
                chat_url = f"{base_url}/api/chat"
                response = requests.post(chat_url, json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": options
                }, timeout=60)
                
                if response.status_code == 404:
                    print(f"[{self.name}] /api/chat not available, falling back to /api/generate")
                    self._use_generate_endpoint = True
                else:
                    response.raise_for_status()
                    return response.json().get("message", {}).get("content", "")
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 404:
                    self._use_generate_endpoint = True
                else:
                    raise
        
        # Fallback to /api/generate
        generate_url = f"{base_url}/api/generate"
        # Convert messages to prompt format for /api/generate
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        prompt_parts.append("Assistant:")
        prompt = "\n\n".join(prompt_parts)
        
        response = requests.post(generate_url, json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options
        }, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")

    async def on_startup(self):
        print(f"on_startup: {self.name}")

    def pipe(self, user_message: str, model_id: str, messages: list[dict], body: dict) -> str:
        start_time = time.time()
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
            result = self._call_ollama(
                model=settings["model"],
                messages=messages,
                settings=settings
            )
            
            # Log successful request
            if tracker:
                tracker.log_request(self.name, mode, (time.time() - start_time) * 1000, True)
            
            return result
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                error_msg = f"Model nie został znaleziony na serwerze Ollama. Upewnij się, że model jest pobrany. (Błąd: {error_msg})"
            
            if tracker:
                tracker.log_request(self.name, mode, (time.time() - start_time) * 1000, False, str(e)[:50])
            return f"❌ Błąd: {error_msg}"
