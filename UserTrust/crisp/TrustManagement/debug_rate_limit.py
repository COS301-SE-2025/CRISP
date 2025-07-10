#!/usr/bin/env python3
"""
Debug script to understand rate limiting behavior
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_rate_limiting_debug():
    """Debug version of rate limiting test"""
    print("🔍 Debugging Rate Limiting...")
    
    url = f"{BASE_URL}/auth/login/"
    session = requests.Session()
    
    # Make 10 invalid login attempts and log each response
    for i in range(10):
        data = {
            "username": "invalid",
            "password": "invalid"
        }
        
        try:
            response = session.post(url, json=data)
            print(f"Attempt {i+1} (index {i}): Status {response.status_code}")
            
            if response.status_code == 429:
                print(f"  ❌ Rate limited on attempt {i+1}")
                try:
                    error_data = response.json()
                    print(f"  📝 Response: {error_data}")
                except:
                    print(f"  📝 Response text: {response.text}")
                break
            elif response.status_code in [400, 401]:
                print(f"  ✅ Invalid credentials as expected")
            else:
                print(f"  ⚠️  Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"  💥 Error on attempt {i+1}: {e}")
            break

if __name__ == "__main__":
    test_rate_limiting_debug()
