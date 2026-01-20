# Test integracji Spotify z OpenWebUI

## 1. Przygotowanie środowiska

✅ **Utworzyłem folder `integrations/` w repozytorium projektu**

✅ **Przygotowałem przykładowy plik `test_spotify_api.md` z instrukcjami testowymi**

✅ **Sprawdziłem, że kontener OpenWebUI pozwala na wykonywanie komend i wywołań HTTP z poziomu narzędzi (Tools)**

## 2. Test połączenia z zewnętrznym API (Spotify Web API – bez logowania)

### Endpoint: Wyszukiwanie utworu
```bash
curl -X GET "https://api.spotify.com/v1/search?q=Bohemian%20Rhapsody&type=track&limit=1"
```

**Oczekiwany rezultat:**
- Status HTTP 401 (Unauthorized) - ponieważ nie mamy tokena
- Lub dane utworu jeśli endpoint jest publiczny

### Test z PowerShell:
```powershell
curl.exe -X GET "https://api.spotify.com/v1/search?q=Bohemian%20Rhapsody&type=track&limit=1"
```

## 3. Test narzędzia (Tool) w OpenWebUI

### Utworzenie prostego Tool w formacie JSON/Python:

**Funkcjonalność narzędzia:**
- przyjmuje zapytanie od użytkownika
- wykonuje żądanie HTTP do Spotify API
- zwraca przetworzony wynik do modelu LLM

### Przykładowy kod Tool (Python):

```python
import requests
import json

def search_spotify(query: str, token: str = None) -> dict:
    """
    Wyszukuje utwory w Spotify API
    
    Args:
        query: Fraza do wyszukania
        token: Token autoryzacyjny Spotify (opcjonalnie)
    
    Returns:
        dict: Wyniki wyszukiwania
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
    
    try:
        response = requests.get(url, params=params, headers=headers)
        return {
            "status": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
            "error": None if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }
```

### Test w OpenWebUI:

1. Przejdź do **Settings** → **Tools** (lub **Workspace** → **Tools**)
2. Kliknij **+ Create Tool**
3. Wklej kod Python
4. Przetestuj wywołanie: `search_spotify("Bohemian Rhapsody")`

**Wynik oczekiwany:** 
- Tool poprawnie wykonuje funkcję i odsyła wynik do modelu LLM
- Model może odpowiedzieć na podstawie danych z API (lub błędu 401)

## 4. Wyniki testów

### ✅ SUKCES - Integracja działa poprawnie!

**Test wykonany:** Zapytanie "search for a track in Spotify"

**Rezultat:**
- Tool `searchSpotifyTrack` został wywołany ✅
- OpenWebUI nawiązało połączenie z Spotify API ✅
- Otrzymano odpowiedź HTTP 401 (Unauthorized) ✅
- Model poprawnie zinterpretował błąd: "no token was provided" ✅

**Potwierdzone możliwości:**
- ✅ OpenWebUI komunikuje się z zewnętrznymi API (HTTP REST)
- ✅ Tools mogą wykonywać zapytania do serwisów zewnętrznych
- ✅ Model LLM otrzymuje i interpretuje odpowiedzi z API
- ✅ Obsługa błędów działa poprawnie (401, brak tokena)

### 🔧 Integracja może być rozszerzona o:
- **pełną autoryzację OAuth2 Spotify** - po uzyskaniu Client ID i Secret
- **sterowanie odtwarzaniem muzyki** - play, pause, next, previous
- **tworzenie playlist** - dodawanie utworów do playlisty użytkownika

## 5. Instrukcja instalacji Tool w OpenWebUI

### Krok 1: Zainstaluj Tool
1. Otwórz OpenWebUI: http://localhost:3000
2. Kliknij ikonę użytkownika → **Workspace** → **Tools**
3. Kliknij **+** (dodaj nowy Tool)
4. Skopiuj zawartość pliku `spotify_tool.py`
5. Wklej kod i zapisz Tool

### Krok 2: Przetestuj Tool

**Opcja A: Test w czacie OpenWebUI**
1. Wróć do głównego okna czatu w OpenWebUI
2. W ustawieniach czatu (ikona ⚙️) upewnij się, że Tool "Spotify" jest włączony
3. Napisz w czacie:
   ```
   Wyszukaj utwór Bohemian Rhapsody w Spotify
   ```
4. Model powinien użyć zewnętrznego API Spotify

**Opcja B: Test bezpośrednio z terminala**
Uruchom w PowerShell:
```powershell
curl.exe -X GET "https://api.spotify.com/v1/search?q=Bohemian%20Rhapsody&type=track&limit=1"
```

**Oczekiwany wynik:**
- Status 401 (Unauthorized) - potwierdza że API działa, ale wymaga tokena
- Lub dane utworu jeśli OpenWebUI przekazuje token automatycznie

### Krok 3: (Opcjonalnie) Uzyskaj token Spotify
1. Przejdź do https://developer.spotify.com/dashboard
2. Zaloguj się lub utwórz konto
3. Utwórz nową aplikację
4. Skopiuj **Client ID** i **Client Secret**
5. Wygeneruj token dostępowy

## 6. Następne kroki

- [ ] Uzyskać Spotify Developer credentials (Client ID, Client Secret)
- [ ] Zaimplementować przepływ OAuth2 dla Spotify
- [ ] Utworzyć Tool z pełną funkcjonalnością sterowania Spotify
- [ ] Przetestować integrację end-to-end

## 7. Test z tokenem Spotify (Bearer)

Jeśli masz już token Spotify (Bearer), możesz wykonać pełny test:

### PowerShell (zalecane na Windows):

```powershell
# Podstaw komendę swoim tokenem
$TOKEN = "WKLEJ_TUTAJ_SWÓJ_TOKEN"

# Uruchom test helper
powershell -ExecutionPolicy Bypass -File .\integrations\test_spotify.ps1 -Token $TOKEN -Query "Bohemian Rhapsody" -Limit 3
```

### OpenWebUI (Tools → External Tool Servers):

**Krok 1: Dodaj Tool**
- Workspace → Tools → Manage Tool Servers → Add Connection
- Import → wklej zawartość `integrations/spotify_tool.json`

**Krok 2: Skonfiguruj autoryzację**
- Wybierz dodany Tool Spotify
- Auth → wybierz **"Bearer"**
- Wklej aktualny token (z `refresh_spotify_token.ps1`):
  ```
  BQDAd27z_2n-90IKn-BwV9b2TPTPjEBVsYVoSboI2TooRfvQrmDoRqgGi-Yt3XufxlDfNogf9-EEprLJtiHbh9MO_XqAIr8_HKH-z22zCuX0CztNgw84KXSylWLexzai8FsF4R_eQkV2060sQD39rgmvS4gVf5Mfjjq_D7UELg7B7VUPHSQOlzKCpfP-c15Q-t8YgzANBZYjdSpACa0oJVIK_GxNMCmjlxIQn2ayZl2AjeI3a1Zgvyo
  ```
- Zapisz

**Krok 3: Włącz w czacie**
- W czacie kliknij ⚙️ → zaznacz "searchSpotifyTrack"
- Napisz: "Wyszukaj The Outsider by Perfect Circle w Spotify"

**Oczekiwany wynik:** lista utworów z nazwą, artystą, albumem i linkiem Spotify.
