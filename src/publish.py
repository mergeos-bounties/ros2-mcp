from typing import Optional
from .config import Config

class Publisher:
    def __init__(self, config: Config):
        self.config = config

    def publish(self, topic: str, message: str) -> bool:
        """Publish a message to a topic if it's in the allowlist."""
        allowlist = self.config.get_allowlist()

        if allowlist is not None and topic not in allowlist:
            print(f"Topic {topic} not in allowlist")
            return False

        # Actual publish logic would go here
        print(f"Published to {topic}: {message}")
        return True