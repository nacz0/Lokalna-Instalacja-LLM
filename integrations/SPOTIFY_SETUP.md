# 🔐 Spotify Integration - Setup Guide

## Bezpieczeństwo - Credentials nie na GitHub!

Twoje **Client ID** i **Client Secret** są teraz bezpieczne:
- ✅ Przechowywane w `.env` (lokalnie, nie na GitHub)
- ✅ `.env` jest w `.gitignore`
- ✅ Szablon dostępny w `.env.example`

## 📋 Struktura plików

```
integrations/
├── .env                          ← TWOJE credentials (NIGDY nie commituj!)
├── .env.example                  ← Szablon (bezpieczny do commitu)
├── spotify_auth_setup.ps1        ← Setup & token management
├── refresh_spotify_token.ps1     ← Odświeżanie tokena
├── spotify_token.json            ← Zapisane tokeny (wygenerowany)
└── spotify_tool.json             ← OpenWebUI Tool definition
```

## 🚀 Szybki start

### 1. Przygotowanie .env

Plik `.env` już istnieje z Twoimi credentials:

```powershell
SPOTIFY_CLIENT_ID=0bd8f8cfded9489b9106a237eeaebada
SPOTIFY_CLIENT_SECRET=63cd2e15d42844959bf70a38b21a3c70
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

**Ważne:** Nigdy nie commituj `.env` na GitHub! Jest on w `.gitignore`.

### 2. Pierwszy raz - Pozyskaj tokeny

```powershell
cd integrations
.\spotify_auth_setup.ps1
```

Wybierz opcję **1** "Zaloguj się (OAuth - PIERWSZY RAZ)"

**Co się stanie:**
1. Skrypt otworzy link do Spotify logowania
2. Zaloguj się i autoryzuj aplikację
3. Spotify przeniesie Cię na `localhost:8888/callback?code=...`
4. **Skopiuj kod z URL** i wklej w terminalu
5. Skrypt pokaże Access & Refresh Token
6. Tokeny zostaną zapisane w `spotify_token.json`

### 3. Odświeżanie tokena

Kiedy token Access wygaśnie, odśwież go:

```powershell
.\spotify_auth_setup.ps1
# Wybierz opcję 2 "🔄 Odśwież Access Token"
```

Lub bezpośrednio:

```powershell
# Pobierz refresh_token z spotify_token.json
$refreshToken = (Get-Content spotify_token.json | ConvertFrom-Json).refresh_token

# Odśwież
.\refresh_spotify_token.ps1 -RefreshToken $refreshToken
```

## 🔒 Bezpieczeństwo - Best Practices

### DO:
✅ Przechowuj `.env` lokalnie  
✅ Dodaj `.env` do `.gitignore`  
✅ Zmień hasło na Spotify jeśli wyciekło  
✅ Użyj scopes minimalnie (principle of least privilege)  

### NIE:
❌ Nie commituj `.env` na GitHub  
❌ Nie wklejaj tokena w komentarzach  
❌ Nie udostępniaj refresh_token publicznie  
❌ Nie zostawiaj credentials w kodzie hardcoded  

## 📁 Dla nowych developerów

Jeśli ktoś klonuje repozytorium:

1. **Nie będzie `.env` (jest w .gitignore)**
2. Powinien skopiować `.env.example`:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Uzupełnić swoje credentials:
   ```powershell
   # Edytuj .env i wstaw swoje Client ID & Secret
   notepad .env
   ```

## 🛠️ Troubleshooting

### Błąd: "Plik .env nie znaleziony"
```powershell
# Skopiuj szablon
Copy-Item integrations\.env.example integrations\.env
# Edytuj i dodaj swoje credentials
```

### Błąd: "Authorization failed"
- Sprawdź czy Client ID i Secret są poprawne
- Sprawdź czy redirect URI się zgadza
- Upewnij się że aplikacja jest aktywna na https://developer.spotify.com

### Token wygasł
```powershell
.\spotify_auth_setup.ps1  # Wybierz opcję 2
```

## 📚 Dokumentacja

- [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- [OAuth Flow](https://developer.spotify.com/documentation/general/guides/authorization/)
- [Refresh Token Guide](https://developer.spotify.com/documentation/general/guides/authorization/code-flow/)
