#!/usr/bin/env python3
"""
Simple test runner to identify and fix test issues
"""
import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')

# Setup Django
django.setup()

# Get Django test runner
TestRunner = get_runner(settings)
test_runner = TestRunner()

# Run specific test module to identify issues
if len(sys.argv) > 1:
    test_module = sys.argv[1]
    failures = test_runner.run_tests([test_module])
else:
    # Run all tests
    failures = test_runner.run_tests(["UserManagement"])

if failures:
    print(f"\n❌ {failures} test(s) failed")
    sys.exit(1)
else:
    print("\n✅ All tests passed!")
    sys.exit(0)
