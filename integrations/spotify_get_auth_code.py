#!/usr/bin/env python3
"""
Spotify OAuth Authorization Helper
Proste narzedzie do pozyskania authorization code
"""

import os
import sys
from urllib.parse import urlencode, quote

# Wczytaj .env
def load_env():
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    config = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
    return config

config = load_env()
CLIENT_ID = config.get('SPOTIFY_CLIENT_ID', '')
REDIRECT_URI = config.get('SPOTIFY_REDIRECT_URI', 'http://localhost:3000/callback')

if not CLIENT_ID:
    print("[ERROR] SPOTIFY_CLIENT_ID nie znaleziony w .env")
    sys.exit(1)

# Generuj URL autoryzacji
scope = "playlist-read-private playlist-read-collaborative"
params = {
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'redirect_uri': REDIRECT_URI,
    'scope': scope
}

auth_url = 'https://accounts.spotify.com/authorize?' + urlencode(params)

print("\n" + "="*50)
print("SPOTIFY OAUTH AUTHORIZATION")
print("="*50)
print("\n1. OTWÓRZ ten link w przegladarce:")
print(f"\n{auth_url}\n")
print("2. Zaloguj sie na Spotify")
print("3. Kliknij 'Akceptuj' aby autozyżować aplikację")
print("4. Spotify Cie przekieruje - SKOPIUJ CAŁY URL z paska adresu")
print("\nOryginalny URL:")
print("Redirect URI: " + REDIRECT_URI)
print("\n" + "="*50)

authorization_code = input("\nWklej cały URL lub tylko kod (code=...) z redirectu: ").strip()

if not authorization_code:
    print("[ERROR] Brak kodu!")
    sys.exit(1)

# Jezeli wklejony URL
if 'code=' in authorization_code:
    try:
        code = authorization_code.split('code=')[1].split('&')[0]
        authorization_code = code
    except:
        pass

print("\n[OK] Otrzymany kod:")
print(authorization_code)
print("\nTeraz uruchom:")
print(".\spotify_auth_setup.ps1")
print("I wklej ten kod w skrypcie.")
