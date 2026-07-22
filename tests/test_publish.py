import os
import tempfile
import unittest
from src.config import Config
from src.publish import Publisher

class TestPublisher(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.allowlist_file = os.path.join(self.temp_dir, 'allowlist.txt')

        with open(self.allowlist_file, 'w') as f:
            f.write("topic1\n")
            f.write("topic2\n")

        self.config = Config()
        self.config.allowlist_file = self.allowlist_file

    def tearDown(self):
        if os.path.exists(self.allowlist_file):
            os.remove(self.allowlist_file)
        os.rmdir(self.temp_dir)

    def test_publish_allowed(self):
        publisher = Publisher(self.config)
        self.assertTrue(publisher.publish("topic1", "test message"))

    def test_publish_not_allowed(self):
        publisher = Publisher(self.config)
        self.assertFalse(publisher.publish("topic3", "test message"))

    def test_publish_no_allowlist(self):
        self.config.allowlist_file = None
        publisher = Publisher(self.config)
        self.assertTrue(publisher.publish("topic3", "test message"))

if __name__ == '__main__':
    unittest.main()