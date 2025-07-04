#!/usr/bin/env python3
"""
CRISP User Management - Comprehensive Test Suite Runner
Runs all tests with consistent colored formatting
"""

import subprocess
import sys
import time
from test_formatting import TestFormatter

def run_test_script(script_name, description, formatter):
    """Run a test script and capture its output"""
    formatter.print_section(f"Running {description}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Determine if the test passed based on return code
        success = result.returncode == 0
        
        if success:
            formatter.print_test_result(description, True, f"Exit code: {result.returncode}")
        else:
            formatter.print_test_result(description, False, f"Exit code: {result.returncode}")
        
        return success
        
    except subprocess.TimeoutExpired:
        formatter.print_test_result(description, False, "Test timed out after 2 minutes")
        return False
    except Exception as e:
        formatter.print_test_result(description, False, f"Error running test: {e}")
        return False

def main():
    formatter = TestFormatter()
    
    formatter.print_header(
        "CRISP User Management - Comprehensive Test Suite",
        "Running all system tests with colored output"
    )
    
    # Prepare test environment
    try:
        formatter.print_info("Preparing test environment...")
        import subprocess
        result = subprocess.run(
            [sys.executable, "prepare_test_environment.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            formatter.print_info("Test environment prepared successfully")
            if result.stdout:
                print(result.stdout)
        else:
            formatter.print_warning("Test environment preparation had issues")
            if result.stderr:
                print(result.stderr)
                
    except Exception as e:
        formatter.print_warning(f"Could not prepare test environment: {e}")
        
        # Fallback to inline preparation
        try:
            import os
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
            import django
            django.setup()
            from django.core.cache import cache
            from UserManagement.models import CustomUser, Organization
            import time
            
            # Clear all caches thoroughly
            cache.clear()
            
            # Clear specific rate limit keys
            current_time = int(time.time())
            time_window = current_time // 300  # 5 minute windows
            
            # Clear multiple time windows to ensure no residual rate limiting
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
            
            formatter.print_info("Cleared rate limiting cache and specific keys")
            
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
                
                if created:
                    formatter.print_info("Created admin test user with proper permissions")
                else:
                    formatter.print_info("Updated admin test user with proper permissions")
                    
            except Exception as e:
                formatter.print_warning(f"Could not setup admin user: {e}")
                
        except Exception as e:
            formatter.print_warning(f"Fallback preparation failed: {e}")
    
    print()
    
    # Test suite configuration
    tests = [
        ("basic_system_test.py", "Basic System Tests"),
        ("test_admin_functionality.py", "Admin Functionality Tests"),
        ("test_api.py", "API Endpoint Tests"),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    # Run each test with longer delays to avoid rate limiting
    for i, (script, description) in enumerate(tests):
        if run_test_script(script, description, formatter):
            passed_tests += 1
        
        # Add extra delay between test suites to ensure rate limits reset
        if i < len(tests) - 1:  # Don't wait after the last test
            print()
            formatter.print_info("Waiting between test suites to avoid rate limiting...")
            time.sleep(5)  # 5 second delay between suites
        print()  # Add spacing between tests
    
    # Final summary
    formatter.print_section("FINAL TEST SUITE RESULTS")
    
    success_rate = (passed_tests / total_tests) * 100
    
    if passed_tests == total_tests:
        formatter.print_test_result("Overall Test Suite", True, 
                                   f"All {total_tests} test suites passed ({success_rate:.1f}%)")
        formatter.print_info("🎉 All test suites completed successfully!")
        return 0
    else:
        failed_tests = total_tests - passed_tests
        formatter.print_test_result("Overall Test Suite", False,
                                   f"{passed_tests}/{total_tests} test suites passed ({success_rate:.1f}%)")
        formatter.print_error(f"⚠️ {failed_tests} test suite(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
