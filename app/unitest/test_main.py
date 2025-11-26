import unittest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestHealthCheck(unittest.TestCase):

    def test_health_check(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("services", data)
        self.assertIn("database", data["services"])
        self.assertIn("redis", data["services"])
        self.assertIn("rabbitmq", data["services"])


if __name__ == "__main__":
    unittest.main()
