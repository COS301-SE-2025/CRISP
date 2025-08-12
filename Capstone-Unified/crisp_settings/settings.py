"""
Django settings for CRISP Unified Platform.
Integrates Publication Consumption Anonymization + Trust Users Management.
"""

import os
from pathlib import Path
from datetime import timedelta

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
if load_dotenv:
    load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # Publication System (core) - Main threat intelligence system
    'core',
    
    # Trust Users Management System - Using AppConfig classes with custom labels
    'core_ut.user_management.apps_ut.UserManagementConfig',
    'core_ut.trust.apps_ut.TrustConfig', 
    'core_ut.alerts.apps_ut.AlertsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom CRISP middleware (from Trust Users)
    # 'core_ut.middleware.audit_middleware.AuditMiddleware',  # Enable after testing
]

ROOT_URLCONF = 'crisp_settings.urls'

# Custom User Model (from Trust Users System)
AUTH_USER_MODEL = 'ut_user_management.CustomUser'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'crisp_settings.wsgi.application'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'crisp_unified'),
        'USER': os.getenv('DB_USER', 'crisp_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
        'CONN_MAX_AGE': 60,
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES AND MEDIA
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# CORS CONFIGURATION
# =============================================================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",   # React default
    "http://localhost:5173",   # Publication frontend
    "http://localhost:5174",   # Trust Management frontend
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# REST FRAMEWORK CONFIGURATION
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'JSON_ENCODER': 'django.core.serializers.json.DjangoJSONEncoder',
}

# =============================================================================
# JWT CONFIGURATION (from Trust Users System)
# =============================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '60'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    
    # Custom JSON encoder for UUID handling
    'JSON_ENCODER': 'django.core.serializers.json.DjangoJSONEncoder',
}

# =============================================================================
# EMAIL CONFIGURATION (from Trust Users System)
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('CRISP_SENDER_EMAIL', EMAIL_HOST_USER)

# CRISP-specific email settings
CRISP_SENDER_NAME = os.getenv('CRISP_SENDER_NAME', 'CRISP Threat Intelligence')
CRISP_SENDER_EMAIL = os.getenv('CRISP_SENDER_EMAIL', EMAIL_HOST_USER)

# =============================================================================
# CELERY CONFIGURATION (Publication System)
# =============================================================================

CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# =============================================================================
# PUBLICATION SYSTEM SETTINGS
# =============================================================================

# TAXII Configuration
TAXII_BASE_URL = os.getenv('TAXII_BASE_URL', 'http://localhost:8000/taxii2/')
TAXII_DISCOVERY_PATH = 'discovery/'

# STIX Configuration
STIX_VERSION = '2.1'
DEFAULT_STIX_SOURCES = [
    'internal',
    'otx',
]

# External API Configuration
OTX_API_KEY = os.getenv('OTX_API_KEY', '')
OTX_BASE_URL = 'https://otx.alienvault.com/api/v1/'

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'crisp_unified.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'core_ut': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# =============================================================================
# TESTING CONFIGURATION
# =============================================================================

if 'test' in os.sys.argv:
    # Use in-memory database for testing
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
    
    # Disable migrations during testing for speed
    class DisableMigrations:
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return None
    
    MIGRATION_MODULES = DisableMigrations()

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================

if DEBUG:
    # Create logs directory if it doesn't exist
    os.makedirs(BASE_DIR / 'logs', exist_ok=True)
    
    # Allow all hosts in debug mode
    ALLOWED_HOSTS.append('*')
    
    # Additional CORS origins for development
    CORS_ALLOWED_ORIGINS.extend([
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ])

# =============================================================================
# TAXII SYSTEM CONFIGURATION
# =============================================================================

TAXII_SETTINGS = {
    'MEDIA_TYPE_TAXII': 'application/taxii+json;version=2.1',
    'MEDIA_TYPE_STIX': 'application/stix+json;version=2.1',
    'DISCOVERY_TITLE': 'CRISP TAXII Server',
    'DISCOVERY_DESCRIPTION': 'CRISP Cyber Risk Information Sharing Platform TAXII 2.1 Server',
    'DISCOVERY_CONTACT': os.getenv('TAXII_CONTACT', 'admin@crisp.local'),
    'DEFAULT_MAX_CONTENT_LENGTH': 10485760,  # 10MB
    'API_ROOT_TITLE': 'CRISP Threat Intelligence',
    'API_ROOT_DESCRIPTION': 'Threat intelligence sharing via TAXII 2.1',
    'API_ROOT_VERSIONS': ['2.1'],
    'API_ROOT_MAX_CONTENT_LENGTH': 10485760,
    'COLLECTION_TITLE': 'CRISP Threat Feed',
    'COLLECTION_DESCRIPTION': 'Aggregated threat intelligence from multiple sources',
    'COLLECTION_CAN_READ': True,
    'COLLECTION_CAN_WRITE': True,
    'COLLECTION_MEDIA_TYPES': [
        'application/stix+json;version=2.1',
        'application/json'
    ]
}

# =============================================================================
# CRISP PLATFORM SPECIFIC SETTINGS
# =============================================================================

# Application version
CRISP_VERSION = '1.0.0'

# Feature flags
CRISP_FEATURES = {
    'publication_system': True,
    'trust_management': True,
    'email_alerts': True,
    'audit_logging': True,
    'advanced_analytics': DEBUG,  # Only in development
}

# Trust Management settings
TRUST_DEFAULT_LEVEL = 'MEDIUM'
TRUST_LEVELS = ['NONE', 'LOW', 'MEDIUM', 'HIGH']

# Publication system settings
PUBLICATION_MAX_FEED_SIZE = 1000000  # 1MB
PUBLICATION_BATCH_SIZE = 100