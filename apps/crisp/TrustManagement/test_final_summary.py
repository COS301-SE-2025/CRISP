#!/usr/bin/env python3
"""
CRISP User Management - Final Test Summary
"""

import sys
import subprocess
import time

def run_test_and_report(test_name, script_name):
    """Run a test and report results"""
    print(f"\n🔄 Running {test_name}...")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ {test_name}: PASSED")
            return True
        else:
            print(f"❌ {test_name}: FAILED")
            if result.stdout:
                print("Output:", result.stdout[-200:])  # Show last 200 chars
            if result.stderr:
                print("Error:", result.stderr[-200:])
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  {test_name}: TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {test_name}: ERROR - {e}")
        return False

def main():
    print("🛡️ CRISP User Management - Final Test Summary")
    print("=" * 60)
    
    # Prepare environment
    print("🧹 Preparing test environment...")
    try:
        subprocess.run([sys.executable, "create_admin_user.py"], 
                      capture_output=True, timeout=10)
        subprocess.run([sys.executable, "clear_all_rate_limits.py"], 
                      capture_output=True, timeout=15)
        print("✅ Environment prepared")
    except:
        print("⚠️  Environment preparation had issues")
    
    # Test suite
    tests = [
        ("Server Connectivity", "test_server.py"),
        ("Admin Functionality", "test_admin_simple.py"),
        ("Basic System Test", "basic_system_test.py"),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, script in tests:
        if run_test_and_report(test_name, script):
            passed += 1
        time.sleep(2)  # Small delay between tests
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    success_rate = (passed / total) * 100
    
    print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ System is fully operational")
        print("✅ Admin privileges are working")
        print("✅ API endpoints are accessible")
        return 0
    else:
        failed = total - passed
        print(f"⚠️  {failed} test(s) failed")
        print("❌ Some functionality may not be working correctly")
        return 1

if __name__ == "__main__":
    sys.exit(main())
