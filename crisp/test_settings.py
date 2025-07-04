from .settings import *

TEST_RUNNER = 'crisp.main_test_runner.CRISPTestOrchestrator'

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Reduce logging verbosity
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'core': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
    },
}

# Speed up password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable debug toolbar
DEBUG = False
DEBUG_TOOLBAR = False

# Disable email sending
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'