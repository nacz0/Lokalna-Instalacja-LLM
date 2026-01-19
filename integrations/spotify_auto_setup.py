#!/usr/bin/env python3
"""
Spotify OAuth Auto-Setup
Automatycznie generuje token dla kazdego uzytkownika
"""

import os
import sys
import json
import webbrowser
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import requests

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code = None
    
    def do_GET(self):
        """Przechwyc redirect z Spotify"""
        if '/callback' in self.path:
            try:
                # Wyciagnij kod z URL
                query_params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
                code = query_params.get('code', [None])[0]
                
                if code:
                    OAuthCallbackHandler.auth_code = code
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = """
                    <html>
                    <head><title>Spotify Authorization</title></head>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: #1DB954;">Success!</h1>
                    <p>Token zostal wygenerowany. Mozna zamknac to okno.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                    return
            except Exception as e:
                print(f"[ERROR] {e}")
        
        self.send_response(400)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Nie pokazuj logów serwera"""
        pass

def load_env():
    """Wczytaj .env"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    config = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
    return config

def main():
    print("\n" + "="*60)
    print("SPOTIFY OAUTH AUTO-SETUP")
    print("="*60)
    
    config = load_env()
    CLIENT_ID = config.get('SPOTIFY_CLIENT_ID', '')
    CLIENT_SECRET = config.get('SPOTIFY_CLIENT_SECRET', '')
    REDIRECT_URI = config.get('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("\n[ERROR] Brakuje SPOTIFY_CLIENT_ID lub SPOTIFY_CLIENT_SECRET w .env")
        sys.exit(1)
    
    print("\n[1] Buduje link do logowania...")
    
    scope = "playlist-read-private playlist-read-collaborative"
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': scope
    }
    auth_url = 'https://accounts.spotify.com/authorize?' + urlencode(params)
    
    print("[2] Uruchamiam serwer nasluchu na porcie 8888...")
    
    try:
        server = HTTPServer(('localhost', 8888), OAuthCallbackHandler)
        print("[3] Otwierám przeglądarke do logowania Spotify...")
        webbrowser.open(auth_url)
        
        print("[4] Czekam na kod z Spotify...")
        print("    (Zaloguj sie i kliknij Akceptuj w przeglądarce)")
        
        # Czekaj na kod max 5 minut
        timeout = 300
        start_time = time.time()
        
        while OAuthCallbackHandler.auth_code is None:
            server.handle_request()
            if time.time() - start_time > timeout:
                print("\n[ERROR] Timeout! Nie otrzymano kodu w ciagu 5 minut.")
                sys.exit(1)
        
        auth_code = OAuthCallbackHandler.auth_code
        print(f"\n[OK] Otrzymany kod!")
        
        print("[5] Wymieniam kod na token...")
        
        token_url = "https://accounts.spotify.com/api/token"
        payload = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        try:
            response = requests.post(token_url, data=payload)
            token_data = response.json()
            
            if 'access_token' not in token_data:
                print(f"[ERROR] {token_data}")
                sys.exit(1)
            
            print("[OK] Token otrzymany!")
            
            # Zapisz token
            spotify_data = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', ''),
                'token_type': token_data.get('token_type', 'Bearer'),
                'expires_in': token_data.get('expires_in', 3600),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            token_file = os.path.join(os.path.dirname(__file__), 'spotify_token.json')
            with open(token_file, 'w') as f:
                json.dump(spotify_data, f, indent=2)
            
            print(f"\n[SUCCESS] Token zapisany do: {token_file}")
            print("\nMozna teraz zamknac to okno i sprobowac Spotify Search!")
            
        except Exception as e:
            print(f"[ERROR] Blad podczas wymiany kodu: {e}")
            sys.exit(1)
    
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
