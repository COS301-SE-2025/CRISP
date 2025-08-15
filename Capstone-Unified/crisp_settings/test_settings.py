from .settings import *
import tempfile
import os

# Use PostgreSQL test database for complete isolation
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('TEST_DB_NAME', 'test_crisp_unified'),
        'USER': os.getenv('DB_USER', 'admin'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'AdminPassword'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'TEST': {
            'NAME': 'test_crisp_unified_temp',
        },
        'OPTIONS': {
            'connect_timeout': 60,
        },
        'CONN_MAX_AGE': 60,
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
TEST_RUNNER = 'crisp_settings.main_test_runner.CRISPTestOrchestrator'