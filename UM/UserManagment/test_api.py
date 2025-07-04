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
        self.rate_limit_detected = False
        
    def clear_rate_limits(self):
        """Attempt to clear rate limits before testing"""
        try:
            import os
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
            import django
            django.setup()
            from django.core.cache import cache
            from UserManagement.models import CustomUser, Organization
            
            # Clear all caches
            cache.clear()
            
            # Clear specific rate limit keys more thoroughly
            current_time = int(time.time())
            time_window = current_time // 300  # 5 minute windows
            
            # Clear multiple time windows
            for i in range(-3, 4):  # Clear 3 windows before and after current
                window = time_window + i
                keys_to_clear = [
                    f'ratelimit:login:127.0.0.1:{window}',
                    f'ratelimit:api:127.0.0.1:{window}',
                    f'ratelimit:password_reset:127.0.0.1:{window}',
                    f'rl:login:127.0.0.1:{window}',
                    f'rl:api:127.0.0.1:{window}',
                ]
                for key in keys_to_clear:
                    cache.delete(key)
            
            # Ensure admin test user exists with proper permissions
            try:
                # Get or create test organization
                test_org, created = Organization.objects.get_or_create(
                    name='Admin Test Organization',
                    defaults={
                        'description': 'Test organization for admin functionality testing',
                        'domain': 'admintest.example.com',
                        'is_active': True
                    }
                )
                
                # Get or create admin test user
                admin_user, created = CustomUser.objects.get_or_create(
                    username='admin_test_user',
                    defaults={
                        'email': 'admin@admintest.example.com',
                        'organization': test_org,
                        'role': 'BlueVisionAdmin',  # Use the correct system admin role
                        'is_verified': True,
                        'is_active': True,
                        'is_staff': True,
                        'is_superuser': True
                    }
                )
                
                # Always update the user to ensure correct role and permissions
                admin_user.role = 'BlueVisionAdmin'
                admin_user.set_password('AdminTestPass123!')
                admin_user.account_locked_until = None
                admin_user.login_attempts = 0
                admin_user.failed_login_attempts = 0
                admin_user.is_verified = True
                admin_user.is_active = True
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()
                
                print("🧹 Cleared rate limiting cache and setup admin user")
                
            except Exception as e:
                print(f"⚠️  Could not setup admin user: {e}")
                
        except Exception as e:
            print(f"⚠️  Could not clear cache: {e}")
    
    def check_rate_limit_status(self):
        """Check if we're currently rate limited"""
        try:
            url = f"{BASE_URL}/auth/login/"
            # Try a simple request to see if we get rate limited
            response = self.session.post(url, json={"username": "test_check", "password": "test_check"})
            if response.status_code == 429:
                self.rate_limit_detected = True
                print("⚠️  Rate limiting detected. Will adjust test strategy.")
                return True
            return False
        except:
            return False
        
    def print_success(self, message):
        print(f"\033[92m✅ {message}\033[0m")  # Green text
        
    def print_error(self, message):
        print(f"\033[91m❌ {message}\033[0m")  # Red text
        
    def print_info(self, message):
        print(f"\033[94mℹ️  {message}\033[0m")  # Blue text
        
    def test_login(self, username="admin_test_user", password="AdminTestPass123!"):
        """Test user login"""
        self.print_info("Testing user login...")
        
        url = f"{BASE_URL}/auth/login/"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=data)
            
            # Handle rate limiting gracefully
            if response.status_code == 429:
                self.print_info("Rate limiting detected. Clearing cache and retrying...")
                self.clear_rate_limits()
                time.sleep(3)  # Wait a bit longer
                
                # Retry the login
                response = self.session.post(url, json=data)
                
                if response.status_code == 429:
                    # If still rate limited, wait for next time window
                    self.print_info("Still rate limited. Waiting for rate limit window to reset...")
                    time.sleep(15)  # Wait 15 seconds for rate limit to reset
                    response = self.session.post(url, json=data)
                    
                    if response.status_code == 429:
                        # Try one more time with a longer wait
                        self.print_info("Rate limit persists. Waiting longer...")
                        time.sleep(30)  # Wait 30 seconds
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
            elif response.status_code == 429:
                self.print_error("Login still rate limited after multiple retries")
                return False
            else:
                self.print_error(f"Login request failed: {response.status_code}")
                if response.text:
                    self.print_error(f"Response: {response.text[:200]}")
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
            rate_limited = False
            attempts = 0
            max_attempts = 10  # Try up to 10 attempts
            
            # Make invalid login attempts until we hit rate limiting
            for i in range(max_attempts):
                data = {
                    "username": f"invalid{i}",  # Use different usernames
                    "password": "invalid"
                }
                response = self.session.post(url, json=data)
                attempts += 1
                
                if response.status_code == 429:
                    rate_limited = True
                    self.print_success(f"Rate limiting triggered after {attempts} attempts")
                    break
                elif response.status_code in [400, 401]:
                    # Expected response for invalid credentials
                    continue
                else:
                    self.print_error(f"Unexpected response on attempt {i+1}: {response.status_code}")
                    return False
            
            if rate_limited:
                # Rate limiting is working
                return True
            else:
                # If we didn't hit rate limiting, it might be disabled or the limit is very high
                # Check if rate limiting is enabled in settings
                self.print_error(f"Rate limiting not triggered after {max_attempts} attempts")
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
    print("\n\033[1mCRISP User Management API Test Suite\033[0m")
    print("=" * 50)
    
    tester = APITester()
    
    # Clear rate limits before starting
    print("\n🧹 Preparing test environment...")
    tester.clear_rate_limits()
    time.sleep(2)  # Give cache clearing time to take effect
    
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
            time.sleep(1)  # Longer delay between tests to avoid rate limiting
        except Exception as e:
            tester.print_error(f"Test {test_name} crashed: {e}")
    
    print(f"\n\033[1mTest Results: {passed}/{total} tests passed\033[0m")
    
    if passed == total:
        print("\033[92m🎉 All tests passed! The API is working correctly.\033[0m")
        return 0
    else:
        print("\033[91m⚠️  Some tests failed. Check the Django server logs for more details.\033[0m")
        return 1

if __name__ == "__main__":
    sys.exit(main())
