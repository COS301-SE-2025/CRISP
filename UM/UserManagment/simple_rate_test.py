#!/usr/bin/env python3
"""
Simple test to verify rate limiting behavior in isolation
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def clear_django_cache():
    """Clear Django cache before testing"""
    import os
    import sys
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    import django
    django.setup()
    from django.core.cache import cache
    cache.clear()
    print("✅ Django cache cleared")

def simple_rate_limit_test():
    """Simple rate limiting test"""
    print("🧪 Simple Rate Limiting Test")
    print("=" * 50)
    
    # Clear cache first
    clear_django_cache()
    
    url = f"{BASE_URL}/auth/login/"
    
    # Test with a new session to avoid any session-based issues
    session = requests.Session()
    
    print("\n🔍 Making invalid login attempts...")
    
    for i in range(8):  # Try 8 attempts to be sure
        data = {
            "username": f"testuser{i}",  # Use different usernames to avoid any user-specific limiting
            "password": "invalidpassword"
        }
        
        try:
            response = session.post(url, json=data, timeout=10)
            status = response.status_code
            
            print(f"Attempt {i+1:2d}: Status {status} ", end="")
            
            if status == 401:
                print("✅ Invalid credentials (expected)")
            elif status == 400:
                print("✅ Bad request (expected)")
            elif status == 429:
                print("🚫 Rate limited!")
                try:
                    data = response.json()
                    print(f"           Message: {data.get('message', 'No message')}")
                except:
                    print(f"           Raw response: {response.text[:100]}")
                break
            else:
                print(f"❓ Unexpected status")
                try:
                    data = response.json()
                    print(f"           Response: {data}")
                except:
                    print(f"           Raw response: {response.text[:100]}")
            
            # Small delay between attempts
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Attempt {i+1:2d}: ❌ Error: {e}")
            break
    
    print("\n🏁 Test completed")

if __name__ == "__main__":
    simple_rate_limit_test()
