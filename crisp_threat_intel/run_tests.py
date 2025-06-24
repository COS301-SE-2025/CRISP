#!/usr/bin/env python
"""
CRISP Threat Intelligence Platform - Unified Test Runner
Run all tests with customizable options and flags.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_threat_intel.settings')

import django
django.setup()

def run_django_tests(verbosity=1, pattern=None, failfast=False):
    """Run Django unit tests"""
    print("=" * 80)
    print("RUNNING DJANGO UNIT TESTS")
    print("=" * 80)
    
    cmd = ["python3", "manage.py", "test", f"--verbosity={verbosity}"]
    
    if pattern:
        cmd.append(pattern)
    
    if failfast:
        cmd.append("--failfast")
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_functionality_tests():
    """Run functionality verification tests"""
    print("=" * 80)
    print("RUNNING FUNCTIONALITY TESTS")
    print("=" * 80)
    
    result = subprocess.run(["python3", "tests/test_functionality.py"], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_comprehensive_tests():
    """Run comprehensive system tests"""
    print("=" * 80)
    print("RUNNING COMPREHENSIVE TESTS")
    print("=" * 80)
    
    result = subprocess.run(["python3", "tests/comprehensive_test.py"], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_postgresql_verification():
    """Run PostgreSQL configuration verification"""
    print("=" * 80)
    print("RUNNING POSTGRESQL VERIFICATION")
    print("=" * 80)
    
    result = subprocess.run(["python3", "tests/verify_postgresql.py"], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_otx_tests():
    """Run OTX integration tests"""
    print("=" * 80)
    print("RUNNING OTX INTEGRATION TESTS")
    print("=" * 80)
    
    result = subprocess.run(["python3", "manage.py", "test_otx_connection"], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_stix_tests():
    """Run comprehensive STIX 2.0/2.1 validation tests"""
    print("=" * 80)
    print("RUNNING STIX VALIDATION TESTS")
    print("=" * 80)
    
    result = subprocess.run(["python3", "run_stix_tests.py"], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_deployment_check():
    """Run deployment security check"""
    print("=" * 80)
    print("RUNNING DEPLOYMENT SECURITY CHECK")
    print("=" * 80)
    
    result = subprocess.run(["python3", "manage.py", "check", "--deploy"], cwd=PROJECT_ROOT)
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="CRISP Test Runner")
    parser.add_argument("--django", action="store_true", help="Run Django unit tests only")
    parser.add_argument("--functionality", action="store_true", help="Run functionality tests only")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive tests only")
    parser.add_argument("--postgresql", action="store_true", help="Run PostgreSQL verification only")
    parser.add_argument("--stix", action="store_true", help="Run STIX 2.0/2.1 validation tests only")
    parser.add_argument("--otx", action="store_true", help="Run OTX integration tests only")
    parser.add_argument("--deployment", action="store_true", help="Run deployment check only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--fast", action="store_true", help="Run essential tests only (Django + functionality)")
    parser.add_argument("--pattern", help="Test pattern for Django tests")
    parser.add_argument("--verbosity", type=int, default=1, choices=[0, 1, 2], help="Test verbosity level")
    parser.add_argument("--failfast", action="store_true", help="Stop on first test failure")
    
    args = parser.parse_args()
    
    # Track test results
    results = []
    
    # Determine which tests to run
    if args.all:
        tests_to_run = ['django', 'functionality', 'comprehensive', 'postgresql', 'stix', 'otx', 'deployment']
    elif args.fast:
        tests_to_run = ['django', 'functionality', 'stix']
    else:
        tests_to_run = []
        if args.django:
            tests_to_run.append('django')
        if args.functionality:
            tests_to_run.append('functionality')
        if args.comprehensive:
            tests_to_run.append('comprehensive')
        if args.postgresql:
            tests_to_run.append('postgresql')
        if args.stix:
            tests_to_run.append('stix')
        if args.otx:
            tests_to_run.append('otx')
        if args.deployment:
            tests_to_run.append('deployment')
        
        # If no specific tests selected, run fast tests
        if not tests_to_run:
            tests_to_run = ['django', 'functionality']
    
    print(f"Running tests: {', '.join(tests_to_run)}")
    print()
    
    # Run selected tests
    if 'django' in tests_to_run:
        success = run_django_tests(args.verbosity, args.pattern, args.failfast)
        results.append(('Django Unit Tests', success))
        print()
    
    if 'functionality' in tests_to_run:
        success = run_functionality_tests()
        results.append(('Functionality Tests', success))
        print()
    
    if 'comprehensive' in tests_to_run:
        success = run_comprehensive_tests()
        results.append(('Comprehensive Tests', success))
        print()
    
    if 'postgresql' in tests_to_run:
        success = run_postgresql_verification()
        results.append(('PostgreSQL Verification', success))
        print()
    
    if 'stix' in tests_to_run:
        success = run_stix_tests()
        results.append(('STIX Validation Tests', success))
        print()
    
    if 'otx' in tests_to_run:
        success = run_otx_tests()
        results.append(('OTX Integration Tests', success))
        print()
    
    if 'deployment' in tests_to_run:
        success = run_deployment_check()
        results.append(('Deployment Check', success))
        print()
    
    # Print summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%" if results else "0%")
    
    # Exit with appropriate code
    if failed > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()