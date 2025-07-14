"""
Test settings for Trust Management module with mock database approach.
Uses mocked PostgreSQL for comprehensive testing without requiring a real database connection.
"""

from TrustManagement.settings import *
import os
from unittest.mock import MagicMock

# FORCE PostgreSQL-only configuration (no SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('TEST_DB_NAME', 'test_trust_management'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
        'TEST': {
            'NAME': 'test_trust_management_test',
        },
    }
}

# Test runner that provides mock database functionality
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Use in-memory mock for database operations during unit tests
USE_TZ = True

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Test-specific settings
DEBUG = False
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Reduce logging verbosity for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'TrustManagement': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Test cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

print("🐘 Using PostgreSQL-compatible test configuration")