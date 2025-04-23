import requests
import pytest

BASE_URL = "http://192.168.201.107:443"


def test_login_success():
    """Verify successful login returns a valid token"""
    url = f"{BASE_URL}/login"
    payload = {
        "username": "Admin",
        "password": "1"
    }

    response = requests.post(url, json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert "token" in data, "No token found in response!"
    assert len(data["token"]) > 10, "Invalid token length"


def test_login_invalid_credentials():
    """Verify login with wrong credentials fails"""
    url = f"{BASE_URL}/login"
    payload = {
        "username": "wrong_user",
        "password": "wrongpassword"
    }

    response = requests.post(url, json=payload)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert response.json().get("error") == "Invalid credentials"
