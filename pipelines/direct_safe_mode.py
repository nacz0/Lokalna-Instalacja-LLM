"""
title: Safe Mode
author: Ty
version: 2.1.3
"""

import sys
import os
import time
import requests
from datetime import datetime
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel, Field

# Import z utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
from model_selector import ModelSelector
from activity_tracker import tracker
from moderator import Moderator

# --- PIPELINE ---

class Pipeline:
    class Valves(BaseModel):
        mode: str = Field(default="auto", description="Tryb: auto, light, balanced, advanced")
        ollama_url: str = Field(
            default=f"{os.getenv('OLLAMA_BASE_URL', 'http://ollama:11434').rstrip('/')}/api/chat",
            description="Adres API Ollama",
        )

    def __init__(self):
        self.name = "Safe Mode"
        self.valves = self.Valves()
        self.moderator = Moderator()
        self._use_generate_endpoint = False  # Fallback flag

    def _call_ollama(self, model: str, messages: list, max_tokens: int, temperature: float) -> str:
        """Call Ollama API with fallback to /api/generate if /api/chat returns 404."""
        base_url = self.valves.ollama_url.rsplit('/api/', 1)[0]
        
        # Try /api/chat first (unless we already know it doesn't work)
        if not self._use_generate_endpoint:
            try:
                chat_url = f"{base_url}/api/chat"
                response = requests.post(chat_url, json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {"num_predict": max_tokens, "temperature": temperature}
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
            "options": {"num_predict": max_tokens, "temperature": temperature}
        }, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")

    async def on_startup(self):
        print(f"on_startup: {self.name}")

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        start_time = time.time()
        mode = ModelSelector.get_mode(self.valves.mode)
        
        res = self.moderator.check_message(user_message)
        if not res["safe"]:
            if tracker:
                tracker.log_request(self.name, mode, (time.time() - start_time) * 1000, False, "blocked_input")
            return f'<div class="safe-mode-block">🛡️ <b>BLOKADA:</b> {res["reason"]}</div>'

        settings = ModelSelector.get_settings_for_mode(mode)

        system_prompt = self.moderator.get_safe_mode_system_prompt()
        if messages and messages[0].get("role") == "system":
            messages[0]["content"] = f"{system_prompt}\n\n{messages[0]['content']}"
        else:
            messages.insert(0, {"role": "system", "content": system_prompt})

        try:
            ai_response = self._call_ollama(
                model=settings["model"],
                messages=messages,
                max_tokens=settings["max_tokens"],
                temperature=settings["temperature"]
            )
            
            out_res = self.moderator.check_message(ai_response)
            if not out_res["safe"]:
                if tracker:
                    tracker.log_request(self.name, mode, (time.time() - start_time) * 1000, False, "blocked_output")
                return f'<div class="safe-mode-block">🛡️ <b>BLOKADA WYJŚCIA:</b> Naruszenie zasad.</div>'

            # Log successful request
            if tracker:
                tracker.log_request(self.name, mode, (time.time() - start_time) * 1000, True)

            formatted_response = (
                f"| 🛡️ **Safe Mode Active** |\n"
                f"| :--- |\n"
                f"| {ai_response} |\n\n"
                f"*Twoje bezpieczeństwo jest naszym priorytetem.*"
            )

            return formatted_response
        except Exception as e:
            if tracker:
                tracker.log_request(self.name, mode, (time.time() - start_time) * 1000, False, str(e)[:50])
            return f"❌ Błąd: {str(e)}"
