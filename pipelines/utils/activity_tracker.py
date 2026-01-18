"""
Activity Tracker - moduł śledzenia aktywności pipeline'ów
Używa pliku JSON do przechowywania danych między wywołaniami.
"""

import threading
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# Ścieżka do pliku z danymi (w katalogu pipelines)
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "activity_data.json")

class ActivityTracker:
    """Tracker aktywności pipeline'ów z persystencją do pliku JSON."""
    
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
        """Wczytaj dane z pliku JSON."""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[ActivityTracker] Error loading data: {e}")
        return {"activity_log": [], "stats": {}}
    
    def _save_data(self, data: dict):
        """Zapisz dane do pliku JSON."""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ActivityTracker] Error saving data: {e}")
    
    def log_request(self, pipeline_name: str, mode: str, response_time_ms: float, success: bool, error: Optional[str] = None):
        """Zapisz pojedyncze wywołanie pipeline'a."""
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
            
            # Limit do ostatnich 100 wpisów
            if len(data["activity_log"]) > 100:
                data["activity_log"] = data["activity_log"][-100:]
            
            # Aktualizuj statystyki
            if pipeline_name not in data["stats"]:
                data["stats"][pipeline_name] = {
                    "total_calls": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "total_response_time_ms": 0,
                    "modes_used": {}
                }
            
            stats = data["stats"][pipeline_name]
            stats["total_calls"] += 1
            stats["total_response_time_ms"] += response_time_ms
            if success:
                stats["success_count"] += 1
            else:
                stats["error_count"] += 1
            
            if mode not in stats["modes_used"]:
                stats["modes_used"][mode] = 0
            stats["modes_used"][mode] += 1
            
            self._save_data(data)
    
    def get_stats(self) -> Dict[str, Dict]:
        """Zwróć agregowane statystyki dla każdego pipeline'a."""
        with self._data_lock:
            data = self._load_data()
            result = {}
            for name, stats in data.get("stats", {}).items():
                avg_time = 0
                if stats["total_calls"] > 0:
                    avg_time = stats["total_response_time_ms"] / stats["total_calls"]
                result[name] = {
                    **stats,
                    "avg_response_time_ms": round(avg_time, 2)
                }
            return result
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Zwróć ostatnie N wywołań."""
        with self._data_lock:
            data = self._load_data()
            return list(reversed(data.get("activity_log", [])[-limit:]))
    
    def clear_stats(self):
        """Wyczyść wszystkie statystyki."""
        with self._data_lock:
            self._save_data({"activity_log": [], "stats": {}})


# Globalna instancja trackera
tracker = ActivityTracker()
