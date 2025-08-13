import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_login():
    login_data = {"username": "admin_test", "password": "admin123"}
    url = f"{BASE_URL}/api/v1/auth/login/"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=login_data, timeout=15)
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response JSON: {response.json()}")
        except json.JSONDecodeError:
            print(f"Response Text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_login()