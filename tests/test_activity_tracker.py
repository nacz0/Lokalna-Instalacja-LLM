#!/usr/bin/env python3
"""
Testy jednostkowe dla modułu ActivityTracker.
Testuje logowanie aktywności, statystyki i persystencję danych.
"""

import sys
import os
import unittest
import tempfile
import json

# Dodaj katalog pipelines/utils do PATH
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pipelines', 'utils'))

# Przed importem - ustaw tymczasowy plik dla testów
import activity_tracker
original_data_file = activity_tracker.DATA_FILE


class TestActivityTrackerLogging(unittest.TestCase):
    """Testy logowania requestów"""
    
    def setUp(self):
        # Używamy tymczasowego pliku dla każdego testu
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        activity_tracker.DATA_FILE = self.temp_file.name
        
        # Tworzymy nową instancję trackera
        activity_tracker.ActivityTracker._instance = None
        self.tracker = activity_tracker.ActivityTracker()
        self.tracker.clear_stats()
    
    def tearDown(self):
        # Przywróć oryginalny plik i usuń tymczasowy
        activity_tracker.DATA_FILE = original_data_file
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_log_successful_request(self):
        """Test: logowanie udanego requestu"""
        self.tracker.log_request("TestPipeline", "balanced", 150.5, True)
        
        stats = self.tracker.get_stats()
        self.assertIn("TestPipeline", stats)
        self.assertEqual(stats["TestPipeline"]["total_calls"], 1)
        self.assertEqual(stats["TestPipeline"]["success_count"], 1)
        self.assertEqual(stats["TestPipeline"]["error_count"], 0)
    
    def test_log_failed_request(self):
        """Test: logowanie nieudanego requestu z błędem"""
        self.tracker.log_request("TestPipeline", "light", 50.0, False, "Connection timeout")
        
        stats = self.tracker.get_stats()
        self.assertEqual(stats["TestPipeline"]["total_calls"], 1)
        self.assertEqual(stats["TestPipeline"]["success_count"], 0)
        self.assertEqual(stats["TestPipeline"]["error_count"], 1)
    
    def test_log_multiple_requests(self):
        """Test: logowanie wielu requestów"""
        self.tracker.log_request("Pipeline1", "balanced", 100.0, True)
        self.tracker.log_request("Pipeline1", "balanced", 200.0, True)
        self.tracker.log_request("Pipeline2", "light", 50.0, False)
        
        stats = self.tracker.get_stats()
        self.assertEqual(stats["Pipeline1"]["total_calls"], 2)
        self.assertEqual(stats["Pipeline2"]["total_calls"], 1)
    
    def test_tracks_modes_used(self):
        """Test: śledzenie użytych trybów"""
        self.tracker.log_request("TestPipeline", "light", 50.0, True)
        self.tracker.log_request("TestPipeline", "balanced", 100.0, True)
        self.tracker.log_request("TestPipeline", "balanced", 150.0, True)
        
        stats = self.tracker.get_stats()
        modes = stats["TestPipeline"]["modes_used"]
        self.assertEqual(modes["light"], 1)
        self.assertEqual(modes["balanced"], 2)


class TestActivityTrackerStatistics(unittest.TestCase):
    """Testy statystyk"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        activity_tracker.DATA_FILE = self.temp_file.name
        
        activity_tracker.ActivityTracker._instance = None
        self.tracker = activity_tracker.ActivityTracker()
        self.tracker.clear_stats()
    
    def tearDown(self):
        activity_tracker.DATA_FILE = original_data_file
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_average_response_time(self):
        """Test: obliczanie średniego czasu odpowiedzi"""
        self.tracker.log_request("TestPipeline", "balanced", 100.0, True)
        self.tracker.log_request("TestPipeline", "balanced", 200.0, True)
        self.tracker.log_request("TestPipeline", "balanced", 300.0, True)
        
        stats = self.tracker.get_stats()
        # Średnia: (100 + 200 + 300) / 3 = 200
        self.assertEqual(stats["TestPipeline"]["avg_response_time_ms"], 200.0)
    
    def test_total_response_time(self):
        """Test: sumowanie całkowitego czasu odpowiedzi"""
        self.tracker.log_request("TestPipeline", "balanced", 100.0, True)
        self.tracker.log_request("TestPipeline", "balanced", 150.0, True)
        
        stats = self.tracker.get_stats()
        self.assertEqual(stats["TestPipeline"]["total_response_time_ms"], 250.0)
    
    def test_empty_stats(self):
        """Test: puste statystyki przed logowaniem"""
        stats = self.tracker.get_stats()
        self.assertEqual(len(stats), 0)


class TestActivityTrackerRecentActivity(unittest.TestCase):
    """Testy ostatniej aktywności"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        activity_tracker.DATA_FILE = self.temp_file.name
        
        activity_tracker.ActivityTracker._instance = None
        self.tracker = activity_tracker.ActivityTracker()
        self.tracker.clear_stats()
    
    def tearDown(self):
        activity_tracker.DATA_FILE = original_data_file
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_get_recent_activity_default_limit(self):
        """Test: pobieranie ostatnich 10 wpisów (domyślnie)"""
        for i in range(15):
            self.tracker.log_request(f"Pipeline{i}", "balanced", 100.0, True)
        
        recent = self.tracker.get_recent_activity()
        self.assertEqual(len(recent), 10)
    
    def test_get_recent_activity_custom_limit(self):
        """Test: pobieranie ostatnich N wpisów"""
        for i in range(10):
            self.tracker.log_request(f"Pipeline{i}", "balanced", 100.0, True)
        
        recent = self.tracker.get_recent_activity(limit=5)
        self.assertEqual(len(recent), 5)
    
    def test_recent_activity_order(self):
        """Test: kolejność wpisów - najnowsze najpierw"""
        self.tracker.log_request("First", "balanced", 100.0, True)
        self.tracker.log_request("Second", "balanced", 100.0, True)
        self.tracker.log_request("Third", "balanced", 100.0, True)
        
        recent = self.tracker.get_recent_activity(limit=3)
        self.assertEqual(recent[0]["pipeline"], "Third")
        self.assertEqual(recent[2]["pipeline"], "First")


class TestActivityTrackerLimit(unittest.TestCase):
    """Testy limitu logów (max 100)"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        activity_tracker.DATA_FILE = self.temp_file.name
        
        activity_tracker.ActivityTracker._instance = None
        self.tracker = activity_tracker.ActivityTracker()
        self.tracker.clear_stats()
    
    def tearDown(self):
        activity_tracker.DATA_FILE = original_data_file
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_log_limit_100_entries(self):
        """Test: log jest ograniczony do 100 wpisów"""
        # Dodaj 120 wpisów
        for i in range(120):
            self.tracker.log_request(f"Pipeline{i}", "balanced", 100.0, True)
        
        # Sprawdź że w pliku jest max 100
        with open(self.temp_file.name, 'r') as f:
            data = json.load(f)
        
        self.assertLessEqual(len(data["activity_log"]), 100)


class TestActivityTrackerPersistence(unittest.TestCase):
    """Testy persystencji danych"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        activity_tracker.DATA_FILE = self.temp_file.name
    
    def tearDown(self):
        activity_tracker.DATA_FILE = original_data_file
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_data_persists_between_instances(self):
        """Test: dane są zachowane między instancjami"""
        # Pierwsza instancja
        activity_tracker.ActivityTracker._instance = None
        tracker1 = activity_tracker.ActivityTracker()
        tracker1.clear_stats()
        tracker1.log_request("PersistTest", "balanced", 123.0, True)
        
        # Druga instancja (symulacja restartu)
        activity_tracker.ActivityTracker._instance = None
        tracker2 = activity_tracker.ActivityTracker()
        
        stats = tracker2.get_stats()
        self.assertIn("PersistTest", stats)
        self.assertEqual(stats["PersistTest"]["total_calls"], 1)
    
    def test_clear_stats_removes_all(self):
        """Test: clear_stats usuwa wszystkie dane"""
        activity_tracker.ActivityTracker._instance = None
        tracker = activity_tracker.ActivityTracker()
        
        tracker.log_request("ToBeCleared", "balanced", 100.0, True)
        tracker.clear_stats()
        
        stats = tracker.get_stats()
        self.assertEqual(len(stats), 0)


class TestActivityTrackerSingleton(unittest.TestCase):
    """Testy wzorca Singleton"""
    
    def test_singleton_same_instance(self):
        """Test: ActivityTracker zwraca tę samą instancję"""
        activity_tracker.ActivityTracker._instance = None
        tracker1 = activity_tracker.ActivityTracker()
        tracker2 = activity_tracker.ActivityTracker()
        
        self.assertIs(tracker1, tracker2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
