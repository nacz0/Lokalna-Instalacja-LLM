import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


UTILS_PATH = Path(__file__).resolve().parents[1] / "pipelines" / "utils"
sys.path.insert(0, str(UTILS_PATH))

from model_selector import ModelSelector


class ModelSelectorTests(unittest.TestCase):
    def test_explicit_argument_has_highest_priority(self):
        with patch.dict(os.environ, {"MODEL_MODE": "advanced"}):
            self.assertEqual(ModelSelector.get_mode("light"), "light")

    def test_environment_mode_is_used_for_auto(self):
        with patch.dict(os.environ, {"MODEL_MODE": "balanced"}):
            self.assertEqual(ModelSelector.get_mode("auto"), "balanced")

    def test_invalid_environment_mode_falls_back_to_ram_detection(self):
        memory = type("Memory", (), {"total": 6 * 1024**3})()
        with patch.dict(os.environ, {"MODEL_MODE": "invalid"}), patch(
            "model_selector.psutil.virtual_memory", return_value=memory
        ):
            self.assertEqual(ModelSelector.get_mode(), "light")


if __name__ == "__main__":
    unittest.main()
