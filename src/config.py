import os
from typing import Optional

class Config:
    def __init__(self):
        self.allowlist_file: Optional[str] = None

    def load(self, config_path: str) -> None:
        """Load configuration from a file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = eval(f.read())  # Note: Using eval for simplicity, consider using json for production

            self.allowlist_file = config.get('allowlist_file')

    def get_allowlist(self) -> Optional[list]:
        """Get the allowlist from the configured file."""
        if not self.allowlist_file or not os.path.exists(self.allowlist_file):
            return None

        with open(self.allowlist_file, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]