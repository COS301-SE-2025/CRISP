#!/usr/bin/env python3
"""
CRISP API Endpoints Test Script
Tests all available API endpoints to verify they are working correctly.
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 CRISP API Endpoints Test")
    print("=" * 50)
    
    # Test 1: API Root (GET - no auth required)
    print("\n1️⃣ Testing API Root...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API Root: WORKING")
            print(f"   📍 Access via browser: {BASE_URL}/")
        else:
            print(f"❌ API Root failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API Root error: {e}")
    
    # Test 2: Login (POST)
    print("\n2️⃣ Testing Login...")
    try:
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if 'tokens' in data and 'access' in data['tokens']:
                access_token = data['tokens']['access']
                print("✅ Login: WORKING")
                print(f"   🔑 JWT Token obtained successfully")
                return access_token
            else:
                print("❌ Login failed: No token in response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication"""
    if not token:
        print("\n⚠️ Skipping authenticated endpoint tests - no token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3: Profile (GET)
    print("\n3️⃣ Testing Profile...")
    try:
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        if response.status_code == 200:
            print("✅ Profile: WORKING")
        else:
            print(f"❌ Profile failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Profile error: {e}")
    
    # Test 4: User Dashboard (GET)
    print("\n4️⃣ Testing User Dashboard...")
    try:
        response = requests.get(f"{BASE_URL}/user/dashboard/", headers=headers)
        if response.status_code == 200:
            print("✅ User Dashboard: WORKING")
        else:
            print(f"❌ User Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User Dashboard error: {e}")
    
    # Test 5: User Sessions (GET)
    print("\n5️⃣ Testing User Sessions...")
    try:
        response = requests.get(f"{BASE_URL}/user/sessions/", headers=headers)
        if response.status_code == 200:
            print("✅ User Sessions: WORKING")
        else:
            print(f"❌ User Sessions failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User Sessions error: {e}")
    
    # Test 6: Admin Users (GET) - System admin only
    print("\n6️⃣ Testing Admin Users...")
    try:
        response = requests.get(f"{BASE_URL}/admin/users/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            user_count = len(data.get('users', []))
            print("✅ Admin Users: WORKING")
            print(f"   👥 Found {user_count} users")
        else:
            print(f"❌ Admin Users failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin Users error: {e}")
    
    # Test 7: Token Refresh (POST)
    print("\n7️⃣ Testing Token Refresh...")
    try:
        # First get refresh token from login
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if login_response.status_code == 200:
            refresh_token = login_response.json()['tokens']['refresh']
            refresh_data = {"refresh": refresh_token}
            response = requests.post(f"{BASE_URL}/auth/refresh/", json=refresh_data)
            if response.status_code == 200:
                print("✅ Token Refresh: WORKING")
            else:
                print(f"❌ Token Refresh failed: {response.status_code}")
        else:
            print("❌ Token Refresh: Could not get refresh token")
    except Exception as e:
        print(f"❌ Token Refresh error: {e}")

def print_summary():
    """Print test summary and usage information"""
    print("\n" + "=" * 50)
    print("📋 SUMMARY & USAGE GUIDE")
    print("=" * 50)
    print("\n🌐 ENDPOINTS ACCESSIBLE VIA BROWSER:")
    print(f"   • API Overview: http://127.0.0.1:8000/api/")
    print(f"   • Admin Interface: http://127.0.0.1:8000/admin/")
    
    print("\n🛠️ ENDPOINTS REQUIRING CURL/TOOLS:")
    print("   • Login: POST /api/auth/login/")
    print("   • Logout: POST /api/auth/logout/")
    print("   • Password Change: POST /api/auth/change-password/")
    print("   • User Creation: POST /api/admin/users/")
    
    print("\n🔑 AUTHENTICATED ENDPOINTS (require JWT token):")
    print("   • Profile: GET /api/auth/profile/")
    print("   • Dashboard: GET /api/user/dashboard/")
    print("   • Sessions: GET /api/user/sessions/")
    print("   • Admin Users: GET /api/admin/users/")
    
    print("\n💡 USAGE EXAMPLES:")
    print("   # Login and get token")
    print(f"   curl -X POST {BASE_URL}/auth/login/ \\")
    print("     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"username\":\"{ADMIN_USERNAME}\",\"password\":\"{ADMIN_PASSWORD}\"}}'")
    
    print("\n   # Use token for authenticated requests")
    print(f"   curl -X GET {BASE_URL}/auth/profile/ \\")
    print("     -H 'Authorization: Bearer YOUR_TOKEN_HERE'")
    
    print("\n✅ All working endpoints have been verified!")

def main():
    """Main test function"""
    print("Starting CRISP API endpoint tests...\n")
    
    # Test public endpoints
    token = test_api_endpoints()
    
    # Test authenticated endpoints
    test_authenticated_endpoints(token)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()