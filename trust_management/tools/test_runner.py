"""
Comprehensive test runner for Trust Management module.
Runs all tests with coverage reporting and performance metrics.
"""
import os
import sys
import django
import subprocess
import time
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.test')

def setup_django():
    """Setup Django for testing."""
    try:
        django.setup()
        print("✓ Django setup complete")
    except Exception as e:
        print(f"✗ Django setup failed: {e}")
        sys.exit(1)

def run_command(command, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    start_time = time.time()
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=False
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✓ {description} completed successfully in {duration:.2f}s")
            if result.stdout:
                print("\nOutput:")
                print(result.stdout)
        else:
            print(f"✗ {description} failed in {duration:.2f}s")
            if result.stderr:
                print("\nError:")
                print(result.stderr)
            if result.stdout:
                print("\nOutput:")
                print(result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ Failed to run {description}: {e}")
        return False

def main():
    """Main test runner function."""
    print("🚀 Starting comprehensive Trust Management test suite")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Setup Django
    setup_django()
    
    # Test commands to run
    test_commands = [
        # 1. Clean previous coverage data
        ("coverage erase", "Cleaning previous coverage data"),
        
        # 2. Run all tests with coverage
        ("coverage run --source=TrustManagement manage.py test TrustManagement.tests", 
         "Running all Trust Management tests with coverage"),
        
        # 3. Run specific test categories
        ("coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_models", 
         "Running model tests"),
        
        ("coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_services", 
         "Running service tests"),
        
        ("coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_api", 
         "Running API tests"),
        
        ("coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_views", 
         "Running view tests"),
        
        ("coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_management_commands", 
         "Running management command tests"),
        
        ("coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_access_control", 
         "Running access control tests"),
        
        ("coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_anonymization", 
         "Running anonymization tests"),
        
        ("coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_utils", 
         "Running utility tests"),
        
        ("coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_integrations", 
         "Running integration tests"),
        
        ("coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_performance", 
         "Running performance tests"),
        
        # 4. Generate coverage reports
        ("coverage combine", "Combining coverage data"),
        
        ("coverage report --show-missing", "Generating coverage report"),
        
        ("coverage html", "Generating HTML coverage report"),
        
        ("coverage xml", "Generating XML coverage report"),
        
        ("coverage json", "Generating JSON coverage report"),
    ]
    
    # Track results
    results = []
    total_start_time = time.time()
    
    for command, description in test_commands:
        success = run_command(command, description)
        results.append((description, success))
    
    total_duration = time.time() - total_start_time
    
    # Print summary
    print(f"\n{'='*80}")
    print("📊 TEST EXECUTION SUMMARY")
    print('='*80)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for description, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:<8} {description}")
    
    print(f"\n📈 Results: {passed} passed, {failed} failed")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    
    # Check coverage threshold
    print(f"\n📋 Coverage Reports Generated:")
    print(f"   • HTML Report: htmlcov/index.html")
    print(f"   • XML Report: coverage.xml")
    print(f"   • JSON Report: coverage.json")
    
    # Final status
    if failed == 0:
        print(f"\n🎉 All tests passed! Coverage reports available.")
        return 0
    else:
        print(f"\n❌ {failed} test commands failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
