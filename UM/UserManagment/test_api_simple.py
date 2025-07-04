#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple API Test Script
Tests API endpoints without Unicode characters for compatibility.
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_login():
    """Test login endpoint"""
    print("Testing Login...")
    try:
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response keys:", list(data.keys()))
            if 'tokens' in data and 'access' in data['tokens']:
                access_token = data['tokens']['access']
                print("✓ Login successful - JWT token obtained")
                return access_token
            else:
                print("✗ Login failed: No token in response")
                print("Response:", data)
                return None
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None

def test_profile(token):
    """Test profile endpoint"""
    if not token:
        return
    
    print("\nTesting Profile...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✓ Profile endpoint working")
            print("User:", data.get('user', {}).get('username', 'Unknown'))
        else:
            print(f"✗ Profile failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Profile error: {e}")

def test_admin_users(token):
    """Test admin users endpoint"""
    if not token:
        return
    
    print("\nTesting Admin Users List...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/admin/users/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✓ Admin users endpoint working")
            print("Users count:", len(data.get('users', [])))
        else:
            print(f"✗ Admin users failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Admin users error: {e}")

def main():
    """Main test function"""
    print("CRISP API Simple Test")
    print("=" * 30)
    
    # Test login first
    token = test_login()
    
    # Test authenticated endpoints
    test_profile(token)
    test_admin_users(token)
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()
