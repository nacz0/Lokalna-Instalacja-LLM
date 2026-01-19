"""
title: Smart Mode
author: Ty
version: 2.3.2
"""

import sys
import os
import time
import json
import threading
import requests
import psutil
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# --- ACTIVITY TRACKER (INLINE) ---
DATA_FILE = "/app/pipelines/activity_data.json"

class ActivityTracker:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._data_lock = threading.Lock()
    
    def _load_data(self) -> dict:
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[ActivityTracker] Error loading: {e}")
        return {"activity_log": [], "stats": {}}
    
    def _save_data(self, data: dict):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ActivityTracker] Error saving: {e}")
    
    def log_request(self, pipeline_name: str, mode: str, response_time_ms: float, success: bool, error: Optional[str] = None):
        with self._data_lock:
            data = self._load_data()
            entry = {
                "timestamp": datetime.now().isoformat(),
                "pipeline": pipeline_name,
                "mode": mode,
                "response_time_ms": round(response_time_ms, 2),
                "success": success,
                "error": error
            }
            data["activity_log"].append(entry)
            if len(data["activity_log"]) > 100:
                data["activity_log"] = data["activity_log"][-100:]
            
            if pipeline_name not in data["stats"]:
                data["stats"][pipeline_name] = {"total_calls": 0, "success_count": 0, "error_count": 0, "total_response_time_ms": 0, "modes_used": {}}
            
            stats = data["stats"][pipeline_name]
            stats["total_calls"] += 1
            stats["total_response_time_ms"] += response_time_ms
            if success: stats["success_count"] += 1
            else: stats["error_count"] += 1
            if mode not in stats["modes_used"]: stats["modes_used"][mode] = 0
            stats["modes_used"][mode] += 1
            self._save_data(data)

tracker = ActivityTracker()

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
                max_tokens=settings["max_tokens"],
                temperature=settings["temperature"]
            )
            
            # Log successful request
            if tracker:
                tracker.log_request(self.name, mode, (time.time() - start_time) * 1000, True)
            
            return result
        except Exception as e:
            if tracker:
                tracker.log_request(self.name, mode, (time.time() - start_time) * 1000, False, str(e)[:50])
            return f"❌ Błąd: {str(e)}"
