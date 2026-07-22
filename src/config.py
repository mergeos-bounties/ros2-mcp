import os
from typing import List

class Config:
    def __init__(self):
        self.pub_allowlist = self._get_pub_allowlist()

    def _get_pub_allowlist(self) -> List[str]:
        """Get the publish allowlist from environment variable."""
        allowlist_str = os.getenv('ROS2_MCP_PUB_ALLOWLIST', '')
        return [topic.strip() for topic in allowlist_str.split(',') if topic.strip()]