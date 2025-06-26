"""
Test settings for CRISP integrated platform
Optimized for fast testing with SQLite and minimal external dependencies
"""

from .settings import *
import tempfile

# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Fast password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable password validation for tests
AUTH_PASSWORD_VALIDATORS = []

# Disable logging during tests to reduce noise
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Disable Celery for tests - run tasks synchronously
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Use locmem cache for tests (needed for rate limiting tests)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

# Test-specific settings
SECRET_KEY = 'test-secret-key-not-for-production'
DEBUG = True
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Disable CORS for tests
CORS_ALLOW_ALL_ORIGINS = True

# Mock external services for tests
OTX_SETTINGS = {
    'API_KEY': 'test-api-key',
    'ENABLED': False,  # Disable external API calls during tests
    'FETCH_INTERVAL': 3600,
    'BATCH_SIZE': 50,
    'MAX_AGE_DAYS': 30,
}

TAXII_SETTINGS = {
    'DISCOVERY_TITLE': 'CRISP Test Server',
    'DISCOVERY_DESCRIPTION': 'Test threat intelligence platform',
    'DISCOVERY_CONTACT': 'test@crisp.test',
    'MEDIA_TYPE_TAXII': 'application/taxii+json;version=2.1',
    'MEDIA_TYPE_STIX': 'application/stix+json;version=2.1',
    'MAX_CONTENT_LENGTH': 104857600,
}

# Test file storage
MEDIA_ROOT = tempfile.mkdtemp()
STATIC_ROOT = tempfile.mkdtemp()

# JWT settings for tests
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
})

# Trust management test settings
TRUST_MANAGEMENT_SECRET_KEY = 'test-trust-management-secret'

# Enable rate limiting for tests (to test the middleware)
RATELIMIT_ENABLE = True