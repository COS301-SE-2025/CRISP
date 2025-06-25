#!/usr/bin/env python
"""
Trust Management - Unified Test Runner
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
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

import django
django.setup()

def run_django_tests(verbosity=1, pattern=None, failfast=False):
    """Run Django unit tests"""
    print("=" * 80)
    print("RUNNING DJANGO UNIT TESTS")
    print("=" * 80)
    
    cmd = ["python3", "manage.py", "test", f"--verbosity={verbosity}", "--settings=test_settings"]
    
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

def run_database_verification():
    """Run database configuration verification"""
    print("=" * 80)
    print("RUNNING DATABASE VERIFICATION")
    print("=" * 80)
    
    result = subprocess.run(["python3", "tests/verify_postgresql.py"], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_trust_services_tests():
    """Run trust services specific tests"""
    print("=" * 80)
    print("RUNNING TRUST SERVICES TESTS")
    print("=" * 80)
    
    result = subprocess.run([
        "python3", "manage.py", "test", "TrustManagement.tests.test_trust_services", 
        "--verbosity=2", "--settings=test_settings"
    ], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_trust_models_tests():
    """Run trust models specific tests"""
    print("=" * 80)
    print("RUNNING TRUST MODELS TESTS")
    print("=" * 80)
    
    result = subprocess.run([
        "python3", "manage.py", "test", "TrustManagement.tests.test_trust_models",
        "--verbosity=2", "--settings=test_settings"
    ], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_access_control_tests():
    """Run access control tests"""
    print("=" * 80)
    print("RUNNING ACCESS CONTROL TESTS")
    print("=" * 80)
    
    result = subprocess.run([
        "python3", "manage.py", "test", "TrustManagement.tests.test_access_control",
        "--verbosity=2", "--settings=test_settings"
    ], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_management_commands_tests():
    """Run management commands tests"""
    print("=" * 80)
    print("RUNNING MANAGEMENT COMMANDS TESTS")
    print("=" * 80)
    
    try:
        # Test setup_trust command
        result1 = subprocess.run([
            "python3", "manage.py", "setup_trust", "--create-defaults"
        ], cwd=PROJECT_ROOT, capture_output=True, text=True)
        
        # Test manage_trust command
        result2 = subprocess.run([
            "python3", "manage.py", "manage_trust", "list-relationships"
        ], cwd=PROJECT_ROOT, capture_output=True, text=True)
        
        # Test audit_trust command
        result3 = subprocess.run([
            "python3", "manage.py", "audit_trust", "--report-type", "summary"
        ], cwd=PROJECT_ROOT, capture_output=True, text=True)
        
        all_passed = (result1.returncode == 0 and 
                     result2.returncode == 0 and 
                     result3.returncode == 0)
        
        if all_passed:
            print("✅ All management commands working")
        else:
            print("❌ Some management commands failed")
            if result1.returncode != 0:
                print(f"setup_trust failed: {result1.stderr}")
            if result2.returncode != 0:
                print(f"manage_trust failed: {result2.stderr}")
            if result3.returncode != 0:
                print(f"audit_trust failed: {result3.stderr}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Management commands test failed: {e}")
        return False

def run_deployment_check():
    """Run deployment security check"""
    print("=" * 80)
    print("RUNNING DEPLOYMENT SECURITY CHECK")
    print("=" * 80)
    
    result = subprocess.run(["python3", "manage.py", "check", "--deploy"], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_api_tests():
    """Run API endpoint tests"""
    print("=" * 80)
    print("RUNNING API ENDPOINT TESTS")
    print("=" * 80)
    
    # Run integration tests that cover API endpoints
    result = subprocess.run([
        "python3", "manage.py", "test", "TrustManagement.tests.test_trust_integration",
        "--verbosity=2", "--settings=test_settings"
    ], cwd=PROJECT_ROOT)
    return result.returncode == 0

def run_migration_tests():
    """Test database migrations"""
    print("=" * 80)
    print("RUNNING MIGRATION TESTS")
    print("=" * 80)
    
    try:
        # Test migration creation (dry run)
        result1 = subprocess.run([
            "python3", "manage.py", "makemigrations", "--dry-run", "--verbosity=2"
        ], cwd=PROJECT_ROOT, capture_output=True, text=True)
        
        # Test migration application
        result2 = subprocess.run([
            "python3", "manage.py", "migrate", "--verbosity=2"
        ], cwd=PROJECT_ROOT, capture_output=True, text=True)
        
        success = result1.returncode == 0 and result2.returncode == 0
        
        if success:
            print("✅ Migration tests passed")
        else:
            print("❌ Migration tests failed")
            if result1.returncode != 0:
                print(f"makemigrations failed: {result1.stderr}")
            if result2.returncode != 0:
                print(f"migrate failed: {result2.stderr}")
        
        return success
        
    except Exception as e:
        print(f"❌ Migration tests failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Trust Management Test Runner")
    parser.add_argument("--django", action="store_true", help="Run Django unit tests only")
    parser.add_argument("--functionality", action="store_true", help="Run functionality tests only")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive tests only")
    parser.add_argument("--database", action="store_true", help="Run database verification only")
    parser.add_argument("--services", action="store_true", help="Run trust services tests only")
    parser.add_argument("--models", action="store_true", help="Run trust models tests only")
    parser.add_argument("--access-control", action="store_true", help="Run access control tests only")
    parser.add_argument("--management", action="store_true", help="Run management commands tests only")
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument("--migrations", action="store_true", help="Run migration tests only")
    parser.add_argument("--deployment", action="store_true", help="Run deployment check only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--fast", action="store_true", help="Run essential tests only (Django + functionality)")
    parser.add_argument("--core", action="store_true", help="Run core tests (Django + functionality + PostgreSQL)")
    parser.add_argument("--pattern", help="Test pattern for Django tests")
    parser.add_argument("--verbosity", type=int, default=1, choices=[0, 1, 2], help="Test verbosity level")
    parser.add_argument("--failfast", action="store_true", help="Stop on first test failure")
    
    args = parser.parse_args()
    
    # Track test results
    results = []
    
    # Determine which tests to run
    if args.all:
        tests_to_run = [
            'database', 'django', 'models', 'services', 'access-control',
            'functionality', 'comprehensive', 'api', 'management', 'migrations', 'deployment'
        ]
    elif args.fast:
        tests_to_run = ['database', 'django', 'functionality']
    elif args.core:
        tests_to_run = ['database', 'django', 'functionality', 'models', 'services']
    else:
        tests_to_run = []
        if args.database:
            tests_to_run.append('database')
        if args.django:
            tests_to_run.append('django')
        if args.models:
            tests_to_run.append('models')
        if args.services:
            tests_to_run.append('services')
        if args.access_control:
            tests_to_run.append('access-control')
        if args.functionality:
            tests_to_run.append('functionality')
        if args.comprehensive:
            tests_to_run.append('comprehensive')
        if args.api:
            tests_to_run.append('api')
        if args.management:
            tests_to_run.append('management')
        if args.migrations:
            tests_to_run.append('migrations')
        if args.deployment:
            tests_to_run.append('deployment')
        
        # If no specific tests selected, run core tests
        if not tests_to_run:
            tests_to_run = ['database', 'django', 'functionality']
    
    print(f"Running tests: {', '.join(tests_to_run)}")
    print()
    
    # Run selected tests
    if 'database' in tests_to_run:
        success = run_database_verification()
        results.append(('Database Verification', success))
        print()
    
    if 'django' in tests_to_run:
        success = run_django_tests(args.verbosity, args.pattern, args.failfast)
        results.append(('Django Unit Tests', success))
        print()
    
    if 'models' in tests_to_run:
        success = run_trust_models_tests()
        results.append(('Trust Models Tests', success))
        print()
    
    if 'services' in tests_to_run:
        success = run_trust_services_tests()
        results.append(('Trust Services Tests', success))
        print()
    
    if 'access-control' in tests_to_run:
        success = run_access_control_tests()
        results.append(('Access Control Tests', success))
        print()
    
    if 'functionality' in tests_to_run:
        success = run_functionality_tests()
        results.append(('Functionality Tests', success))
        print()
    
    if 'comprehensive' in tests_to_run:
        success = run_comprehensive_tests()
        results.append(('Comprehensive Tests', success))
        print()
    
    if 'api' in tests_to_run:
        success = run_api_tests()
        results.append(('API Tests', success))
        print()
    
    if 'management' in tests_to_run:
        success = run_management_commands_tests()
        results.append(('Management Commands', success))
        print()
    
    if 'migrations' in tests_to_run:
        success = run_migration_tests()
        results.append(('Migration Tests', success))
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
        print("\nTroubleshooting:")
        print("1. Ensure database is properly configured and accessible")
        print("2. Check database credentials in environment variables")
        print("3. Verify all dependencies are installed (pip install -r requirements.txt)")
        print("4. Run 'python manage.py migrate --settings=test_settings' to ensure database schema is up to date")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        print("Trust Management system is ready for production!")
        sys.exit(0)

if __name__ == "__main__":
    main()