"""
Test settings for Trust Management module.
Uses PostgreSQL ONLY - no SQLite fallback.
"""

from TrustManagement.settings import *
import os

# FORCE PostgreSQL usage - no fallback to SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('TEST_DB_NAME', 'crisp'),
        'USER': os.getenv('DB_USER', 'admin'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'AdminPassword'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
        'TEST': {
            'NAME': f'test_trust_management_{os.getpid()}',
            'CREATE_DB': True,
        },
    }
}

print("🐘 Using PostgreSQL for testing - NO SQLite fallback")

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations for faster test runs
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

# Comment out the line below if you want to test with migrations
# MIGRATION_MODULES = DisableMigrations()

# Test-specific settings
DEBUG = False
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Reduce logging verbosity for tests
LOGGING['loggers']['TrustManagement']['level'] = 'WARNING'

# Test cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Security settings for tests
TRUST_MANAGEMENT_SECRET_KEY = 'test-secret-key-for-hmac-validation-in-trust-management-tests'