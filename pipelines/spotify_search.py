"""
title: Spotify Search Pipeline
author: OpenWebUI Integration
version: 1.0.0
"""

from typing import List, Union, Generator, Iterator
import requests
import os


class Pipeline:
    def __init__(self):
        # Token Spotify - zaktualizuj przed użyciem
        self.spotify_token = "BQDAd27z_2n-90IKn-BwV9b2TPTPjEBVsYVoSboI2TooRfvQrmDoRqgGi-Yt3XufxlDfNogf9-EEprLJtiHbh9MO_XqAIr8_HKH-z22zCuX0CztNgw84KXSylWLexzai8FsF4R_eQkV2060sQD39rgmvS4gVf5Mfjjq_D7UELg7B7VUPHSQOlzKCpfP-c15Q-t8YgzANBZYjdSpACa0oJVIK_GxNMCmjlxIQn2ayZl2AjeI3a1Zgvyo"
        self.name = "Spotify Search"

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        """
        Wyszukuje utwory w Spotify na podstawie zapytania użytkownika
        """
        
        # Wyciągnij zapytanie - usuń słowa kluczowe, zostaw artystę/tytuł
        msg_lower = user_message.lower()
        
        # Usuń typowe frazy
        query = msg_lower
        for phrase in ["wyszukaj", "znajdź", "szukaj", "w spotify", "spotify", "utwór", "piosenkę", "dla", "od"]:
            query = query.replace(phrase, "")
        
        query = query.strip()
        
        if not query or len(query) < 2:
            return "Proszę podać nazwę utworu lub artysty do wyszukania w Spotify. Np: 'Wyszukaj Bohemian Rhapsody'"
        
        # Wywołaj Spotify API
        url = "https://api.spotify.com/v1/search"
        params = {
            "q": query,
            "type": "track",
            "limit": 1
        }
        headers = {
            "Authorization": f"Bearer {self.spotify_token}"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 401:
                return "❌ Token Spotify wygasł. Odśwież token używając skryptu refresh_spotify_token.ps1 i zaktualizuj pipeline."
            
            if response.status_code != 200:
                return f"❌ Błąd Spotify API: {response.status_code} - {response.text}"
            
            data = response.json()
            tracks = data.get("tracks", {}).get("items", [])
            
            if not tracks:
                return f"🔍 Nie znaleziono utworów dla zapytania: '{query}'"
            
            # Formatuj wyniki czytelnie
            result = f"🎵 Znalazłem utwór dla '{query}':\n\n"
            for idx, track in enumerate(tracks, 1):
                name = track.get("name", "Unknown")
                artists = ", ".join([artist["name"] for artist in track.get("artists", [])])
                album = track.get("album", {}).get("name", "Unknown")
                url = track.get("external_urls", {}).get("spotify", "")
                
                result += f"**{name}** — {artists}\n"
                result += f"📀 Album: {album}\n"
                result += f"🔗 {url}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Wystąpił błąd: {str(e)}"
