#!/usr/bin/env python
"""
Simple verification script for the last 4 failing tests
"""
import subprocess
import sys

def run_test(test_name):
    """Run a specific test and return True if it passes"""
    cmd = [
        'python3', 'manage.py', 'test', test_name, 
        '--verbosity=0', '--failfast'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"{test_name}: TIMEOUT")
        return False
    except Exception as e:
        print(f"{test_name}: ERROR - {e}")
        return False

def main():
    """Test the 4 specific tests we fixed"""
    tests = [
        'UserManagement.tests.test_middleware.SessionTimeoutMiddlewareTestCase.test_invalid_token_returns_401',
        'UserManagement.tests.test_observers.NewLocationAlertObserverTestCase.test_new_location_detection', 
        'UserManagement.tests.test_observers.SecurityAlertObserverTestCase.test_account_locked_alert',
        'UserManagement.tests.test_observers.SecurityAlertObserverTestCase.test_password_reset_alert'
    ]
    
    print("Verifying the 4 specific tests that were fixed...")
    print("=" * 70)
    
    passed = 0
    total = len(tests)
    
    for i, test in enumerate(tests, 1):
        test_short = test.split('.')[-1]
        print(f"[{i}/{total}] Testing {test_short}...", end=" ")
        
        if run_test(test):
            print("PASS")
            passed += 1
        else:
            print("FAIL")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passing")
    
    if passed == total:
        print("SUCCESS: All target tests are now PASSING!")
        return 0
    else:
        print("Some tests are still failing")
        return 1

if __name__ == '__main__':
    sys.exit(main())
