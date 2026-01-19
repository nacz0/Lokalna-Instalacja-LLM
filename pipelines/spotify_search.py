"""
title: Spotify Search Pipeline
author: OpenWebUI Integration
version: 1.0.0
"""

from typing import List, Union, Generator, Iterator
import requests
import os
import json
import subprocess
import sys
import threading
import time
from urllib.parse import quote


class Pipeline:
    def __init__(self):
        self.spotify_token = None
        self.name = "Spotify Search"
        self.token_file = None
        self.client_id = None
        self.redirect_uri = "http://localhost:8888/callback"
        self.load_spotify_config()

    def load_spotify_config(self):
        """Wczytaj konfiguracje Spotify z pliku .env i tokenow"""
        env_file = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "integrations", 
            ".env"
        )
        
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key.strip() == 'SPOTIFY_CLIENT_ID':
                                self.client_id = value.strip()
                            elif key.strip() == 'SPOTIFY_REDIRECT_URI':
                                self.redirect_uri = value.strip()
            except Exception as e:
                print(f"[WARN] Blad wczytywania .env: {e}")
        
        self.token_file = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "integrations", 
            "spotify_token.json"
        )
        
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.spotify_token = data.get("access_token")
                    if self.spotify_token:
                        print(f"[OK] Token Spotify wczytany z pliku")
                    else:
                        print("[WARN] Brak access_token w pliku")
            else:
                print(f"[WARN] Plik spotify_token.json nie znaleziony: {self.token_file}")
        except Exception as e:
            print(f"[ERROR] Blad podczas wczytywania tokena: {e}")

    def get_setup_instructions(self) -> str:
        """Zwroc instrukcje konfiguracji Spotify"""
        integrations_dir = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "integrations"
        )
        
        instructions = """🎵 **Konfiguracja Spotify Search - Pierwsze uruchomienie**

Aby wyszukiwać piosenki w Spotify, musisz skonfigurować dostęp API.

**Kroki:**

1. **Przejdź do folderu integrations i uruchom setup:**
   - Windows: `powershell .\\spotify_setup.ps1` w folderze `integrations/`
   - Linux/Mac: `bash ./spotify_setup.sh` w folderze `integrations/`

2. **Setup przeprowadzi Cię przez:**
   - Rejestrację aplikacji Spotify Developer
   - Ustawienie zmiennych w `.env`
   - Automatyczne pobranie tokena dostępu

3. **Po konfiguracji** - spróbuj ponownie wyszukania piosenki!

📂 **Folder konfiguracji:** `{integrations_dir}`

ℹ️ Szczegółowe instrukcje znajdziesz w: `integrations/README.md`
"""
        return instructions

    def try_auto_setup_token(self) -> bool:
        """Sprobuj automatycznie pobrać token"""
        env_file = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "integrations", 
            ".env"
        )
        
        # Sprawdz czy sa CLIENT_ID i SECRET
        has_client_id = False
        has_client_secret = False
        
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if 'SPOTIFY_CLIENT_ID=' in line and not line.strip().startswith('#'):
                            parts = line.split('=', 1)
                            if len(parts) > 1 and parts[1].strip():
                                has_client_id = True
                        elif 'SPOTIFY_CLIENT_SECRET=' in line and not line.strip().startswith('#'):
                            parts = line.split('=', 1)
                            if len(parts) > 1 and parts[1].strip():
                                has_client_secret = True
            except Exception as e:
                print(f"[WARN] Blad czytania .env: {e}")
                return False
        
        if not (has_client_id and has_client_secret):
            return False
        
        # Sprobuj uruchomić auto_setup w tle
        try:
            auto_setup_script = os.path.join(
                os.path.dirname(__file__), 
                "..", 
                "integrations", 
                "spotify_auto_setup.py"
            )
            
            if not os.path.exists(auto_setup_script):
                print("[WARN] Plik spotify_auto_setup.py nie znaleziony")
                return False
            
            print("[INFO] Uruchamiam automatyczne pobieranie tokena...")
            
            # Uruchom w tle, żeby nie blokowal pipeline'u
            def run_setup():
                try:
                    subprocess.run(
                        [sys.executable, auto_setup_script],
                        cwd=os.path.dirname(auto_setup_script),
                        capture_output=True,
                        timeout=300
                    )
                    # Po setupie - zaladuj token na nowo
                    self.load_spotify_config()
                except Exception as e:
                    print(f"[ERROR] Setup nie udal sie: {e}")
            
            thread = threading.Thread(target=run_setup, daemon=True)
            thread.start()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Nie udalo sie uruchomic auto_setup: {e}")
            return False

    def get_spotify_login_url(self) -> str:
        """Wygeneruj URL do logowania w Spotify"""
        if not self.client_id:
            return "https://accounts.spotify.com/login"
        
        scope = "playlist-read-private playlist-read-collaborative"
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': scope
        }
        
        url = "https://accounts.spotify.com/authorize?"
        url += "&".join([f"{k}={quote(v)}" for k, v in params.items()])
        return url

    async def on_startup(self):
        print(f"on_startup:{__name__}")

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        """
        Wyszukuje utwory w Spotify na podstawie zapytania uzytkownika
        """
        
        if not self.spotify_token:
            # Sprobuj automatycznie pobrać token
            if self.try_auto_setup_token():
                # Czekaj aż token bedzie dostepny (max 30 sekund)
                for i in range(30):
                    time.sleep(1)
                    self.load_spotify_config()
                    if self.spotify_token:
                        print("[OK] Token zostal pobrany podczas auto_setup!")
                        break
                
                if self.spotify_token:
                    # Sprobuj ponownie z nowym tokenem
                    return self.pipe(user_message, model_id, messages, body)
                else:
                    return f"""⏱️ **Setup jest w trakcie...**

Otwórz przeglądarkę i zaloguj się na Spotify. Po zalogowaniu, spróbuj ponownie wyszukania!

Jeśli się nie uda automatycznie, wykonaj ręcznie:
1. Przejdź do folderu `integrations/`
2. Uruchom: `python spotify_auto_setup.py`
3. Zaloguj się w przeglądarce
4. Spróbuj ponownie!"""
            else:
                return self.get_setup_instructions()
        
        msg_lower = user_message.lower()
        query = msg_lower
        for phrase in ["wyszukaj", "znajdz", "szukaj", "w spotify", "spotify", "utwr", "piosenke", "dla", "od"]:
            query = query.replace(phrase, "")
        
        query = query.strip()
        
        if not query or len(query) < 2:
            return "Prosze podac nazwe utworu lub artysty. Np: 'Wyszukaj Bohemian Rhapsody'"
        
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
                return f"""⚠️ **Token Spotify wygasł!**

Twój token dostępu stracił ważność. Musisz go odświeżyć.

**Rozwiązanie:**
1. Przejdź do folderu `integrations/`
2. Uruchom: `powershell .\\refresh_and_restart.ps1` (Windows) lub `bash ./refresh_and_restart.sh` (Linux/Mac)
3. Podaj swój refresh token
4. Spróbuj ponownie!

Po udanym odświeżeniu, wszystko powinno zadziałać 🎵"""
            
            if response.status_code != 200:
                return f"Blad Spotify API: {response.status_code}"
            
            data = response.json()
            tracks = data.get("tracks", {}).get("items", [])
            
            if not tracks:
                return f"Nie znaleziono utworow dla: '{query}'"
            
            result = f"Znalazlem utwr dla '{query}':\n\n"
            for track in tracks:
                name = track.get("name", "Unknown")
                artists = ", ".join([a["name"] for a in track.get("artists", [])])
                album = track.get("album", {}).get("name", "Unknown")
                url_link = track.get("external_urls", {}).get("spotify", "")
                
                result += f"**{name}** - {artists}\n"
                result += f"Album: {album}\n"
                result += f"Link: {url_link}\n"
            
            return result
            
        except Exception as e:
            return f"Blad: {str(e)}"
