import requests
import csv
import os
import time

# --- KONFIGURACJA ---
# W kontenerze Docker używamy wewnętrznej nazwy serwisu
BASE_URL = os.getenv("OPEN_WEBUI_URL", "http://open-webui:8080") + "/api/v1"
ADMIN_EMAIL = "admin@admin.admin"
ADMIN_PASSWORD = "a"
DEFAULT_PW = "haslo123"

# Definicje grup do utworzenia
GROUPS_TO_CREATE = {
    "power": {"name": "Power User", "description": "Dostęp do wszystkich modeli"},
    "normal": {"name": "Normal User", "description": "Dostęp do Spotify, Safe i Smart"},
    "safe": {"name": "Safe User", "description": "Dostęp tylko do Safe Mode"}
}

# Mapowanie modeli na grupy (klucze: power, normal, safe)
MODEL_PERMISSIONS = {
    # Modele specjalne (widoczne dla wielu grup)
    "direct_safe_mode": ["safe", "normal", "power"],
    "direct_smart_mode": ["normal", "power"],
    "spotify_spotipy": ["normal", "power"],
    
    # Pozostałe modele (tylko dla Power User)
    "pipeline_activity": ["power"],
    "gemma2:2b": ["power"],
    "llama3:latest": ["power"],
    "llama3.1:latest": ["power"],
    "phi3:mini": ["power"],
    "research-model": ["power"]
}

# Domyślne uprawnienia grupy (zapobiegają błędowi 500)
DEFAULT_GROUP_PERMISSIONS = {
    "workspace": {"models": True, "knowledge": True, "prompts": True, "tools": True}
}

headers = {}
GROUP_IDS = {}  # Będzie wypełnione dynamicznie


def wait_for_server(max_wait=120, interval=5):
    """Czeka aż Open WebUI będzie gotowe do połączeń."""
    print(f"⏳ Czekam na uruchomienie Open WebUI (max {max_wait}s)...")
    waited = 0
    while waited < max_wait:
        try:
            r = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
            if r.status_code == 200:
                print(f"✅ Open WebUI gotowe po {waited}s")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(interval)
        waited += interval
        print(f"   ...czekam ({waited}s)")
    print(f"❌ Open WebUI nie odpowiada po {max_wait}s")
    return False


def ensure_admin_exists():
    """Tworzy konto admina jeśli nie istnieje (pierwszy użytkownik = admin)."""
    # Próbuj signup (działa tylko przy pierwszym uruchomieniu)
    r = requests.post(f"{BASE_URL}/auths/signup", json={
        "name": "Administrator",
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if r.status_code == 200:
        print("✅ Utworzono konto administratora")
        return r.json().get("token")
    # Jeśli konto już istnieje, zaloguj się
    return None


def get_token():
    """Loguje się jako admin i zwraca token JWT."""
    # Najpierw spróbuj utworzyć admina (przy pierwszym uruchomieniu)
    token = ensure_admin_exists()
    if token:
        return token
    
    # Jeśli admin już istnieje, zaloguj się normalnie
    r = requests.post(f"{BASE_URL}/auths/signin", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    if r.status_code == 200:
        return r.json().get("token")
    print(f"❌ Błąd logowania admina: {r.status_code} - {r.text}")
    return None


def get_groups():
    """Pobiera listę wszystkich istniejących grup."""
    r = requests.get(f"{BASE_URL}/groups/", headers=headers)
    if r.status_code == 200:
        return r.json()
    return []


def create_group(key, name, description):
    """Tworzy grupę jeśli nie istnieje. Zwraca ID grupy."""
    existing = get_groups()
    for g in existing:
        if g['name'] == name:
            print(f"✅ Grupa '{name}' już istnieje (ID: {g['id']})")
            return g['id']

    r = requests.post(f"{BASE_URL}/groups/create", headers=headers,
                      json={"name": name, "description": description})
    if r.status_code == 200:
        group_id = r.json().get("id")
        print(f"✅ Utworzono grupę '{name}' (ID: {group_id})")
        return group_id
    else:
        print(f"❌ Błąd tworzenia grupy '{name}': {r.status_code} - {r.text}")
        return None


def setup_groups():
    """Tworzy wszystkie grupy i zapisuje ich ID do GROUP_IDS."""
    global GROUP_IDS
    print("\n--- 1. Tworzenie grup ---")
    for key, info in GROUPS_TO_CREATE.items():
        group_id = create_group(key, info["name"], info["description"])
        if group_id:
            GROUP_IDS[key] = group_id
        else:
            print(f"❌ Nie udało się utworzyć grupy {key}")
            return False
    return True


def create_user(name, email, password):
    """Tworzy użytkownika (Krok 1)."""
    r_add = requests.post(f"{BASE_URL}/auths/add", headers=headers,
                          json={"name": name, "email": email, "password": password, "role": "pending"})
    if r_add.status_code == 200:
        return r_add.json().get('id')
    elif "already" in r_add.text:
        r_list = requests.get(f"{BASE_URL}/users/", headers=headers).json()
        return next((u['id'] for u in r_list if u['email'] == email), None)
    return None


def add_to_group_and_fix(group_id, user_id):
    """Dodaje do grupy i naprawia jej strukturę (Krok 2)."""
    g_data = requests.get(f"{BASE_URL}/groups/id/{group_id}", headers=headers).json()
    u_ids = g_data.get("user_ids", [])

    if user_id not in u_ids:
        u_ids.append(user_id)

    payload = {
        "id": g_data.get("id"),
        "name": g_data.get("name"),
        "description": g_data.get("description", ""),
        "user_ids": u_ids,
        "permissions": DEFAULT_GROUP_PERMISSIONS
    }
    requests.post(f"{BASE_URL}/groups/id/{group_id}/update", headers=headers, json=payload)


def activate_user(user_id):
    """Finalna aktywacja konta (Krok 3)."""
    requests.post(f"{BASE_URL}/users/update/role", headers=headers, json={"id": user_id, "role": "user"})


def set_model_access(all_models, model_id, group_keys):
    """
    Tworzy lub aktualizuje model w bazie danych, aby nadać mu uprawnienia RBAC.
    """
    # 1. Znajdź dane modelu w runtime
    model_runtime_data = next((m for m in all_models if m['id'] == model_id), None)
    
    if not model_runtime_data:
        print(f"⚠️  MODEL NIEZNALEZIONY W RUNTIME: {model_id}. Skip.")
        return

    # 2. Przygotuj ID grup
    allowed_ids = [GROUP_IDS[k] for k in group_keys if k in GROUP_IDS]
    
    # 3. Przygotuj payload
    # Open WebUI wymaga pełnej struktury przy tworzeniu/aktualizacji
    payload = {
        "id": model_id,
        "name": model_runtime_data.get("name", model_id),
        "base_model_id": model_runtime_data.get("base_model_id"),
        "params": model_runtime_data.get("params", {}),
        "meta": model_runtime_data.get("meta", {}),
        "visibility": "private",
        "access_control": {
            "read": {
                "group_ids": allowed_ids,
                "user_ids": []
            }
        }
    }

    # 4. Sprawdź czy model istnieje w bazie (v1/models)
    check_r = requests.get(f"{BASE_URL}/models/model?id={model_id}", headers=headers)
    
    if check_r.status_code == 200:
        # MODEL ISTNIEJE -> UPDATE
        url = f"{BASE_URL}/models/model/update?id={model_id}"
        r = requests.post(url, headers=headers, json=payload)
        action = "Zaktualizowano"
    else:
        # MODEL NIE ISTNIEJE -> CREATE
        # To "wyciągnie" model z Pipelines do bazy danych Open WebUI
        url = f"{BASE_URL}/models/create"
        r = requests.post(url, headers=headers, json=payload)
        action = "Utworzono i zabezpieczono"

    if r.status_code == 200:
        print(f"✅ {action}: {model_id} dla grup: {group_keys}")
    else:
        # Jeśli nadal jest błąd, spróbujmy wymusić update mimo wszystko
        print(f"❌ BŁĄD ({r.status_code}) dla {model_id}: {r.text}")

def main():
    global headers
    print("=" * 50)
    print("AUTO-SETUP: Konfiguracja Open WebUI")
    print("=" * 50)

    # Czekaj aż serwer będzie gotowy
    if not wait_for_server():
        return

    token = get_token()
    if not token:
        print("❌ Nie udało się zalogować. Upewnij się, że admin istnieje.")
        return
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 1. Tworzenie grup
    if not setup_groups():
        print("❌ Nie udało się utworzyć grup. Przerywam.")
        return

    # 2. Proces użytkowników
    print("\n--- 2. Tworzenie użytkowników z users.csv ---")
    if os.path.exists("users.csv"):
        with open("users.csv", mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                full_name = f"{row['first_name']} {row['last_name']}"
                email = row['email']
                group_key = row['group']

                if group_key not in GROUP_IDS:
                    print(f"⚠️  Nieznana grupa '{group_key}' dla {email}")
                    continue

                u_id = create_user(full_name, email, DEFAULT_PW)
                if u_id:
                    add_to_group_and_fix(GROUP_IDS[group_key], u_id)
                    activate_user(u_id)
                    print(f"✅ Gotowy: {email} -> {group_key}")
                time.sleep(0.2)
    else:
        print("⚠️  Brak pliku users.csv - pomijam tworzenie użytkowników")

    # 3. Proces modeli
    print("\n--- 3. Konfiguracja RBAC dla modeli ---")
    
    # Używamy endpointu /api/models (bez /v1), aby pobrać modele "w locie" z Pipelines
    RUNTIME_MODELS_URL = BASE_URL.replace("/v1", "") + "/models"
    
    try:
        r_all = requests.get(RUNTIME_MODELS_URL, headers=headers, timeout=10)
        if r_all.status_code == 200:
            # W tym endpoincie dane są zazwyczaj w kluczu 'data'
            response_json = r_all.json()
            all_available_models = response_json.get("data", response_json) if isinstance(response_json, dict) else response_json
            
            if not all_available_models:
                print(f"❌ Lista modeli nadal pusta na {RUNTIME_MODELS_URL}. Sprawdź w GUI czy Pipelines są aktywne.")
                return

            print(f"🔎 Znaleziono {len(all_available_models)} modeli w runtime. Rozpoczynam przypisywanie...")
            
            for m_id, groups_to_assign in MODEL_PERMISSIONS.items():
                set_model_access(all_available_models, m_id, groups_to_assign)
        else:
            print(f"❌ Błąd pobierania runtime models ({r_all.status_code}): {r_all.text}")
    except Exception as e:
        print(f"❌ Błąd połączenia podczas pobierania modeli: {e}")


if __name__ == "__main__":
    main()