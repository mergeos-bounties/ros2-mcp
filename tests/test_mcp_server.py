import unittest
from unittest.mock import patch
from src.mcp_server import MCPServer

class TestMCPServer(unittest.TestCase):
    @patch.dict('os.environ', {'ROS2_MCP_PUB_ALLOWLIST': '/cmd_vel,/turtle1/cmd_vel'})
    def test_allowlist_blocking(self):
        server = MCPServer()

        # Test allowed topic
        allowed_msg = {'topic': '/cmd_vel'}
        self.assertTrue(server.handle_message(allowed_msg))

        # Test blocked topic
        blocked_msg = {'topic': '/blocked_topic'}
        self.assertFalse(server.handle_message(blocked_msg))

        # Test empty allowlist (should allow all)
        with patch.object(server.config, 'pub_allowlist', []):
            self.assertTrue(server.handle_message(blocked_msg))

if __name__ == '__main__':
    unittest.main()