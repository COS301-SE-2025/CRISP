#!/usr/bin/env python3
"""
Test CORS configuration for CRISP React frontend
"""

import requests
import json

def test_cors():
    """Test CORS preflight and actual request"""
    print("🧪 Testing CORS Configuration")
    print("=" * 40)
    
    api_url = "http://127.0.0.1:8000/api/auth/login/"
    frontend_origin = "http://localhost:5173"
    
    # Test 1: CORS Preflight request (OPTIONS)
    print("\n1️⃣ Testing CORS Preflight (OPTIONS)...")
    try:
        preflight_headers = {
            'Origin': frontend_origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type,authorization'
        }
        
        response = requests.options(api_url, headers=preflight_headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
            print("   CORS Headers:")
            for header, value in cors_headers.items():
                print(f"     {header}: {value}")
            
            if 'Access-Control-Allow-Origin' in response.headers:
                print("   ✅ CORS preflight successful")
            else:
                print("   ❌ CORS headers missing")
        else:
            print(f"   ❌ Preflight failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Preflight error: {e}")
    
    # Test 2: Actual login request with Origin header
    print("\n2️⃣ Testing Login with CORS...")
    try:
        login_headers = {
            'Origin': frontend_origin,
            'Content-Type': 'application/json'
        }
        
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(api_url, json=login_data, headers=login_headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login successful with CORS")
            
            # Check if CORS headers are present in actual response
            if 'Access-Control-Allow-Origin' in response.headers:
                print(f"   CORS Origin: {response.headers['Access-Control-Allow-Origin']}")
            else:
                print("   ⚠️ CORS headers missing in response")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    # Test 3: Check API root with CORS
    print("\n3️⃣ Testing API Root with CORS...")
    try:
        response = requests.get("http://127.0.0.1:8000/api/", headers={'Origin': frontend_origin})
        print(f"   Status: {response.status_code}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("   ✅ API root accessible with CORS")
        else:
            print("   ⚠️ CORS headers missing")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_cors()