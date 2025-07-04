"""
Django settings for running tests for the trust_management app.
This file is self-contained and does not depend on any external project.
"""

import os

# Basic Django settings
SECRET_KEY = os.getenv('TEST_SECRET_KEY', 'a-test-secret-key-for-trust-management')
DEBUG = True
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core.trust',  # The app being tested
    'core.user_management',  # User management system
    'core.tests',  # Test modules
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'core.trust.urls'  # Point to the app's own urls if they exist for testing

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Use PostgreSQL for tests (consistent with production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('TEST_DB_NAME', 'crisp_trust_test_db'),
        'USER': os.getenv('TEST_DB_USER', 'crisp_user'),
        'PASSWORD': os.getenv('TEST_DB_PASSWORD', 'crisp_password'),
        'HOST': os.getenv('TEST_DB_HOST', 'localhost'),
        'PORT': os.getenv('TEST_DB_PORT', '5432'),
        'TEST': {
            'NAME': os.getenv('TEST_DB_NAME', 'crisp_trust_test_db'),
        }
    }
}

# Disable database migrations for tests for speed
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Cache configuration for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Use the custom user model for tests
AUTH_USER_MODEL = 'user_management.CustomUser'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings for tests
REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}