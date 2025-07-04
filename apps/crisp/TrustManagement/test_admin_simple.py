#!/usr/bin/env python3
"""
Simple admin functionality test
"""

import requests
import json
import sys

def test_admin_functionality():
    """Test admin functionality"""
    print("🔐 Testing Admin Functionality")
    print("=" * 40)
    
    # Test 1: Login as admin
    print("1. Testing admin login...")
    login_url = "http://127.0.0.1:8000/api/auth/login/"
    login_data = {
        "username": "admin_test_user",
        "password": "AdminTestPass123!"
    }
    
    try:
        response = requests.post(login_url, json=login_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                access_token = result['tokens']['access']
                user_role = result['user']['role']
                print(f"   ✅ Admin login successful (Role: {user_role})")
                
                # Test 2: Admin users list
                print("2. Testing admin users list...")
                admin_url = "http://127.0.0.1:8000/api/admin/users/"
                headers = {"Authorization": f"Bearer {access_token}"}
                
                admin_response = requests.get(admin_url, headers=headers, timeout=10)
                
                if admin_response.status_code == 200:
                    admin_result = admin_response.json()
                    users_count = len(admin_result.get('users', []))
                    print(f"   ✅ Admin users list retrieved ({users_count} users)")
                    
                    # Test 3: User profile
                    print("3. Testing user profile...")
                    profile_url = "http://127.0.0.1:8000/api/auth/profile/"
                    profile_response = requests.get(profile_url, headers=headers, timeout=10)
                    
                    if profile_response.status_code == 200:
                        profile = profile_response.json()
                        print(f"   ✅ Profile retrieved: {profile['username']} - {profile['email']}")
                        
                        print("\n" + "=" * 40)
                        print("🎉 All admin functionality tests passed!")
                        return True
                    else:
                        print(f"   ❌ Profile test failed: {profile_response.status_code}")
                        return False
                        
                elif admin_response.status_code == 403:
                    print("   ❌ Access denied - user doesn't have admin privileges")
                    print(f"   Response: {admin_response.text}")
                    return False
                else:
                    print(f"   ❌ Admin API failed: {admin_response.status_code}")
                    return False
            else:
                print(f"   ❌ Login failed: {result.get('message')}")
                return False
        else:
            print(f"   ❌ Login request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_admin_functionality()
    print("\n" + "=" * 40)
    if success:
        print("✅ ADMIN FUNCTIONALITY: WORKING")
    else:
        print("❌ ADMIN FUNCTIONALITY: FAILED")
    
    sys.exit(0 if success else 1)
