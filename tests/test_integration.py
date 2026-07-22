import unittest
import os
from src.main import Ros2Mcp

class TestIntegration(unittest.TestCase):
    def test_backend_selection(self):
        # Test auto mode with rclpy available
        with patch.dict('sys.modules', {'rclpy': MagicMock()}):
            os.environ['ROS2_MCP_MODE'] = 'auto'
            mcp = Ros2Mcp()
            self.assertIsInstance(mcp._backend, RclpyBackend)

        # Test auto mode with rclpy not available
        with patch.dict('sys.modules', {}, clear=True):
            os.environ['ROS2_MCP_MODE'] = 'auto'
            mcp = Ros2Mcp()
            self.assertIsInstance(mcp._backend, CliBackend)

        # Test explicit mode selection
        os.environ['ROS2_MCP_MODE'] = 'cli'
        mcp = Ros2Mcp()
        self.assertIsInstance(mcp._backend, CliBackend)

        os.environ['ROS2_MCP_MODE'] = 'mock'
        mcp = Ros2Mcp()
        self.assertIsInstance(mcp._backend, MockBackend)

    # Add more integration tests for backend functionality