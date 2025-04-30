import unittest
from locust import HttpUser
from locustfile import WebsiteUser
from tasks.price_task import PriceTaskSet

class TestWebsiteUser(unittest.TestCase):
    def test_host(self):
        # Test if the host is correctly set
        self.assertEqual(WebsiteUser.host, "https://ygg.brf.cloud")

    def test_tasks(self):
        # Test if the tasks list contains the correct task set
        self.assertIn(PriceTaskSet, WebsiteUser.tasks)

if __name__ == "__main__":
    unittest.main()