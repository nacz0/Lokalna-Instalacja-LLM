#!/usr/bin/env python3
"""
Testy jednostkowe dla modułu ModelSelector.
Testuje automatyczny wybór trybu na podstawie RAM oraz zwracanie ustawień modeli.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Dodaj katalog pipelines/utils do PATH
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pipelines', 'utils'))

from model_selector import ModelSelector


class TestModelSelectorGetMode(unittest.TestCase):
    """Testy metody get_mode()"""
    
    def test_manual_mode_light(self):
        """Test: przekazanie trybu 'light' omija auto-detekcję"""
        result = ModelSelector.get_mode("light")
        self.assertEqual(result, "light")
    
    def test_manual_mode_balanced(self):
        """Test: przekazanie trybu 'balanced' omija auto-detekcję"""
        result = ModelSelector.get_mode("balanced")
        self.assertEqual(result, "balanced")
    
    def test_manual_mode_advanced(self):
        """Test: przekazanie trybu 'advanced' omija auto-detekcję"""
        result = ModelSelector.get_mode("advanced")
        self.assertEqual(result, "advanced")
    
    @patch('model_selector.psutil.virtual_memory')
    def test_auto_mode_low_ram_returns_light(self, mock_vm):
        """Test: RAM < 8GB zwraca tryb 'light'"""
        mock_vm.return_value = MagicMock(total=6 * (1024**3))  # 6 GB
        result = ModelSelector.get_mode("auto")
        self.assertEqual(result, "light")
    
    @patch('model_selector.psutil.virtual_memory')
    def test_auto_mode_medium_ram_returns_balanced(self, mock_vm):
        """Test: 8GB <= RAM < 16GB zwraca tryb 'balanced'"""
        mock_vm.return_value = MagicMock(total=12 * (1024**3))  # 12 GB
        result = ModelSelector.get_mode("auto")
        self.assertEqual(result, "balanced")
    
    @patch('model_selector.psutil.virtual_memory')
    def test_auto_mode_high_ram_returns_advanced(self, mock_vm):
        """Test: RAM >= 16GB zwraca tryb 'advanced'"""
        mock_vm.return_value = MagicMock(total=32 * (1024**3))  # 32 GB
        result = ModelSelector.get_mode("auto")
        self.assertEqual(result, "advanced")
    
    @patch('model_selector.psutil.virtual_memory')
    def test_auto_mode_exactly_8gb_returns_balanced(self, mock_vm):
        """Test graniczny: dokładnie 8GB zwraca 'balanced'"""
        mock_vm.return_value = MagicMock(total=8 * (1024**3))  # 8 GB
        result = ModelSelector.get_mode("auto")
        self.assertEqual(result, "balanced")
    
    @patch('model_selector.psutil.virtual_memory')
    def test_auto_mode_exactly_16gb_returns_advanced(self, mock_vm):
        """Test graniczny: dokładnie 16GB zwraca 'advanced'"""
        mock_vm.return_value = MagicMock(total=16 * (1024**3))  # 16 GB
        result = ModelSelector.get_mode("auto")
        self.assertEqual(result, "advanced")


class TestModelSelectorGetSettings(unittest.TestCase):
    """Testy metody get_settings_for_mode()"""
    
    def test_light_mode_settings(self):
        """Test: tryb 'light' zwraca poprawne ustawienia dla gemma2:2b"""
        settings = ModelSelector.get_settings_for_mode("light")
        
        self.assertEqual(settings["model"], "gemma2:2b")
        self.assertEqual(settings["max_tokens"], 512)
        self.assertEqual(settings["temperature"], 0.4)
        self.assertEqual(settings["top_p"], 0.9)
        self.assertEqual(settings["top_k"], 40)
        self.assertEqual(settings["repeat_penalty"], 1.1)
        self.assertEqual(settings["num_ctx"], 2048)
    
    def test_balanced_mode_settings(self):
        """Test: tryb 'balanced' zwraca poprawne ustawienia dla llama3"""
        settings = ModelSelector.get_settings_for_mode("balanced")
        
        self.assertEqual(settings["model"], "llama3:latest")
        self.assertEqual(settings["max_tokens"], 1024)
        self.assertEqual(settings["temperature"], 0.5)
        self.assertEqual(settings["num_ctx"], 4096)
    
    def test_advanced_mode_settings(self):
        """Test: tryb 'advanced' zwraca poprawne ustawienia dla llama3.1"""
        settings = ModelSelector.get_settings_for_mode("advanced")
        
        self.assertEqual(settings["model"], "llama3.1:latest")
        self.assertEqual(settings["max_tokens"], 2048)
        self.assertEqual(settings["temperature"], 0.6)
        self.assertEqual(settings["num_ctx"], 8192)
    
    def test_unknown_mode_returns_fallback(self):
        """Test: nieznany tryb zwraca domyślne ustawienia fallback"""
        settings = ModelSelector.get_settings_for_mode("unknown_mode")
        
        self.assertEqual(settings["model"], "llama3")
        self.assertEqual(settings["max_tokens"], 512)
        self.assertEqual(settings["temperature"], 0.5)
    
    def test_custom_fallback_settings(self):
        """Test: nieznany tryb z custom fallback zwraca te ustawienia"""
        custom_fallback = {
            "model": "custom_model",
            "max_tokens": 256,
            "temperature": 0.3
        }
        settings = ModelSelector.get_settings_for_mode("unknown", fallback_settings=custom_fallback)
        
        self.assertEqual(settings["model"], "custom_model")
        self.assertEqual(settings["max_tokens"], 256)
        self.assertEqual(settings["temperature"], 0.3)
    
    def test_all_modes_return_required_keys(self):
        """Test: wszystkie tryby zwracają wymagane klucze"""
        required_keys = ["model", "max_tokens", "temperature"]
        
        for mode in ["light", "balanced", "advanced"]:
            settings = ModelSelector.get_settings_for_mode(mode)
            for key in required_keys:
                self.assertIn(key, settings, f"Brak klucza '{key}' w trybie '{mode}'")


class TestModelSelectorEdgeCases(unittest.TestCase):
    """Testy przypadków granicznych"""
    
    def test_empty_string_mode(self):
        """Test: pusty string jako tryb - nie jest 'auto' więc zwraca pusty string"""
        result = ModelSelector.get_mode("")
        self.assertEqual(result, "")
    
    def test_case_sensitivity(self):
        """Test: tryby są case-sensitive"""
        # "AUTO" nie jest rozpoznawany jako "auto"
        result = ModelSelector.get_mode("AUTO")
        self.assertEqual(result, "AUTO")  # zwraca to co dostał
    
    def test_none_fallback(self):
        """Test: gdy fallback jest None, używane są domyślne ustawienia"""
        settings = ModelSelector.get_settings_for_mode("unknown", fallback_settings=None)
        self.assertIsNotNone(settings)
        self.assertIn("model", settings)


if __name__ == "__main__":
    unittest.main(verbosity=2)
