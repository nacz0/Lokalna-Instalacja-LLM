"""
title: Smart Mode Auto-Selector
author: AI Assistant
version: 2.0.0
description: Automatycznie dobiera model i parametry na podstawie dostępnego RAM
"""

from typing import List, Union, Generator, Iterator
from pydantic import BaseModel, Field
import os
import sys

# Dodaj ścieżkę do utils
sys.path.append(os.path.dirname(__file__))

from utils.model_selector import ModelSelector
from utils.activity_tracker import tracker

class Pipeline:
    class Valves(BaseModel):
        mode: str = Field(
            default="auto",
            description="Tryb modelu: 'auto' (automatyczny), 'light', 'balanced', 'advanced'"
        )
        ollama_base_url: str = Field(
            default="http://ollama:11434",
            description="URL do Ollama API"
        )
    
    def __init__(self):
        self.name = "Smart Mode Selector"
        self.valves = self.Valves()
        
    async def on_startup(self):
        print(f"🚀 on_startup: {self.name}")
        mode = ModelSelector.get_mode(self.valves.mode)
        settings = ModelSelector.get_settings_for_mode(mode)
        print(f"   📊 Wykryty tryb: {mode}")
        print(f"   🤖 Model: {settings['model']}")
        
    async def on_shutdown(self):
        print(f"🛑 on_shutdown: {self.name}")
    
    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        """
        Pipeline który automatycznie dobiera model i parametry na podstawie RAM.
        """
        import time
        import requests
        
        start_time = time.time()
        
        # 1. Wykryj tryb
        mode = ModelSelector.get_mode(self.valves.mode)
        settings = ModelSelector.get_settings_for_mode(mode)
        
        print(f"\n{'='*60}")
        print(f"🎯 Smart Mode Selector - {mode.upper()}")
        print(f"   Model: {settings['model']}")
        print(f"   Max tokens: {settings['max_tokens']}")
        print(f"   Temperature: {settings['temperature']}")
        print(f"{'='*60}\n")
        
        # 2. Przygotuj payload dla Ollama
        url = f"{self.valves.ollama_base_url}/api/chat"
        
        payload = {
            "model": settings["model"],
            "messages": messages,
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
        
        # 3. Wywołaj Ollama ze streamingiem
        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)
            response.raise_for_status()
            
            def generate():
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        import json
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            text = chunk["message"]["content"]
                            full_response += text
                            yield text
                
                # Zapisz aktywność
                elapsed = (time.time() - start_time) * 1000
                tracker.log_activity(
                    pipeline_name=self.name,
                    mode=mode,
                    success=True,
                    response_time_ms=elapsed
                )
            
            return generate()
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            tracker.log_activity(
                pipeline_name=self.name,
                mode=mode,
                success=False,
                response_time_ms=elapsed,
                error=str(e)
            )
            return f"❌ Błąd: {str(e)}"
