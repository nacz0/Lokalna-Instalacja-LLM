"""
Spotify Spotipy Pipeline
Searches for a track and returns a Spotify link using Client Credentials.
"""
import os
from typing import List, Union, Generator, Iterator

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except Exception:
    spotipy = None

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(WORKSPACE_ROOT, "integrations", ".env")


def _read_env(path: str) -> dict:
    env = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


class Pipeline:
    def __init__(self):
        self.name = "Spotify Search"
        self.client_id = None
        self.client_secret = None
        self.market = None
        self._load_env()
        self.sp = None
        self._init_client()

    def _load_env(self):
        env = _read_env(ENV_PATH)
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID", env.get("SPOTIFY_CLIENT_ID"))
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", env.get("SPOTIFY_CLIENT_SECRET"))
        self.market = os.getenv("SPOTIFY_MARKET", env.get("SPOTIFY_MARKET"))

    def _init_client(self):
        if spotipy is None:
            return
        if not self.client_id or not self.client_secret:
            return
        auth = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        self.sp = spotipy.Spotify(auth_manager=auth)

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass

    def _extract_query(self, text: str) -> str:
        q = text.lower()
        for phrase in ["wyszukaj", "znajdz", "szukaj", "w spotify", "spotify", "utwór", "utwor", "piosenke", "piosenka", "dla", "od"]:
            q = q.replace(phrase, "")
        return q.strip()

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        if spotipy is None:
            return "Brak biblioteki spotipy. Zainstaluj: pip install spotipy"

        if not (self.client_id and self.client_secret):
            return (
                "Uzupełnij Spotify credentials w integrations/.env (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET).\n"
                "Przykład znajdziesz w integrations/.env.example."
            )

        query = self._extract_query(user_message)
        if not query:
            return "Podaj nazwę utworu lub artysty. Np.: 'Wyszukaj Bohemian Rhapsody'"

        try:
            result = self.sp.search(q=query, type="track", limit=1, market=self.market)
            items = result.get("tracks", {}).get("items", [])
            if not items:
                return f"Nie znaleziono utworu dla: '{query}'"
            t = items[0]
            name = t.get("name", "Unknown")
            artists = ", ".join([a.get("name", "") for a in t.get("artists", []) if a.get("name")])
            album = t.get("album", {}).get("name", "Unknown")
            url = t.get("external_urls", {}).get("spotify", "")
            return f"Znaleziono: {name} - {artists}\nAlbum: {album}\nLink: {url}"
        except Exception as e:
            return f"Błąd wyszukiwania: {e}"
