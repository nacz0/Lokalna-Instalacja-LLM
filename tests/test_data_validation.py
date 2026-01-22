#!/usr/bin/env python3
"""
Testy walidacji danych wejściowych.
Testuje poprawność pliku users.csv i konfiguracji.
"""

import sys
import os
import unittest
import csv
import re

# Ścieżki do plików
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
USERS_CSV_PATH = os.path.join(SCRIPTS_DIR, 'users.csv')


class TestUsersCSVStructure(unittest.TestCase):
    """Testy struktury pliku users.csv"""
    
    def test_csv_file_exists(self):
        """Test: plik users.csv istnieje"""
        self.assertTrue(os.path.exists(USERS_CSV_PATH), 
                       f"Plik {USERS_CSV_PATH} nie istnieje")
    
    def test_csv_has_required_headers(self):
        """Test: CSV zawiera wymagane nagłówki"""
        required_headers = {'group', 'first_name', 'last_name', 'email'}
        
        with open(USERS_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            actual_headers = set(reader.fieldnames)
        
        self.assertTrue(required_headers.issubset(actual_headers),
                       f"Brakujące nagłówki: {required_headers - actual_headers}")
    
    def test_csv_not_empty(self):
        """Test: CSV zawiera dane (nie tylko nagłówki)"""
        with open(USERS_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertGreater(len(rows), 0, "Plik CSV nie zawiera żadnych danych")


class TestUsersCSVData(unittest.TestCase):
    """Testy poprawności danych w users.csv"""
    
    def setUp(self):
        with open(USERS_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.rows = list(reader)
    
    def test_all_groups_are_valid(self):
        """Test: wszystkie grupy są dozwolone (power, normal, safe)"""
        valid_groups = {'power', 'normal', 'safe'}
        
        for i, row in enumerate(self.rows):
            group = row.get('group', '').strip()
            self.assertIn(group, valid_groups, 
                         f"Wiersz {i+2}: Nieznana grupa '{group}'")
    
    def test_all_emails_are_valid_format(self):
        """Test: wszystkie emaile mają poprawny format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for i, row in enumerate(self.rows):
            email = row.get('email', '').strip()
            self.assertTrue(re.match(email_pattern, email),
                           f"Wiersz {i+2}: Niepoprawny email '{email}'")
    
    def test_all_names_are_not_empty(self):
        """Test: wszystkie imiona i nazwiska są wypełnione"""
        for i, row in enumerate(self.rows):
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()
            
            self.assertTrue(len(first_name) > 0,
                           f"Wiersz {i+2}: Puste imię")
            self.assertTrue(len(last_name) > 0,
                           f"Wiersz {i+2}: Puste nazwisko")
    
    def test_no_duplicate_emails(self):
        """Test: brak duplikatów emaili"""
        emails = [row.get('email', '').strip().lower() for row in self.rows]
        duplicates = [email for email in emails if emails.count(email) > 1]
        
        self.assertEqual(len(set(duplicates)), 0,
                        f"Znaleziono duplikaty emaili: {set(duplicates)}")
    
    def test_group_distribution(self):
        """Test: istnieją użytkownicy w każdej grupie"""
        groups = [row.get('group', '').strip() for row in self.rows]
        unique_groups = set(groups)
        
        expected_groups = {'power', 'normal', 'safe'}
        self.assertEqual(unique_groups, expected_groups,
                        f"Brakujące grupy: {expected_groups - unique_groups}")


class TestAutoSetupConfig(unittest.TestCase):
    """Testy konfiguracji auto_setup.py"""
    
    def setUp(self):
        # Import konfiguracji z auto_setup.py
        sys.path.insert(0, SCRIPTS_DIR)
        import auto_setup
        self.config = auto_setup
    
    def test_admin_email_format(self):
        """Test: email admina ma poprawny format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$'
        self.assertTrue(re.match(email_pattern, self.config.ADMIN_EMAIL),
                       f"Niepoprawny format email admina: {self.config.ADMIN_EMAIL}")
    
    def test_groups_to_create_not_empty(self):
        """Test: lista grup do utworzenia nie jest pusta"""
        self.assertGreater(len(self.config.GROUPS_TO_CREATE), 0,
                          "GROUPS_TO_CREATE jest pusta")
    
    def test_groups_have_required_fields(self):
        """Test: każda grupa ma wymagane pola (name, description)"""
        for key, group in self.config.GROUPS_TO_CREATE.items():
            self.assertIn('name', group, f"Grupa '{key}' nie ma pola 'name'")
            self.assertIn('description', group, f"Grupa '{key}' nie ma pola 'description'")
    
    def test_model_permissions_valid_groups(self):
        """Test: uprawnienia modeli odnoszą się do istniejących grup"""
        valid_group_keys = set(self.config.GROUPS_TO_CREATE.keys())
        
        for model_id, groups in self.config.MODEL_PERMISSIONS.items():
            for group in groups:
                self.assertIn(group, valid_group_keys,
                             f"Model '{model_id}' odwołuje się do nieistniejącej grupy '{group}'")
    
    def test_default_password_not_too_short(self):
        """Test: domyślne hasło ma minimum 6 znaków"""
        self.assertGreaterEqual(len(self.config.DEFAULT_PW), 6,
                               "Domyślne hasło jest zbyt krótkie (min 6 znaków)")


class TestGroupPermissions(unittest.TestCase):
    """Testy uprawnień grup"""
    
    def setUp(self):
        sys.path.insert(0, SCRIPTS_DIR)
        import auto_setup
        self.config = auto_setup
    
    def test_default_group_permissions_structure(self):
        """Test: DEFAULT_GROUP_PERMISSIONS ma poprawną strukturę"""
        perms = self.config.DEFAULT_GROUP_PERMISSIONS
        
        self.assertIn('workspace', perms)
        self.assertIn('models', perms['workspace'])
        self.assertIn('knowledge', perms['workspace'])
        self.assertIn('prompts', perms['workspace'])
        self.assertIn('tools', perms['workspace'])
    
    def test_safe_mode_accessible_to_all_groups(self):
        """Test: Safe Mode powinien być dostępny dla wszystkich grup"""
        safe_mode_groups = self.config.MODEL_PERMISSIONS.get('direct_safe_mode', [])
        expected_groups = {'safe', 'normal', 'power'}
        
        self.assertEqual(set(safe_mode_groups), expected_groups,
                        f"Safe Mode powinien być dostępny dla wszystkich grup")
    
    def test_power_user_has_most_access(self):
        """Test: Power User ma dostęp do wszystkich modeli"""
        for model_id, groups in self.config.MODEL_PERMISSIONS.items():
            self.assertIn('power', groups,
                         f"Power User nie ma dostępu do modelu '{model_id}'")


class TestEdgeCases(unittest.TestCase):
    """Testy przypadków granicznych"""
    
    def test_empty_csv_row_handling(self):
        """Test: obsługa pustych wierszy w CSV"""
        # Ten test sprawdza czy parser CSV radzi sobie z pustymi wierszami
        with open(USERS_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            valid_rows = 0
            for row in reader:
                # Sprawdź czy wiersz ma jakiekolwiek niepuste wartości
                if any(v.strip() for v in row.values() if v):
                    valid_rows += 1
        
        self.assertGreater(valid_rows, 0, "Brak prawidłowych wierszy w CSV")
    
    def test_polish_characters_in_names(self):
        """Test: obsługa polskich znaków diakrytycznych w imionach/nazwiskach"""
        polish_chars = set('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')
        
        with open(USERS_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        has_polish = False
        for row in rows:
            name = row.get('first_name', '') + row.get('last_name', '')
            if any(c in polish_chars for c in name):
                has_polish = True
                break
        
        # Informacyjny test - polskie znaki powinny być obsługiwane
        if has_polish:
            self.assertTrue(True, "Plik zawiera polskie znaki diakrytyczne")


if __name__ == "__main__":
    unittest.main(verbosity=2)
