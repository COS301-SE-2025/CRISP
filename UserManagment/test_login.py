#!/usr/bin/env python3
"""
Simple login test
"""

import requests
import json

def test_login():
    url = "http://127.0.0.1:8000/api/auth/login/"
    
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful!")
            return result.get('tokens', {}).get('access')
        else:
            print("❌ Login failed")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_login()