"""
title: Spotify Search Tool
author: OpenWebUI Integration
version: 1.0.0
description: Tool do wyszukiwania utworów w Spotify API
"""

import requests
from typing import Optional


class Tools:
    def __init__(self):
        self.spotify_token = None
    
    def search_spotify_track(self, query: str, token: Optional[str] = None) -> str:
        """
        Wyszukuje utwory w Spotify API
        
        :param query: Fraza do wyszukania (nazwa utworu, artysty)
        :param token: Token autoryzacyjny Spotify (Bearer token)
        :return: Wyniki wyszukiwania w formacie tekstowym
        """
        url = "https://api.spotify.com/v1/search"
        params = {
            "q": query,
            "type": "track",
            "limit": 5
        }
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        elif self.spotify_token:
            headers["Authorization"] = f"Bearer {self.spotify_token}"
        
        try:
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 401:
                return "❌ Błąd autoryzacji: Brak tokena Spotify. Aby użyć tego narzędzia, potrzebujesz tokena API z Spotify Developer Dashboard."
            
            if response.status_code != 200:
                return f"❌ Błąd API Spotify (status {response.status_code}): {response.text}"
            
            data = response.json()
            tracks = data.get("tracks", {}).get("items", [])
            
            if not tracks:
                return f"🔍 Nie znaleziono utworów dla zapytania: '{query}'"
            
            # Formatowanie wyników
            result = f"🎵 Znalezione utwory dla '{query}':\n\n"
            for idx, track in enumerate(tracks, 1):
                name = track.get("name", "Unknown")
                artists = ", ".join([artist["name"] for artist in track.get("artists", [])])
                album = track.get("album", {}).get("name", "Unknown")
                url = track.get("external_urls", {}).get("spotify", "")
                
                result += f"{idx}. **{name}** - {artists}\n"
                result += f"   Album: {album}\n"
                result += f"   Link: {url}\n\n"
            
            return result
            
        except Exception as e:
            return f"❌ Wystąpił błąd: {str(e)}"
