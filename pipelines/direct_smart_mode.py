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
            r = requests.post(self.valves.ollama_url, json={
                "model": settings["model"],
                "messages": messages,
                "stream": False,
                "options": {"num_predict": settings["max_tokens"], "temperature": settings["temperature"]}
            }, timeout=60)
            r.raise_for_status()
            result = r.json().get("message", {}).get("content", "")
            
            # Log successful request
            if tracker:
                tracker.log_request(self.name, mode, (time.time() - start_time) * 1000, True)
            
            return result
        except Exception as e:
            if tracker:
                tracker.log_request(self.name, mode, (time.time() - start_time) * 1000, False, str(e)[:50])
            return f"❌ Błąd: {str(e)}"
