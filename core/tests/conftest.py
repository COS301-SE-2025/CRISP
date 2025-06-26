import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def pytest_configure():
    """Configure Django settings for pytest"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
    django.setup()

def pytest_runtest_setup(item):
    """Setup for each test"""
    pass