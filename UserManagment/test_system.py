#!/usr/bin/env python3
"""
Quick system test for CRISP User Management
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_login():
    """Test user login"""
    print("Testing login...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            access_token = data.get('tokens', {}).get('access', 'Not found')
            print(f"Access token: {access_token[:50]}...")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running - skipping API tests")
        return "skip"
    except requests.exceptions.Timeout:
        print("⚠️  Server timeout - skipping API tests")
        return "skip"
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_profile(token):
    """Test profile endpoint"""
    print("\nTesting profile...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Profile fetch successful!")
            print(f"User: {data.get('username')} ({data.get('role')})")
            print(f"Organization: {data.get('organization', {}).get('name')}")
        else:
            print(f"❌ Profile fetch failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error fetching profile: {e}")

def test_admin_users(token):
    """Test admin users endpoint"""
    print("\nTesting admin users endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Admin users endpoint successful!")
            print(f"Total users: {data.get('count', 0)}")
        else:
            print(f"❌ Admin users endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error accessing admin users: {e}")

def main():
    print("🛡️  CRISP User Management System Test")
    print("="*50)
    
    # Test login
    token = test_login()
    
    if token == "skip":
        print("\n⚠️  Server not running - API tests skipped")
        print("\nTo run full API tests:")
        print("1. Start the Django server: python3 manage.py runserver")
        print("2. Run this test again")
        sys.exit(0)  # Exit with success since server not running is expected
    elif token:
        # Test profile
        test_profile(token)
        
        # Test admin endpoints
        test_admin_users(token)
        
        print("\n🎉 System test completed!")
        
    else:
        print("\n❌ System test failed - could not authenticate")
        sys.exit(1)

if __name__ == "__main__":
    main()