from locust import HttpUser, task, between
import requests
from requests.auth import HTTPBasicAuth

class LoginStressTest(HttpUser):
    wait_time = between(1, 3)  # Simulates user wait time before making another request
    token = None  # Store token globally

    def on_start(self):
        """Fetch a fresh token before running tasks"""
        self.get_token()

    def get_token(self):
        """Authenticate using Basic Auth and retrieve access token"""
        auth_url = "http://192.168.201.107:443/Login"  # Change to https if required

        headers = {
            "DeviceName": "ActiveSystemsTablet"
            #"Content-Type": "application/json"
        }

        try:
            #response = requests.post(auth_url, auth=("Admin", "1"), headers=headers,timeout=5)
            response = requests.post(auth_url, headers=headers, auth=HTTPBasicAuth("Admin", "1"), timeout=5)
            response.raise_for_status()  # Raise error for HTTP failures

            # Extract token from response
            self.token = response.json().get("access_token")
            if not self.token:
                print("⚠️ Token not found in response!")
                return

            print(f"✅ Token obtained: {self.token}")

            # Set Authorization header for future requests
            self.headers = {
                "DeviceName": "ActiveSystemsTablet",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch token: {e}")

    @task
    def test_authenticated_request(self):
        """Make an API request using the token"""
        if not self.token:
            print("⚠️ No token available, skipping request")
            return

        response = self.client.get("/SomeEndpoint", headers=self.headers)

        if response.status_code == 200:
            print("✅ Request successful!")
        elif response.status_code == 401:
            print("🔄 Token expired, refreshing...")
            self.get_token()  # Refresh token and retry
        else:
            print(f"❌ Request failed: {response.status_code} {response.text}")
