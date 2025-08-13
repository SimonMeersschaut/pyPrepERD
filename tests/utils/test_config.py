import unittest
import os

class TestRectangleContains(unittest.TestCase):
    def test_yaml_file_exists(self):
        self.assertTrue(os.path.exists("config/settings.yaml"))