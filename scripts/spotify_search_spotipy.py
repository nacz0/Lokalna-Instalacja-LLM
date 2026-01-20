"""
Simple Spotify track search using Spotipy + OAuth.
Reads credentials from integrations/.env and prints first match URL.
Usage:
    python scripts/spotify_search_spotipy.py "Bohemian Rhapsody"
"""
import os
import sys
from typing import Optional

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
except Exception as e:
    print("[ERROR] Missing spotipy. Install with: pip install spotipy")
    raise

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


def get_spotify_client() -> spotipy.Spotify:
    env = _read_env(ENV_PATH)
    client_id = os.getenv("SPOTIFY_CLIENT_ID", env.get("SPOTIFY_CLIENT_ID"))
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", env.get("SPOTIFY_CLIENT_SECRET"))
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", env.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:9090"))
    scope = os.getenv("SPOTIFY_SCOPE", env.get("SPOTIFY_SCOPE", "user-read-private"))
    use_client_credentials = os.getenv("SPOTIFY_USE_CLIENT_CREDENTIALS", env.get("SPOTIFY_USE_CLIENT_CREDENTIALS", "1"))

    if not client_id or not client_secret:
        raise RuntimeError("SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET missing. Fill integrations/.env")

    # If only search is needed, prefer Client Credentials (no redirect_uri)
    if str(use_client_credentials).lower() in ("1", "true", "yes"):
        cc_mgr = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        return spotipy.Spotify(auth_manager=cc_mgr)
    else:
        auth_mgr = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            open_browser=True,
            cache_path=os.path.join(WORKSPACE_ROOT, "integrations", "spotify_token_cache")
        )
        return spotipy.Spotify(auth_manager=auth_mgr)


def search_track_url(query: str, market: Optional[str] = None) -> Optional[str]:
    sp = get_spotify_client()
    result = sp.search(q=query, type="track", limit=1, market=market)
    items = result.get("tracks", {}).get("items", [])
    if not items:
        return None
    return items[0].get("external_urls", {}).get("spotify")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/spotify_search_spotipy.py \"Song name or artist\"")
        sys.exit(1)
    query = " ".join(sys.argv[1:]).strip()
    market = os.getenv("SPOTIFY_MARKET")
    url = search_track_url(query, market=market)
    if url:
        print(url)
    else:
        print("No track found for:", query)


if __name__ == "__main__":
    main()
