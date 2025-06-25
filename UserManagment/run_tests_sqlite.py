#!/usr/bin/env python3
"""
Test runner with SQLite database for testing
"""
import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Force test database settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')

# Override database settings for testing
import crisp_project.settings as django_settings
django_settings.DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Setup Django
django.setup()

# Get Django test runner
TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=2, interactive=False)

# Run specific test module to identify issues
if len(sys.argv) > 1:
    test_module = sys.argv[1]
    print(f"Running test module: {test_module}")
    failures = test_runner.run_tests([test_module])
else:
    # Run all tests
    print("Running all UserManagement tests...")
    failures = test_runner.run_tests(["UserManagement"])

if failures:
    print(f"\n❌ {failures} test(s) failed")
    sys.exit(1)
else:
    print("\n✅ All tests passed!")
    sys.exit(0)
