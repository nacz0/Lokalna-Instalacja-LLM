import psutil
from pydantic import BaseModel, Field

class ModelSettings(BaseModel):
    model: str
    max_tokens: int
    temperature: float
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1

class ModelSelector:
    @staticmethod
    def get_mode(manual_mode: str = "auto"):
        """Wykrywa tryb na podstawie dostępnej pamięci RAM."""
        if manual_mode != "auto":
            return manual_mode
        
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        if ram_gb < 8:
            return "light"
        elif ram_gb < 16:
            return "balanced"
        else:
            return "advanced"
    
    @staticmethod
    def get_settings_for_mode(mode: str, fallback_settings: dict = None):
        """Zwraca ustawienia dla danego trybu."""
        if mode == "light":
            # ZMIANA: gemma2:2b zamiast phi3:mini (mniej halucynacji)
            return {
                "model": "gemma2:2b",
                "max_tokens": 512,        # Zwiększone z 256
                "temperature": 0.4,       # Zwiększone z 0.3
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,
                "num_ctx": 2048
            }
        elif mode == "balanced":
            return {
                "model": "llama3:latest",
                "max_tokens": 1024,       # Zwiększone z 512
                "temperature": 0.5,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,
                "num_ctx": 4096
            }
        elif mode == "advanced":
            return {
                "model": "llama3.1:latest",
                "max_tokens": 2048,       # Zwiększone z 1024
                "temperature": 0.6,       # Obniżone z 0.7 dla precyzji
                "top_p": 0.95,
                "top_k": 50,
                "repeat_penalty": 1.05,
                "num_ctx": 8192
            }
        else:
            # Fallback
            return fallback_settings or {
                "model": "llama3",
                "max_tokens": 512,
                "temperature": 0.5,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1
            }
