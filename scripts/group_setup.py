import requests
import sys

# Konfiguracja
BASE_URL = "http://localhost:3000/api/v1"
ADMIN_EMAIL = "admin@admin.admin"
ADMIN_PASSWORD = "a"

def get_admin_token():
    """Pobiera token JWT dla administratora."""
    url = f"{BASE_URL}/auths/signin"
    payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("token")
    return None

def get_groups(token):
    """Pobiera listę wszystkich grup."""
    url = f"{BASE_URL}/groups/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def create_group(token, name, description=""):
    """Tworzy nową grupę i zwraca jej ID."""
    # Sprawdź czy grupa już istnieje
    existing_groups = get_groups(token)
    for g in existing_groups:
        if g['name'] == name:
            print(f"Grupa '{name}' już istnieje (ID: {g['id']})")
            return g['id']

    url = f"{BASE_URL}/groups/create"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": name, "description": description}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        group_id = response.json().get("id")
        print(f"Utworzono grupę '{name}' (ID: {group_id})")
        return group_id
    else:
        print(f"Błąd tworzenia grupy '{name}': {response.status_code} - {response.text}")
        return None

def get_models(token):
    """Pobiera listę wszystkich modeli."""
    url = f"{BASE_URL}/models/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def update_model_access(token, model_id, group_ids):
    """Aktualizuje uprawnienia dostępu do modelu dla konkretnych grup."""
    # Pobierz aktualne dane modelu
    models = get_models(token)
    target_model = next((m for m in models if m['id'] == model_id), None)
    
    if not target_model:
        print(f"Model '{model_id}' nie został znaleziony.")
        return False

    url = f"{BASE_URL}/models/model/update?id={model_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Kopiujemy całą strukturę modelu i aktualizujemy access_control
    payload = target_model.copy()
    payload['access_control'] = {
        "read": {
            "group_ids": group_ids,
            "user_ids": []
        },
        "write": {
            "group_ids": [],
            "user_ids": []
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Zaktualizowano dostęp do modelu '{model_id}' dla grup: {group_ids}")
        return True
    else:
        print(f"Błąd aktualizacji modelu '{model_id}': {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    print("--- Konfiguracja Grup i Uprawnień Open WebUI ---")
    token = get_admin_token()
    if not token:
        print("Błąd autoryzacji admina.")
        sys.exit(1)

    # 1. Tworzenie grup
    groups = {
        "Power User": create_group(token, "Power User", "Dostęp do wszystkich modeli"),
        "Normal User": create_group(token, "Normal User", "Dostęp do Spotify, Safe i Smart"),
        "Safe User": create_group(token, "Safe User", "Dostęp tylko do Safe Mode")
    }

    if not all(groups.values()):
        print("Nie udało się utworzyć wszystkich grup. Przerywam.")
        sys.exit(1)

    # 2. Konfiguracja uprawnień modeli
    # Safe User widzi tylko safe-mode
    # Normal User widzi spotify, safe-mode, smart-mode
    # Power User widzi wszystko (więc dodajemy go do każdego modelu)

    # Definicja widoczności dla grup
    # Model ID -> List of Group IDs that can see it
    permissions = {
        "direct_safe_mode": [groups["Safe User"], groups["Normal User"], groups["Power User"]],
        "direct_smart_mode": [groups["Normal User"], groups["Power User"]],
        "spotify_spotipy": [groups["Normal User"], groups["Power User"]],
        "pipeline_activity": [groups["Power User"]]  # Tylko dla Power User - dashboard statystyk
    }

    # Zastosuj uprawnienia dla znanych modeli
    for model_id, allowed_group_ids in permissions.items():
        update_model_access(token, model_id, allowed_group_ids)

    # Opcjonalnie: Reszta modeli (typu gemma, llama itp.) powinna być widoczna tylko dla Power User
    # Aby to zrobić, trzeba by przejść przez wszystkie pozostałe modele i je też zaktualizować.
    # Na razie skupiamy się na Twoich potokach.

    print("--- Konfiguracja zakończona pomyślnie ---")
