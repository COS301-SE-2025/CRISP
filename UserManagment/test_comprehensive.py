#!/usr/bin/env python3
"""
CRISP User Management - Comprehensive Test Runner
Handles all setup, cache clearing, and test execution
"""

import subprocess
import sys
import time
import os

def setup_environment():
    """Set up the test environment"""
    print("🧹 Setting up test environment...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    
    try:
        # Import Django and setup
        import django
        django.setup()
        
        from django.core.cache import cache
        from UserManagement.models import CustomUser, Organization
        
        # Clear all caches
        cache.clear()
        print("   ✅ Cache cleared")
        
        # Create test organization
        test_org, created = Organization.objects.get_or_create(
            name='Admin Test Organization',
            defaults={
                'description': 'Test organization for admin functionality testing',
                'domain': 'admintest.example.com',
                'is_active': True
            }
        )
        
        # Create/update admin user
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin_test_user',
            defaults={
                'email': 'admin@admintest.example.com',
                'organization': test_org,
                'role': 'BlueVisionAdmin',
                'is_verified': True,
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Always update to ensure correct settings
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
        
        print(f"   ✅ Admin user ready: {admin_user.username} (Role: {admin_user.role})")
        
        # Wait for any processes to settle
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Environment setup failed: {e}")
        return False

def run_individual_test(test_name, test_function):
    """Run an individual test"""
    print(f"\n🔄 Running {test_name}...")
    print("-" * 40)
    
    try:
        result = test_function()
        if result:
            print(f"✅ {test_name}: PASSED")
            return True
        else:
            print(f"❌ {test_name}: FAILED")
            return False
    except Exception as e:
        print(f"💥 {test_name}: ERROR - {e}")
        return False

def test_server_connectivity():
    """Test server connectivity"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
        return response.status_code in [200, 302]
    except:
        return False

def test_admin_login():
    """Test admin login functionality"""
    try:
        import requests
        
        login_url = "http://127.0.0.1:8000/api/auth/login/"
        login_data = {
            "username": "admin_test_user",
            "password": "AdminTestPass123!"
        }
        
        response = requests.post(login_url, json=login_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('success', False)
        else:
            print(f"   Status: {response.status_code}")
            if response.text:
                print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_admin_users_list():
    """Test admin users list access"""
    try:
        import requests
        
        # Login first
        login_url = "http://127.0.0.1:8000/api/auth/login/"
        login_data = {
            "username": "admin_test_user",
            "password": "AdminTestPass123!"
        }
        
        response = requests.post(login_url, json=login_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                access_token = result['tokens']['access']
                
                # Test admin users list
                admin_url = "http://127.0.0.1:8000/api/admin/users/"
                headers = {"Authorization": f"Bearer {access_token}"}
                
                admin_response = requests.get(admin_url, headers=headers, timeout=10)
                
                if admin_response.status_code == 200:
                    admin_result = admin_response.json()
                    users_count = len(admin_result.get('users', []))
                    print(f"   Found {users_count} users")
                    return True
                else:
                    print(f"   Admin API Status: {admin_response.status_code}")
                    return False
            else:
                print(f"   Login failed: {result.get('message')}")
                return False
        else:
            print(f"   Login status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """Main test runner"""
    print("🛡️ CRISP User Management - Comprehensive Test Runner")
    print("=" * 70)
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed. Exiting.")
        return 1
    
    # Define tests
    tests = [
        ("Server Connectivity", test_server_connectivity),
        ("Admin Login", test_admin_login),
        ("Admin Users List", test_admin_users_list),
    ]
    
    # Run tests
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if run_individual_test(test_name, test_func):
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    # Final results
    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS")
    print("=" * 70)
    
    success_rate = (passed / total) * 100
    print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ System is fully operational")
        print("✅ Admin privileges are working correctly")
        print("✅ API endpoints are accessible")
        print("\nYour CRISP User Management system is ready to use!")
        return 0
    else:
        failed = total - passed
        print(f"⚠️  {failed} test(s) failed")
        print("❌ Some functionality may not be working correctly")
        
        if passed > 0:
            print(f"✅ {passed} test(s) are working correctly")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
