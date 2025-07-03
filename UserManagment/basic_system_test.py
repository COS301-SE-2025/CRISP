#!/usr/bin/env python3
"""
Basic System Test - Tests core functionality without complex unit tests
"""

import requests
import json
import sys

def test_django_setup():
    """Test Django configuration"""
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    
    try:
        import django
        django.setup()
        print("Django setup successful")
        return True
    except Exception as e:
        print(f"Django setup failed: {e}")
        return False

def test_models():
    """Test model imports and basic functionality"""
    try:
        from UserManagement.models import CustomUser, Organization, UserSession, AuthenticationLog
        
        # Check counts
        user_count = CustomUser.objects.count()
        org_count = Organization.objects.count()
        session_count = UserSession.objects.count()
        log_count = AuthenticationLog.objects.count()
        
        print(f"Models functional - Users: {user_count}, Orgs: {org_count}, Sessions: {session_count}, Logs: {log_count}")
        return True
    except Exception as e:
        print(f"Model test failed: {e}")
        return False

def test_authentication_service():
    """Test authentication service"""
    try:
        from UserManagement.services.auth_service import AuthenticationService
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/api/auth/login/')
        request.META['HTTP_USER_AGENT'] = 'TestAgent'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        auth_service = AuthenticationService()
        result = auth_service.authenticate_user(
            username='admin',
            password='admin123',
            request=request
        )
        
        if result['success']:
            print("Authentication service working")
            return True
        else:
            print(f"Authentication failed: {result.get('message')}")
            return False
    except Exception as e:
        print(f"Authentication service test failed: {e}")
        return False

def test_api_login():
    """Test API login endpoint"""
    try:
        url = "http://127.0.0.1:8000/api/auth/login/"
        data = {"username": "admin", "password": "admin123"}
        
        response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if 'tokens' in result and 'access' in result['tokens']:
                print("API login successful")
                return True, result['tokens']['access']
            else:
                print("API login response missing tokens")
                return False, None
        else:
            print(f"API login failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"API login test failed: {e}")
        return False, None

def test_api_profile(token):
    """Test API profile endpoint"""
    try:
        url = "http://127.0.0.1:8000/api/auth/profile/"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"API profile working - User: {result.get('username')}")
            return True
        else:
            print(f"API profile failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"API profile test failed: {e}")
        return False

def test_admin_interface():
    """Test admin interface accessibility"""
    try:
        response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
        
        if response.status_code in [200, 302]:  # 302 = redirect to login
            print("Admin interface accessible")
            return True
        else:
            print(f"Admin interface failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Admin interface test failed: {e}")
        return False

def test_security_headers():
    """Test security headers"""
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
            print("Security headers present")
            return True
        else:
            print(f"Security headers missing ({found_headers}/3)")
            return False
    except Exception as e:
        print(f"Security headers test failed: {e}")
        return False

def main():
    print("🛡️ CRISP User Management - Basic System Test")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Django Setup
    tests_total += 1
    if test_django_setup():
        tests_passed += 1
    
    # Test 2: Models
    tests_total += 1
    if test_models():
        tests_passed += 1
    
    # Test 3: Authentication Service
    tests_total += 1
    if test_authentication_service():
        tests_passed += 1
    
    # Test 4: API Login
    tests_total += 1
    api_success, token = test_api_login()
    if api_success:
        tests_passed += 1
    
    # Test 5: API Profile (only if login worked)
    if api_success and token:
        tests_total += 1
        if test_api_profile(token):
            tests_passed += 1
    
    # Test 6: Admin Interface
    tests_total += 1
    if test_admin_interface():
        tests_passed += 1
    
    # Test 7: Security Headers
    tests_total += 1
    if test_security_headers():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{tests_total} passed")
    success_rate = (tests_passed / tests_total) * 100
    print(f"Success Rate: {success_rate:.1f}%")
    
    if tests_passed == tests_total:
        print("\nAll basic tests passed! System is operational.")
        return 0
    else:
        print(f"\n{tests_total - tests_passed} tests failed. Check server is running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())