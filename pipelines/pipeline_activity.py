"""
title: Pipeline Activity
author: AI Assistant
version: 1.0.0
description: Wizualizacja aktywności pipeline'ów - statystyki i historia
"""

import os
import json
from typing import List, Union, Generator, Iterator, Dict
from pydantic import BaseModel, Field

# Ścieżka do pliku z danymi (ta sama co w innych pipeline'ach)
DATA_FILE = "/app/pipelines/activity_data.json"

class ActivityReader:
    """Odczytuje dane z pliku JSON."""
    
    def _load_data(self) -> dict:
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[Pipeline Activity] Error loading data: {e}")
        return {"activity_log": [], "stats": {}}
    
    def get_stats(self) -> Dict[str, Dict]:
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
        data = self._load_data()
        return list(reversed(data.get("activity_log", [])[-limit:]))
    
    def clear_stats(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({"activity_log": [], "stats": {}}, f)
        except Exception as e:
            print(f"[Pipeline Activity] Error clearing: {e}")


tracker = ActivityReader()


class Pipeline:
    class Valves(BaseModel):
        show_recent_limit: int = Field(default=10, description="Liczba ostatnich wywołań do wyświetlenia")
    
    def __init__(self):
        self.name = "📊 Pipeline Activity"
        self.valves = self.Valves()
    
    async def on_startup(self):
        print(f"on_startup: {self.name}")
    
    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        msg_lower = user_message.lower().strip()
        
        # Komenda do czyszczenia statystyk
        if msg_lower in ["clear", "reset", "wyczyść"]:
            tracker.clear_stats()
            return "🗑️ Statystyki zostały wyczyszczone."
        
        # Pobierz dane
        stats = tracker.get_stats()
        recent = tracker.get_recent_activity(self.valves.show_recent_limit)
        
        # Generuj dashboard
        output = []
        output.append("# 📊 Dashboard Aktywności Pipeline'ów\n")
        
        # --- Statystyki ---
        output.append("## 📈 Statystyki\n")
        
        if not stats:
            output.append("*Brak zarejestrowanych wywołań.*\n")
        else:
            output.append("| Pipeline | Wywołania | ✅ Sukces | ❌ Błędy | ⏱️ Śr. czas |")
            output.append("|----------|-----------|----------|---------|-------------|")
            
            for name, s in stats.items():
                success_rate = (s["success_count"] / s["total_calls"] * 100) if s["total_calls"] > 0 else 0
                output.append(
                    f"| {name} | {s['total_calls']} | {s['success_count']} ({success_rate:.0f}%) | {s['error_count']} | {s['avg_response_time_ms']:.0f}ms |"
                )
            output.append("")
            
            # Tryby używane
            output.append("### 🎯 Tryby używane\n")
            for name, s in stats.items():
                if s["modes_used"]:
                    modes_str = ", ".join([f"`{m}`: {c}" for m, c in s["modes_used"].items()])
                    output.append(f"**{name}**: {modes_str}")
            output.append("")
        
        # --- Ostatnia aktywność ---
        output.append(f"## 🕐 Ostatnie {self.valves.show_recent_limit} wywołań\n")
        
        if not recent:
            output.append("*Brak aktywności.*\n")
        else:
            output.append("| Czas | Pipeline | Tryb | Status | Czas odp. |")
            output.append("|------|----------|------|--------|-----------|")
            
            for entry in recent:
                time_str = entry["timestamp"].split("T")[1][:8]
                status = "✅" if entry["success"] else f"❌ {entry.get('error', '')[:20]}"
                output.append(
                    f"| {time_str} | {entry['pipeline']} | `{entry['mode']}` | {status} | {entry['response_time_ms']:.0f}ms |"
                )
            output.append("")
        
        output.append("---")
        output.append("*Wpisz `clear` aby wyczyścić statystyki.*")
        
        return "\n".join(output)
