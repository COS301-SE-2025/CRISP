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

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'celery',
    
    # Publication System (core)
    'core',
    
    # Trust Users System - Use AppConfig classes to get custom labels
    'core_ut.user_management.apps_ut.UserManagementConfig',
    'core_ut.trust.apps_ut.TrustConfig', 
    'core_ut.alerts.apps_ut.AlertsConfig',
    
    # Trust system integration
    'core_ut.trust',
    'core_ut.user_management',
    'core_ut.alerts',
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Unified authentication middleware (CRITICAL: Must be after AuthenticationMiddleware)
    'core.middleware.unified_auth_middleware.UnifiedAuthenticationMiddleware',
    
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom CRISP middleware (from Trust Users)
    # 'core_ut.middleware.audit_middleware.AuditMiddleware',  # Enable after testing
    
    # Trust system audit middleware
    'core_ut.middleware.audit_middleware.AuditMiddleware',
]

ROOT_URLCONF = 'crisp_settings.urls'

# Custom User Model (from Trust Users System)
AUTH_USER_MODEL = 'ut_user_management.CustomUser'

# Custom user model from Trust system
AUTH_USER_MODEL = 'user_management.CustomUser'

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

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'crisp_unified'),
        'USER': os.getenv('DB_USER', 'crisp_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'your_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
        'CONN_MAX_AGE': 60,
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# REST FRAMEWORK & AUTHENTICATION CONFIGURATION
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
    'JSON_ENCODER': 'django.core.serializers.json.DjangoJSONEncoder',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Note: UUID JWT fix will be applied in the auth service

# JWT Configuration (from Trust Users System)
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
    
    # Custom token class to handle UUID serialization
    'TOKEN_CLASS': 'core.middleware.jwt_serializers.UUIDSafeRefreshToken',
    
    # Use custom serializer to handle UUID fields
    'TOKEN_OBTAIN_SERIALIZER': 'core.middleware.jwt_serializers.UnifiedTokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
    
    # JSON encoder for UUID handling - use a more explicit UUID-safe encoder
    'JSON_ENCODER': 'core.middleware.jwt_serializers.UUIDEncoder',
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
# CORS CONFIGURATION
# =============================================================================

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 
    'http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174'
).split(',')

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only in debug mode

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding', 
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174", 
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]


# =============================================================================
# CELERY CONFIGURATION (for Publication System background tasks)
# =============================================================================

CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# =============================================================================
# TAXII CONFIGURATION (for Publication System)
# =============================================================================

TAXII_SETTINGS = {
    'DISCOVERY_TITLE': os.getenv('TAXII_SERVER_TITLE', 'CRISP Threat Intelligence Platform'),
    'DISCOVERY_DESCRIPTION': os.getenv('TAXII_SERVER_DESCRIPTION', 'Educational threat intelligence sharing platform'),
    'DISCOVERY_CONTACT': os.getenv('TAXII_CONTACT_EMAIL', 'admin@example.com'),
    'MEDIA_TYPE_TAXII': 'application/taxii+json;version=2.1',
    'MEDIA_TYPE_STIX': 'application/stix+json;version=2.1',
    'API_VERSION': '2.1',
    'MAX_CONTENT_LENGTH': 10 * 1024 * 1024,  # 10MB
    'DEFAULT_PAGE_SIZE': 100,
    'MAX_PAGE_SIZE': 1000,
}

# Celery Configuration (for background tasks)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'