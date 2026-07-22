import os
import tempfile
import unittest
from src.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'config.txt')
        self.allowlist_file = os.path.join(self.temp_dir, 'allowlist.txt')

        with open(self.config_file, 'w') as f:
            f.write(f"{{'allowlist_file': '{self.allowlist_file}'}}")

        with open(self.allowlist_file, 'w') as f:
            f.write("topic1\n")
            f.write("topic2\n")

    def tearDown(self):
        for file in [self.config_file, self.allowlist_file]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.temp_dir)

    def test_load_config(self):
        config = Config()
        config.load(self.config_file)
        self.assertEqual(config.allowlist_file, self.allowlist_file)

    def test_get_allowlist(self):
        config = Config()
        config.load(self.config_file)
        allowlist = config.get_allowlist()
        self.assertEqual(allowlist, ["topic1", "topic2"])

    def test_get_allowlist_nonexistent(self):
        config = Config()
        config.allowlist_file = "nonexistent.txt"
        self.assertIsNone(config.get_allowlist())

if __name__ == '__main__':
    unittest.main()