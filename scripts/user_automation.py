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

def create_user(token, name, email, password, role="user"):
    """Tworzy nowego użytkownika przez panel admina."""
    url = f"{BASE_URL}/auths/add"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": name, "email": email, "password": password, "role": role}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Użytkownik {email} utworzony pomyślnie.")
        return response.json()
    elif response.status_code == 400 and ("already registered" in response.text.lower() or "already exists" in response.text.lower()):
        print(f"Użytkownik {email} już istnieje. Pobieram dane...")
        # Pobierz ID istniejącego użytkownika
        users = requests.get(f"{BASE_URL}/users/", headers=headers).json()
        for u in users:
            if u['email'] == email:
                return u
    print(f"Błąd tworzenia użytkownika: {response.status_code} - {response.text}")
    return None

def assign_models_to_user(token, user_id, model_ids):
    """Przypisuje modele do użytkownika przez endpoint /update."""
    url = f"{BASE_URL}/users/{user_id}/update"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Najpierw pobierz aktualne dane użytkownika
    user_data = requests.get(f"{BASE_URL}/users/", headers=headers).json()
    target_user = next((u for u in user_data if u['id'] == user_id), None)
    
    if not target_user:
        print("Nie znaleziono użytkownika do aktualizacji.")
        return False

    # Przygotuj payload do aktualizacji
    payload = {
        "name": target_user.get("name"),
        "email": target_user.get("email"),
        "role": target_user.get("role"),
        "profile_image_url": target_user.get("profile_image_url"),
        "settings": {
            "ui": {
                "models": model_ids
            }
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Pomyślnie przypisano modele {model_ids} do użytkownika.")
        return True
    else:
        print(f"Błąd przypisywania modeli: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    print("--- Autmatyzacja Open WebUI (Final) ---")
    token = get_admin_token()
    if not token:
        print("Błąd autoryzacji admina.")
        sys.exit(1)
        
    student_email = "student@uczelnia.pl"
    user = create_user(token, "Student", student_email, "haslo123")
    
    if user:
        uid = user.get("id")
        # Wybieramy konkretne modele (pipeline'y)
        # UWAGA: Upewnij się, że nazwy odpowiadają ID modeli w Twoim WebUI
        models = ["safe-mode", "smart-mode"] 
        assign_models_to_user(token, uid, models)
