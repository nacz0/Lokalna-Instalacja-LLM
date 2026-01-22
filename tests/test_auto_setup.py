#!/usr/bin/env python3
"""
Testy jednostkowe i integracyjne dla modułu auto_setup.py.
Testuje funkcje pomocnicze z użyciem mocków (bez połączenia z prawdziwym serwerem).
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Dodaj katalog scripts do PATH
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))


class TestAutoSetupImport(unittest.TestCase):
    """Test że moduł auto_setup mozna zaimportować"""
    
    def test_import_auto_setup(self):
        """Test: można zaimportować moduł auto_setup"""
        import auto_setup
        self.assertTrue(hasattr(auto_setup, 'main'))


class TestConfigurationConstants(unittest.TestCase):
    """Testy stałych konfiguracyjnych"""
    
    def setUp(self):
        import auto_setup
        self.config = auto_setup
    
    def test_admin_email_defined(self):
        """Test: ADMIN_EMAIL jest zdefiniowany"""
        self.assertTrue(hasattr(self.config, 'ADMIN_EMAIL'))
        self.assertIsInstance(self.config.ADMIN_EMAIL, str)
        self.assertIn('@', self.config.ADMIN_EMAIL)
    
    def test_admin_password_defined(self):
        """Test: ADMIN_PASSWORD jest zdefiniowany"""
        self.assertTrue(hasattr(self.config, 'ADMIN_PASSWORD'))
        self.assertIsInstance(self.config.ADMIN_PASSWORD, str)
    
    def test_default_password_defined(self):
        """Test: DEFAULT_PW jest zdefiniowany"""
        self.assertTrue(hasattr(self.config, 'DEFAULT_PW'))
        self.assertIsInstance(self.config.DEFAULT_PW, str)
        self.assertGreaterEqual(len(self.config.DEFAULT_PW), 1)
    
    def test_groups_to_create_defined(self):
        """Test: GROUPS_TO_CREATE jest zdefiniowany i niepusty"""
        self.assertTrue(hasattr(self.config, 'GROUPS_TO_CREATE'))
        self.assertGreater(len(self.config.GROUPS_TO_CREATE), 0)
    
    def test_model_permissions_defined(self):
        """Test: MODEL_PERMISSIONS jest zdefiniowany"""
        self.assertTrue(hasattr(self.config, 'MODEL_PERMISSIONS'))
        self.assertIsInstance(self.config.MODEL_PERMISSIONS, dict)
    
    def test_base_url_defined(self):
        """Test: BASE_URL jest zdefiniowany"""
        self.assertTrue(hasattr(self.config, 'BASE_URL'))
        self.assertIn('http', self.config.BASE_URL)


class TestGroupsConfiguration(unittest.TestCase):
    """Testy konfiguracji grup"""
    
    def setUp(self):
        import auto_setup
        self.config = auto_setup
    
    def test_all_groups_have_name(self):
        """Test: wszystkie grupy mają pole name"""
        for key, group in self.config.GROUPS_TO_CREATE.items():
            self.assertIn('name', group, f"Grupa '{key}' nie ma pola 'name'")
    
    def test_all_groups_have_description(self):
        """Test: wszystkie grupy mają pole description"""
        for key, group in self.config.GROUPS_TO_CREATE.items():
            self.assertIn('description', group, f"Grupa '{key}' nie ma pola 'description'")
    
    def test_required_groups_exist(self):
        """Test: istnieją wymagane grupy (power, normal, safe)"""
        required_keys = {'power', 'normal', 'safe'}
        actual_keys = set(self.config.GROUPS_TO_CREATE.keys())
        self.assertTrue(required_keys.issubset(actual_keys),
                       f"Brakujące grupy: {required_keys - actual_keys}")


class TestModelPermissionsConfiguration(unittest.TestCase):
    """Testy konfiguracji uprawnień modeli"""
    
    def setUp(self):
        import auto_setup
        self.config = auto_setup
    
    def test_model_permissions_valid_groups(self):
        """Test: uprawnienia modeli odnoszą się do istniejących grup"""
        valid_group_keys = set(self.config.GROUPS_TO_CREATE.keys())
        
        for model_id, groups in self.config.MODEL_PERMISSIONS.items():
            for group in groups:
                self.assertIn(group, valid_group_keys,
                             f"Model '{model_id}' odwołuje się do nieistniejącej grupy '{group}'")
    
    def test_safe_mode_available_to_safe_users(self):
        """Test: Safe Mode dostępny dla grupy safe"""
        if 'direct_safe_mode' in self.config.MODEL_PERMISSIONS:
            groups = self.config.MODEL_PERMISSIONS['direct_safe_mode']
            self.assertIn('safe', groups)
    
    def test_power_users_have_most_access(self):
        """Test: Power users mają dostęp do wszystkich zdefiniowanych modeli"""
        for model_id, groups in self.config.MODEL_PERMISSIONS.items():
            self.assertIn('power', groups,
                         f"Power users nie mają dostępu do '{model_id}'")


class TestDefaultGroupPermissions(unittest.TestCase):
    """Testy domyślnych uprawnień grup"""
    
    def setUp(self):
        import auto_setup
        self.config = auto_setup
    
    def test_default_permissions_structure(self):
        """Test: DEFAULT_GROUP_PERMISSIONS ma poprawną strukturę"""
        perms = self.config.DEFAULT_GROUP_PERMISSIONS
        
        self.assertIn('workspace', perms)
    
    def test_workspace_permissions_defined(self):
        """Test: uprawnienia workspace są zdefiniowane"""
        perms = self.config.DEFAULT_GROUP_PERMISSIONS
        workspace = perms.get('workspace', {})
        
        self.assertIn('models', workspace)
        self.assertIn('knowledge', workspace)
        self.assertIn('prompts', workspace)
        self.assertIn('tools', workspace)


class TestFunctionSignatures(unittest.TestCase):
    """Testy sygnatur funkcji"""
    
    def setUp(self):
        import auto_setup
        self.module = auto_setup
    
    def test_wait_for_server_exists(self):
        """Test: funkcja wait_for_server istnieje"""
        self.assertTrue(hasattr(self.module, 'wait_for_server'))
        self.assertTrue(callable(self.module.wait_for_server))
    
    def test_get_token_exists(self):
        """Test: funkcja get_token istnieje"""
        self.assertTrue(hasattr(self.module, 'get_token'))
        self.assertTrue(callable(self.module.get_token))
    
    def test_create_user_exists(self):
        """Test: funkcja create_user istnieje"""
        self.assertTrue(hasattr(self.module, 'create_user'))
        self.assertTrue(callable(self.module.create_user))
    
    def test_create_group_exists(self):
        """Test: funkcja create_group istnieje"""
        self.assertTrue(hasattr(self.module, 'create_group'))
        self.assertTrue(callable(self.module.create_group))
    
    def test_get_groups_exists(self):
        """Test: funkcja get_groups istnieje"""
        self.assertTrue(hasattr(self.module, 'get_groups'))
        self.assertTrue(callable(self.module.get_groups))
    
    def test_setup_groups_exists(self):
        """Test: funkcja setup_groups istnieje"""
        self.assertTrue(hasattr(self.module, 'setup_groups'))
        self.assertTrue(callable(self.module.setup_groups))
    
    def test_activate_user_exists(self):
        """Test: funkcja activate_user istnieje"""
        self.assertTrue(hasattr(self.module, 'activate_user'))
        self.assertTrue(callable(self.module.activate_user))
    
    def test_main_exists(self):
        """Test: funkcja main istnieje"""
        self.assertTrue(hasattr(self.module, 'main'))
        self.assertTrue(callable(self.module.main))


class TestSecurityConfiguration(unittest.TestCase):
    """Testy konfiguracji bezpieczeństwa"""
    
    def setUp(self):
        import auto_setup
        self.config = auto_setup
    
    def test_password_not_empty(self):
        """Test: hasła nie są puste"""
        self.assertTrue(len(self.config.ADMIN_PASSWORD) > 0)
        self.assertTrue(len(self.config.DEFAULT_PW) > 0)
    
    def test_api_endpoint_uses_v1(self):
        """Test: API endpoint używa wersji v1"""
        self.assertIn('/api/v1', self.config.BASE_URL)


class TestHeadersVariable(unittest.TestCase):
    """Testy zmiennej headers"""
    
    def setUp(self):
        import auto_setup
        self.module = auto_setup
    
    def test_headers_initialized(self):
        """Test: zmienna headers jest zainicjalizowana"""
        self.assertTrue(hasattr(self.module, 'headers'))
    
    def test_group_ids_initialized(self):
        """Test: zmienna GROUP_IDS jest zainicjalizowana"""
        self.assertTrue(hasattr(self.module, 'GROUP_IDS'))
        self.assertIsInstance(self.module.GROUP_IDS, dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)
