# Custom CSS dla Open WebUI

Ten folder zawiera pliki do customizacji wyglądu Open WebUI.

## Pliki

| Plik | Opis |
|------|------|
| `Dockerfile` | Rozszerza bazowy obraz Open WebUI o custom CSS |
| `custom.css` | Niestandardowe style dla interfejsu |

## Jak używać

### 1. Zbuduj i uruchom
```powershell
docker-compose up -d --build
```

### 2. Wymuś przebudowę (po zmianach CSS)
```powershell
docker-compose build --no-cache open-webui
docker-compose up -d
```

## Jak edytować style

1. Otwórz `custom.css`
2. Zmień zmienne kolorów w sekcji `:root`
3. Przebuduj obraz

### Główne zmienne kolorów

```css
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --accent-color: #667eea;
  --bg-primary: #0f0f1a;
  --bg-secondary: #1a1a2e;
}
```

## Przywrócenie domyślnego wyglądu

Zmień w `docker-compose.yml`:
```yaml
open-webui:
  image: ghcr.io/open-webui/open-webui:main  # zamiast build
```
