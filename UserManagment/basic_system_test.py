#!/usr/bin/env python3
"""
Basic System Test - Tests core functionality without complex unit tests
Enhanced with improved visual formatting for clear pass/fail status
"""

import requests
import json
import sys
import time
from test_formatting import TestFormatter

def test_django_setup(formatter):
    """Test Django configuration"""
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    
    formatter.print_test_start("Django Setup")
    try:
        import django
        django.setup()
        formatter.print_test_result("Django Setup", True, "Django environment configured successfully")
        return True
    except Exception as e:
        formatter.print_test_result("Django Setup", False, f"Django setup failed: {e}")
        return False

def test_models(formatter):
    """Test model imports and basic functionality"""
    formatter.print_test_start("Model Functionality")
    try:
        from UserManagement.models import CustomUser, Organization, UserSession, AuthenticationLog
        
        # Check counts
        user_count = CustomUser.objects.count()
        org_count = Organization.objects.count()
        session_count = UserSession.objects.count()
        log_count = AuthenticationLog.objects.count()
        
        details = f"Users: {user_count}, Organizations: {org_count}, Sessions: {session_count}, Logs: {log_count}"
        formatter.print_test_result("Model Functionality", True, details)
        return True
    except Exception as e:
        formatter.print_test_result("Model Functionality", False, f"Model test failed: {e}")
        return False

def test_authentication_service(formatter):
    """Test authentication service"""
    formatter.print_test_start("Authentication Service")
    try:
        from UserManagement.services.auth_service import AuthenticationService
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/api/auth/login/')
        request.META['HTTP_USER_AGENT'] = 'TestAgent'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        auth_service = AuthenticationService()
        result = auth_service.authenticate_user(
            username='admin_test_user',
            password='AdminTestPass123!',
            request=request
        )
        
        if result['success']:
            formatter.print_test_result("Authentication Service", True, "Authentication service working")
            return True
        else:
            formatter.print_test_result("Authentication Service", False, f"Authentication failed: {result.get('message')}")
            return False
    except Exception as e:
        formatter.print_test_result("Authentication Service", False, f"Authentication service test failed: {e}")
        return False

def test_api_login(formatter):
    """Test API login endpoint"""
    formatter.print_test_start("API Login")
    try:
        # Clear rate limits before testing
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
        import django
        django.setup()
        from django.core.cache import cache
        from UserManagement.models import CustomUser, Organization
        
        # Clear all caches
        cache.clear()
        
        # Clear specific rate limit keys
        current_time = int(time.time())
        time_window = current_time // 300
        
        for i in range(-3, 4):
            window = time_window + i
            keys_to_clear = [
                f'ratelimit:login:127.0.0.1:{window}',
                f'ratelimit:api:127.0.0.1:{window}',
                f'rl:login:127.0.0.1:{window}',
                f'rl:api:127.0.0.1:{window}',
            ]
            for key in keys_to_clear:
                cache.delete(key)
        
        # Ensure admin test user exists with proper permissions
        try:
            test_org, created = Organization.objects.get_or_create(
                name='Admin Test Organization',
                defaults={
                    'description': 'Test organization for admin functionality testing',
                    'domain': 'admintest.example.com',
                    'is_active': True
                }
            )
            
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
            
        except Exception as e:
            print(f"Warning: Could not setup admin user: {e}")
        
        time.sleep(2)  # Give cache clearing time to take effect
        
        url = "http://127.0.0.1:8000/api/auth/login/"
        data = {"username": "admin_test_user", "password": "AdminTestPass123!"}
        
        response = requests.post(url, json=data, timeout=10)
        
        # Handle rate limiting
        if response.status_code == 429:
            time.sleep(5)  # Wait for rate limit to reset
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'tokens' in result and 'access' in result['tokens']:
                formatter.print_test_result("API Login", True, "API login successful")
                return True, result['tokens']['access']
            else:
                formatter.print_test_result("API Login", False, "API login response missing tokens")
                return False, None
        else:
            formatter.print_test_result("API Login", False, f"API login failed: {response.status_code}")
            return False, None
    except Exception as e:
        formatter.print_test_result("API Login", False, f"API login test failed: {e}")
        return False, None

def test_api_profile(token, formatter):
    """Test API profile endpoint"""
    formatter.print_test_start("API Profile")
    try:
        url = "http://127.0.0.1:8000/api/auth/profile/"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            formatter.print_test_result("API Profile", True, f"API profile working - User: {result.get('username')}")
            return True
        else:
            formatter.print_test_result("API Profile", False, f"API profile failed: {response.status_code}")
            return False
    except Exception as e:
        formatter.print_test_result("API Profile", False, f"API profile test failed: {e}")
        return False

def test_admin_interface(formatter):
    """Test admin interface accessibility"""
    formatter.print_test_start("Admin Interface")
    try:
        response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
        
        if response.status_code in [200, 302]:  # 302 = redirect to login
            formatter.print_test_result("Admin Interface", True, "Admin interface accessible")
            return True
        else:
            formatter.print_test_result("Admin Interface", False, f"Admin interface failed: {response.status_code}")
            return False
    except Exception as e:
        formatter.print_test_result("Admin Interface", False, f"Admin interface test failed: {e}")
        return False

def test_security_headers(formatter):
    """Test security headers"""
    formatter.print_test_start("Security Headers")
    try:
        response = requests.get("http://127.0.0.1:8000/api/auth/login/", timeout=5)
        
        security_headers = [
            'X-XSS-Protection',
            'X-Content-Type-Options', 
            'X-Frame-Options'
        ]
        
        found_headers = 0
        for header in security_headers:
            if header in response.headers:
                found_headers += 1
        
        if found_headers >= 3:
            formatter.print_test_result("Security Headers", True, "Security headers present")
            return True
        else:
            formatter.print_test_result("Security Headers", False, f"Security headers missing ({found_headers}/3)")
            return False
    except Exception as e:
        formatter.print_test_result("Security Headers", False, f"Security headers test failed: {e}")
        return False

def main():
    print("🛡️ CRISP User Management - Basic System Test")
    print("=" * 50)
    
    # Initialize formatter
    formatter = TestFormatter()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Django Setup
    tests_total += 1
    if test_django_setup(formatter):
        tests_passed += 1
    
    # Test 2: Models
    tests_total += 1
    if test_models(formatter):
        tests_passed += 1
    
    # Test 3: Authentication Service
    tests_total += 1
    if test_authentication_service(formatter):
        tests_passed += 1
    
    # Test 4: API Login
    tests_total += 1
    api_success, token = test_api_login(formatter)
    if api_success:
        tests_passed += 1
    
    # Test 5: API Profile (only if login worked)
    if api_success and token:
        tests_total += 1
        if test_api_profile(token, formatter):
            tests_passed += 1
    
    # Test 6: Admin Interface
    tests_total += 1
    if test_admin_interface(formatter):
        tests_passed += 1
    
    # Test 7: Security Headers
    tests_total += 1
    if test_security_headers(formatter):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    formatter.print_info("FINAL RESULTS")
    
    success_rate = (tests_passed / tests_total) * 100
    
    if tests_passed == tests_total:
        formatter.print_info(f"✅ ALL TESTS PASSED! ({tests_passed}/{tests_total})")
        formatter.print_info(f"Success Rate: {success_rate:.1f}%")
        formatter.print_info("\n🎉 System is fully operational!")
        return 0
    else:
        formatter.print_error(f"❌ SOME TESTS FAILED ({tests_passed}/{tests_total})")
        formatter.print_warning(f"Success Rate: {success_rate:.1f}%")
        formatter.print_error(f"\n⚠️  {tests_total - tests_passed} tests failed. Check server and credentials.")
        return 1

if __name__ == "__main__":
    sys.exit(main())