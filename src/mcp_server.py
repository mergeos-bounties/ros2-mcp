import os
from typing import List, Dict, Any
from .config import Config

class MCPServer:
    def __init__(self):
        self.config = Config()

    def handle_message(self, message: Dict[str, Any]) -> bool:
        """Handle incoming message and check against publish allowlist."""
        if 'topic' not in message:
            return False

        topic = message['topic']
        if not self.config.pub_allowlist or topic in self.config.pub_allowlist:
            return True

        print(f"Blocked message on topic: {topic}")
        return False