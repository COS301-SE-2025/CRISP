#!/usr/bin/env python3
"""
CRISP User Management API Test Script

This script tests the main API endpoints to verify the system is working correctly.
Run this after starting the Django development server.
"""

import requests
import json
import sys
import time

BASE_URL = "http://127.0.0.1:8000/api"

class APITester:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.session = requests.Session()
        
    def print_success(self, message):
        print(f"✅ {message}")
        
    def print_error(self, message):
        print(f"❌ {message}")
        
    def print_info(self, message):
        print(f"ℹ️  {message}")
        
    def test_login(self, username="admin", password="AdminPassword123!"):
        """Test user login"""
        self.print_info("Testing user login...")
        
        url = f"{BASE_URL}/auth/login/"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.access_token = result['tokens']['access']
                    self.refresh_token = result['tokens']['refresh']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    self.print_success("Login successful")
                    self.print_info(f"User: {result['user']['username']} ({result['user']['role']})")
                    return True
                else:
                    self.print_error(f"Login failed: {result.get('message')}")
                    return False
            else:
                self.print_error(f"Login request failed: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to server. Is Django running on port 8000?")
            return False
        except Exception as e:
            self.print_error(f"Login error: {e}")
            return False
    
    def test_profile(self):
        """Test getting user profile"""
        self.print_info("Testing user profile...")
        
        url = f"{BASE_URL}/auth/profile/"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                profile = response.json()
                self.print_success("Profile retrieved successfully")
                self.print_info(f"Profile: {profile['username']} - {profile['email']}")
                return True
            else:
                self.print_error(f"Profile request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Profile error: {e}")
            return False
    
    def test_token_refresh(self):
        """Test token refresh"""
        self.print_info("Testing token refresh...")
        
        url = f"{BASE_URL}/auth/refresh/"
        data = {
            "refresh": self.refresh_token
        }
        
        try:
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    new_access_token = result['tokens']['access']
                    self.session.headers.update({
                        'Authorization': f'Bearer {new_access_token}'
                    })
                    self.print_success("Token refresh successful")
                    return True
                else:
                    self.print_error("Token refresh failed")
                    return False
            else:
                self.print_error(f"Token refresh request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Token refresh error: {e}")
            return False
    
    def test_admin_users_list(self):
        """Test admin users list (requires admin privileges)"""
        self.print_info("Testing admin users list...")
        
        url = f"{BASE_URL}/admin/users/"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                result = response.json()
                users_count = len(result.get('users', []))
                self.print_success(f"Admin users list retrieved ({users_count} users)")
                return True
            elif response.status_code == 403:
                self.print_error("Access denied - user doesn't have admin privileges")
                return False
            else:
                self.print_error(f"Admin users list request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Admin users list error: {e}")
            return False
    
    def test_user_dashboard(self):
        """Test user dashboard"""
        self.print_info("Testing user dashboard...")
        
        url = f"{BASE_URL}/user/dashboard/"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                dashboard = response.json()
                self.print_success("User dashboard retrieved successfully")
                stats = dashboard.get('stats', {})
                self.print_info(f"Stats: {stats.get('total_logins', 0)} logins, {stats.get('active_sessions', 0)} active sessions")
                return True
            else:
                self.print_error(f"User dashboard request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"User dashboard error: {e}")
            return False
    
    def test_rate_limiting(self):
        """Test rate limiting by making multiple invalid login attempts"""
        self.print_info("Testing rate limiting...")
        
        url = f"{BASE_URL}/auth/login/"
        
        # Remove auth header for this test
        temp_headers = self.session.headers.copy()
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        
        try:
            # Make 6 invalid login attempts
            for i in range(6):
                data = {
                    "username": "invalid",
                    "password": "invalid"
                }
                response = self.session.post(url, json=data)
                
                if i < 5:
                    # First 5 should get 401 (invalid credentials)
                    if response.status_code in [400, 401]:
                        continue
                    else:
                        self.print_error(f"Unexpected response on attempt {i+1}: {response.status_code}")
                        return False
                else:
                    # 6th should get 429 (rate limited)
                    if response.status_code == 429:
                        self.print_success("Rate limiting working correctly")
                        return True
                    else:
                        self.print_error(f"Rate limiting not working: got {response.status_code} instead of 429")
                        return False
            
            # Restore headers
            self.session.headers.update(temp_headers)
            return False
            
        except Exception as e:
            self.print_error(f"Rate limiting test error: {e}")
            return False
        finally:
            # Restore headers
            self.session.headers.update(temp_headers)
    
    def test_logout(self):
        """Test user logout"""
        self.print_info("Testing user logout...")
        
        url = f"{BASE_URL}/auth/logout/"
        
        try:
            response = self.session.post(url)
            
            if response.status_code == 200:
                self.print_success("Logout successful")
                return True
            else:
                self.print_error(f"Logout request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Logout error: {e}")
            return False

def main():
    print("🧪 CRISP User Management API Test Suite")
    print("=" * 50)
    
    tester = APITester()
    
    # Test sequence
    tests = [
        ("Login", tester.test_login),
        ("Profile", tester.test_profile),
        ("Token Refresh", tester.test_token_refresh),
        ("User Dashboard", tester.test_user_dashboard),
        ("Admin Users List", tester.test_admin_users_list),
        ("Rate Limiting", tester.test_rate_limiting),
        ("Logout", tester.test_logout),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            tester.print_error(f"Test {test_name} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the Django server logs for more details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())