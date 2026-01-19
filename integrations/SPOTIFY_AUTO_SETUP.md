# Spotify Auto Setup

Automatyczne generowanie Spotify tokena dla każdego użytkownika.

## 🚀 Szybki Start

### 1. Przygotowanie (tylko raz)

```powershell
# Zainstaluj wymagane pakiety
pip install requests
```

### 2. Auto-Setup

```powershell
cd integrations
python spotify_auto_setup.py
```

**Co się stanie:**
1. ✅ Otwórzy się przeglądarke z logowaniem Spotify
2. ✅ Zaloguj się na swoje konto
3. ✅ Kliknij "Akceptuj" 
4. ✅ Skrypt automatycznie wyłapie kod
5. ✅ Token będzie zapisany do `spotify_token.json`

### 3. Gotowe!

Wróć do Open WebUI i spróbuj: **"Wyszukaj Bohemian Rhapsody"** 🎵

---

## 📋 Wymagania

- **Python 3.6+**
- **Konto Spotify** (darmowe lub premium)
- **Client ID i Secret** z Spotify Developer Dashboard

## 🔧 Pierwsze uruchomienie

Jeśli nigdy nie uruchamiałeś, najpierw:

```powershell
# Skopiuj szablon
Copy-Item .env.example .env

# Edytuj i wstaw swoje credentials
notepad .env
```

Następnie uruchom skrypt.

## ⚙️ Co się dzieje pod spodem?

1. Skrypt buduje URL do Spotify login
2. Otwiera go w Twojej domyślnej przeglądarce
3. Nasłuchuje na `localhost:8888/callback`
4. Gdy Spotify Cię przeniesie, wyodrębnia kod
5. Wymienia kod na token API
6. Zapisuje token do pliku

Wszystko **automatycznie** - nic nie musisz kopować! 🚀

## 🐛 Problemy?

**"Port 8888 zajęty"**
```powershell
# Zmień w .env:
SPOTIFY_REDIRECT_URI=http://localhost:9999/callback
```

**"Timeout"**
- Upewnij się że zalogowałeś się i kliknąłeś Akceptuj
- Skrypt czeka max 5 minut

**"requests module not found"**
```powershell
pip install requests
```
