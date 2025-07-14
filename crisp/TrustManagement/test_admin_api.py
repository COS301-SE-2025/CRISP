#!/usr/bin/env python3
"""
Quick admin API test
"""

import requests
import json
import sys

def test_admin_api():
    """Test admin API access"""
    print("Testing admin API access...")
    
    # Step 1: Login as admin
    login_url = "http://127.0.0.1:8000/api/auth/login/"
    login_data = {
        "username": "admin_test_user",
        "password": "AdminTestPass123!"
    }
    
    try:
        print("1. Logging in as admin...")
        response = requests.post(login_url, json=login_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                access_token = result['tokens']['access']
                print(f"✅ Login successful. Role: {result['user']['role']}")
                
                # Step 2: Test admin users list
                print("2. Testing admin users list...")
                admin_url = "http://127.0.0.1:8000/api/admin/users/"
                headers = {"Authorization": f"Bearer {access_token}"}
                
                admin_response = requests.get(admin_url, headers=headers, timeout=10)
                
                if admin_response.status_code == 200:
                    admin_result = admin_response.json()
                    users_count = len(admin_result.get('users', []))
                    print(f"✅ Admin users list retrieved ({users_count} users)")
                    return True
                elif admin_response.status_code == 403:
                    print("❌ Access denied - user doesn't have admin privileges")
                    print(f"Response: {admin_response.text}")
                    return False
                else:
                    print(f"❌ Admin API failed: {admin_response.status_code}")
                    print(f"Response: {admin_response.text}")
                    return False
            else:
                print(f"❌ Login failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Login request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_admin_api()
    sys.exit(0 if success else 1)
