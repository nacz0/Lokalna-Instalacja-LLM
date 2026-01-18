import psutil
from pydantic import BaseModel, Field

class ModelSettings(BaseModel):
    model: str
    max_tokens: int
    temperature: float

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
            return {
                "model": "phi3:mini",
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
                "model": "llama3.1:latest",
                "max_tokens": 1024,
                "temperature": 0.7
            }
        else:
            # Fallback
            return fallback_settings or {
                "model": "llama3",
                "max_tokens": 512,
                "temperature": 0.5
            }
