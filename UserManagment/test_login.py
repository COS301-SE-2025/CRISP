#!/usr/bin/env python3
"""
Simple login test with color-coded output
"""

import requests
import json

# Color printing helpers
def print_success(message):
    print(f"\033[92m✅ {message}\033[0m")  # Green

def print_error(message):
    print(f"\033[91m❌ {message}\033[0m")  # Red

def print_info(message):
    print(f"\033[94mℹ️  {message}\033[0m")  # Blue

def test_login():
    url = "http://127.0.0.1:8000/api/auth/login/"
    
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data)
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print_success("Login successful!")
            return result.get('tokens', {}).get('access')
        else:
            print_error("Login failed")
            return None
            
    except Exception as e:
        print_error(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_login()
