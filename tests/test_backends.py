import unittest
from unittest.mock import patch, MagicMock
from src.backends import RclpyBackend, CliBackend, MockBackend

class TestBackends(unittest.TestCase):
    def test_rclpy_backend_availability(self):
        with patch.dict('sys.modules', {'rclpy': MagicMock()}):
            backend = RclpyBackend()
            self.assertTrue(backend._rclpy_available)

        with patch.dict('sys.modules', {}, clear=True):
            backend = RclpyBackend()
            self.assertFalse(backend._rclpy_available)

    def test_rclpy_backend_fallback(self):
        with patch.dict('sys.modules', {}, clear=True):
            backend = RclpyBackend()
            # Test that fallback methods are called
            with patch.object(CliBackend, 'get_nodes') as mock_get_nodes:
                backend.get_nodes()
                mock_get_nodes.assert_called_once()

    # Add more tests for other backend methods and edge cases