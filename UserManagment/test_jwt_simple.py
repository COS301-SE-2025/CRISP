#!/usr/bin/env python3
"""
Simple JWT token test without database dependencies
"""

import requests
import json
import sys

def test_login_and_token():
    """Test login and token usage"""
    print("🔐 Testing JWT Token Authentication")
    print("=" * 40)
    
    # Test login first
    login_url = 'http://127.0.0.1:8000/api/auth/login/'
    
    # Get credentials from user
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    login_data = {
        'username': username,
        'password': password
    }
    
    print(f"\n1. Testing login...")
    try:
        response = requests.post(
            login_url,
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   Login successful!")
            print(f"   Response keys: {list(data.keys())}")
            
            # Check token structure
            if 'tokens' in data:
                tokens = data['tokens']
                print(f"   Token keys: {list(tokens.keys())}")
                access_token = tokens.get('access')
                print(f"   Access token (first 50 chars): {access_token[:50]}...")
                
                # Test profile access
                print(f"\n2. Testing profile access with token...")
                profile_url = 'http://127.0.0.1:8000/api/auth/profile/'
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                profile_response = requests.get(profile_url, headers=headers, timeout=10)
                print(f"   Profile status: {profile_response.status_code}")
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("   Profile access successful!")
                    print(f"   User: {profile_data.get('username')}")
                    print(f"   Role: {profile_data.get('role')}")
                    print(f"   Organization: {profile_data.get('organization', {}).get('name', 'N/A')}")
                else:
                    print("   Profile access failed")
                    print(f"   Response: {profile_response.text}")
                
                # Test other endpoints
                print(f"\n3. Testing other endpoints...")
                endpoints = [
                    '/api/user/dashboard/',
                    '/api/user/organization-users/',
                    '/api/admin/users/'
                ]
                
                for endpoint in endpoints:
                    try:
                        resp = requests.get(f'http://127.0.0.1:8000{endpoint}', headers=headers, timeout=10)
                        status = "" if resp.status_code == 200 else ""
                        print(f"   {status} {endpoint}: {resp.status_code}")
                        if resp.status_code != 200:
                            error_data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text
                            print(f"      Error: {error_data}")
                    except Exception as e:
                        print(f"   {endpoint}: Error - {e}")
                
            else:
                print("   No 'tokens' key in response")
                print(f"   Full response: {data}")
        else:
            print(f"   Login failed")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   Connection failed - is the Django server running?")
        return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

if __name__ == '__main__':
    test_login_and_token()