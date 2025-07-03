#!/usr/bin/env python
"""
Quick verification script for the last 4 failing tests
"""
import os
import sys
import django

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')
django.setup()

import unittest
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test.runner import DiscoverRunner

def run_specific_tests():
    """Run only the 4 tests we fixed"""
    setup_test_environment()
    
    # Create test runner
    runner = DiscoverRunner(verbosity=2, interactive=False, failfast=True)
    
    # Specific tests we fixed
    test_labels = [
        'UserManagement.tests.test_middleware.SessionTimeoutMiddlewareTestCase.test_invalid_token_returns_401',
        'UserManagement.tests.test_observers.NewLocationAlertObserverTestCase.test_new_location_detection', 
        'UserManagement.tests.test_observers.SecurityAlertObserverTestCase.test_account_locked_alert',
        'UserManagement.tests.test_observers.SecurityAlertObserverTestCase.test_password_reset_alert'
    ]
    
    print("Testing the 4 specific tests that were fixed...")
    print("=" * 60)
    
    # Run the tests
    result = runner.run_tests(test_labels)
    
    teardown_test_environment()
    
    if result == 0:
        print("\nAll 4 target tests are now PASSING!")
        print("SUCCESS: The specific failing tests have been fixed.")
    else:
        print(f"\n{result} test(s) still failing")
        print("FAILURE: Some tests still need fixes.")
    
    return result

if __name__ == '__main__':
    exit_code = run_specific_tests()
    sys.exit(exit_code)
