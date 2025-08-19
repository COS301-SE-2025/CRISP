from .settings import *
import tempfile
import os

# Allow testserver for testing
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Disable APPEND_SLASH for tests to prevent URL routing issues
APPEND_SLASH = False

# Use in-memory database for complete isolation
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'NAME': ':memory:',
        }
    }
}

# CRITICAL: Ensure each test gets a completely fresh database
TEST_NON_SERIALIZED_APPS = ['core']
DATABASES['default']['ATOMIC_REQUESTS'] = False

# Use TransactionTestCase by default for better isolation
DEFAULT_TESTCASE_CLASS = 'django.test.TransactionTestCase'

# Speed up testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Test-specific configurations
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable migrations for faster testing
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use the custom test runner that provides better isolation
TEST_RUNNER = 'crisp_unified.main_test_runner.CRISPTestOrchestrator'