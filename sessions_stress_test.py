from locust import HttpUser, task, between
from requests.auth import HTTPBasicAuth

class MyServerUser(HttpUser):
    host = "http://192.168.201.107:443"  # Target server
    wait_time = between(1, 0.5)  # Simulated user wait time

    def on_start(self):
        """Runs when a user starts a test."""
        self.client.auth = HTTPBasicAuth("Admin", "1")  # Replace with actual credentials
        self.client.headers.update({"DeviceName": "ActiveSystemsTablet"})  # Set custom header

    @task
    def test_homepage(self):
        self.client.get("/")  # Modify to test specific API routes

    @task
    def test_login(self):
        self.client.post(
            "/login",
            json={"username": "Marlo", "password": "1"},  # Example payload
        )

