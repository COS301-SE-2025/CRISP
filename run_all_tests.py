#!/usr/bin/env python3
"""
CRISP Complete Test Suite
Run all tests and verify system functionality
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test(test_name, test_command):
    """Run a test and show the result"""
    print(f"🧪 Testing: {test_name}")
    print(f"Command: {test_command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(test_command, shell=True, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"✅ {test_name} - PASSED")
            return True
        else:
            print(f"❌ {test_name} - FAILED")
            return False
    except Exception as e:
        print(f"❌ {test_name} - ERROR: {e}")
        return False
    finally:
        print()

def main():
    """Run all tests"""
    print("🧪 CRISP COMPLETE TEST SUITE")
    print("=" * 60)
    print()
    
    passed = 0
    total = 0
    
    tests = [
        ("Core Anonymization", "python3 core/tests/test_anonymization.py"),
        ("STIX Anonymization", "python3 core/tests/test_stix_anonymization.py"),
        ("STIX 2.0 Anonymization", "python3 core/tests/test_stix_2_0_anonymization.py"),
        ("Anonymization Strategies", "python3 core/tests/test_strategies.py"),
        ("Import Verification", "python3 core/tests/test_import_verification.py"),
        ("STIX Custom Tool", "python3 core/tests/test_stix_custom.py --trust medium"),
    ]
    
    print("📋 Running Core Tests...")
    print("=" * 40)
    
    for test_name, command in tests:
        total += 1
        if run_test(test_name, command):
            passed += 1
    
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Core anonymization system: Working")
        print("✅ STIX 2.0/2.1 support: Working") 
        print("✅ Observer pattern integration: Working")
        print("✅ File structure: Complete")
        print("✅ Import system: Functional")
        print()
        print("🚀 System is ready for deployment!")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)