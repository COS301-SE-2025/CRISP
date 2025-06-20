#!/usr/bin/env python3
"""
Check Pi server status and data
"""
import requests
import json

PI_BASE_URL = 'http://100.117.251.119:8001'
PI_USERNAME = 'datadefenders'
PI_PASSWORD = 'DataDefenders123!'

def check_server():
    print("🔍 Checking Pi server status...")
    
    # Test basic connectivity
    try:
        response = requests.get(f'{PI_BASE_URL}/admin/', timeout=5)
        print(f"✅ Pi server is accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Pi server not accessible: {e}")
        return False
    
    # Test authentication
    try:
        login_data = {'username': PI_USERNAME, 'password': PI_PASSWORD}
        response = requests.post(f'{PI_BASE_URL}/api/auth/login/', json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authentication successful")
            print(f"   User: {data.get('user', {}).get('username')}")
            print(f"   Role: {data.get('user', {}).get('role')}")
            
            # Check available endpoints
            token = data.get('token')
            headers = {'Authorization': f'Bearer {token}'}
            
            endpoints = [
                '/api/organizations/',
                '/api/threat-feeds/',
                '/api/indicators/'
            ]
            
            for endpoint in endpoints:
                try:
                    resp = requests.get(f'{PI_BASE_URL}{endpoint}', headers=headers, timeout=5)
                    count = 0
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, list):
                            count = len(data)
                        elif isinstance(data, dict) and 'results' in data:
                            count = len(data['results'])
                    print(f"   {endpoint}: {resp.status_code} ({count} items)")
                except Exception as e:
                    print(f"   {endpoint}: Error - {e}")
            
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

if __name__ == '__main__':
    check_server()
