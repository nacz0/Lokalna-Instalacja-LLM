# Spotify OAuth - Szybki Start

Jeśli masz problem z Redirect URI, użyj tego prostszego podejścia:

## Krok 1: Uzyskaj Authorization Code

```powershell
cd integrations
python spotify_get_auth_code.py
```

**Co robić:**
1. Otwórz link w przeglądarce
2. Zaloguj się na Spotify
3. Kliknij "Akceptuj"
4. Skopiuj cały URL z paska adresu lub tylko kod
5. Wklej w terminalu

## Krok 2: Exchange Code na Token

Po uzyskaniu kodu, przejdź do drugiego kroku:

```powershell
.\spotify_auth_setup.ps1
```

Wybierz opcję 1 i wklej kod gdy będzie prosić.

## Alternatywa: Zmień Redirect URI

Jeśli dalej nie działa, w `spotify_auth_setup.ps1` zmień:

```powershell
$RedirectUri = "http://localhost:3000"  # zamiast /callback
```

## Problemy?

- **"This redirect URI is not secure"** → To normalne dla HTTP. Spotify akceptuje to dla developmentu
- **"URI mismatch"** → Upewnij się że URL dokładnie się zgadza w Spotify Dashboard
