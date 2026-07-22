import os
from typing import Optional

from .backends import BaseBackend, CliBackend, MockBackend, RclpyBackend

class Ros2Mcp:
    def __init__(self):
        self._backend: Optional[BaseBackend] = None
        self._initialize_backend()

    def _initialize_backend(self):
        mode = os.getenv('ROS2_MCP_MODE', 'auto').lower()

        if mode == 'rclpy':
            self._backend = RclpyBackend()
        elif mode == 'cli':
            self._backend = CliBackend()
        elif mode == 'mock':
            self._backend = MockBackend()
        else:  # auto
            try:
                # Try to use rclpy first
                self._backend = RclpyBackend()
                if not self._backend._rclpy_available:
                    raise ImportError
            except ImportError:
                # Fall back to CLI
                self._backend = CliBackend()

    # Rest of the implementation remains the same