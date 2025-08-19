import os
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Add core patterns to Python path for imports
CORE_PATH = BASE_DIR.parent / 'core'
if str(CORE_PATH) not in sys.path:
    sys.path.append(str(CORE_PATH))

# Add the root directory
ROOT_PATH = BASE_DIR.parent
if str(ROOT_PATH) not in sys.path:
    sys.path.append(str(ROOT_PATH))

env_file = BASE_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-default-key-for-dev')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Custom User Model - CRITICAL: Must be set before any migrations are run
AUTH_USER_MODEL = 'core.CustomUser'

# Security settings
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# SSL Redirect - Set to False for development
SECURE_SSL_REDIRECT = False

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]

# Integrated CRISP applications - threat intel + user/trust management
LOCAL_APPS = [
    'core',
    'core.alerts',
    'core.user_management',
    'core.trust_management',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.audit_middleware.AuditMiddleware',
    'core.middleware.trust_middleware.TrustMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crisp_unified.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'crisp_unified.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'crisp_unified'),
        'USER': os.getenv('DB_USER', 'crisp_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'crisp_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Fallback to SQLite for development if PostgreSQL not available
if os.getenv('USE_SQLITE', 'false').lower() == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'JSON_ENCODER': 'django.core.serializers.json.DjangoJSONEncoder',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '60'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'crisp-unified-platform',
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JSON_ENCODER': 'django.core.serializers.json.DjangoJSONEncoder'
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175').split(',')
CORS_ALLOW_CREDENTIALS = True
# Cache preflight requests for 1 hour to reduce OPTIONS requests
CORS_PREFLIGHT_MAX_AGE = 3600

# Email Configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_TIMEOUT = 30

# Default email settings for CRISP notifications
DEFAULT_FROM_EMAIL = os.getenv('CRISP_SENDER_EMAIL', 'noreply@crisp-system.org')
SERVER_EMAIL = os.getenv('CRISP_SENDER_EMAIL', 'noreply@crisp-system.org')

# TAXII Client Settings
TAXII_DEFAULT_USERNAME = os.getenv('OTX_API_KEY', '')
TAXII_DEFAULT_PASSWORD = 'unused'  # OTX ignores the password field

# OTX Configuration
OTX_SETTINGS = {
    'API_KEY': os.getenv('OTX_API_KEY', ''),
    'ENABLED': os.getenv('OTX_ENABLED', 'True').lower() == 'true',
    'FETCH_INTERVAL': int(os.getenv('OTX_FETCH_INTERVAL', '3600')),
    'BATCH_SIZE': int(os.getenv('OTX_BATCH_SIZE', '10')),  # Reduced from 50 to 10 for faster processing
<<<<<<< Updated upstream
    'MAX_AGE_DAYS': int(os.getenv('OTX_MAX_AGE_DAYS', '2')),  # Changed from 30 to 2 days
=======
    'MAX_AGE_DAYS': int(os.getenv('OTX_MAX_AGE_DAYS', '3')),  # 3 days
>>>>>>> Stashed changes
}

# TAXII Server Configuration
TAXII_SETTINGS = {
    'DISCOVERY_TITLE': os.getenv('TAXII_SERVER_TITLE', 'CRISP Threat Intelligence Platform'),
    'DISCOVERY_DESCRIPTION': os.getenv('TAXII_SERVER_DESCRIPTION', 'Educational threat intelligence sharing platform'),
    'DISCOVERY_CONTACT': os.getenv('TAXII_CONTACT_EMAIL', 'admin@example.com'),
    'MEDIA_TYPE_TAXII': 'application/taxii+json;version=2.1',
    'MEDIA_TYPE_STIX': 'application/stix+json;version=2.1',
    'MAX_CONTENT_LENGTH': 104857600,  # 100MB
    'FILTER_LAST_DAYS': int(os.getenv('TAXII_FILTER_DAYS', 1)),  # Only fetch objects from last 1 day
}

# File Upload Settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB for in-memory uploads
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB for file uploads

# Celery Configuration
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Logging Configuration
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
            'filename': BASE_DIR / 'crisp_unified.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
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
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# CRISP Trust Management System Configuration
CRISP_SETTINGS = {
    # Trust system configuration
    'TRUST_SYSTEM': {
        'DEFAULT_TRUST_LEVEL': os.getenv('DEFAULT_TRUST_LEVEL', 'restricted'),
        'AUTO_APPROVE_TRUST_RELATIONSHIPS': os.getenv('AUTO_APPROVE_TRUST_RELATIONSHIPS', 'False').lower() == 'true',
        'TRUST_RELATIONSHIP_EXPIRY_DAYS': int(os.getenv('TRUST_RELATIONSHIP_EXPIRY_DAYS', '365')),
        'MAX_TRUST_GROUPS_PER_ORG': int(os.getenv('MAX_TRUST_GROUPS_PER_ORG', '10')),
        'ENABLE_TRUST_INHERITANCE': os.getenv('ENABLE_TRUST_INHERITANCE', 'True').lower() == 'true',
    },
    
    # User management configuration
    'USER_MANAGEMENT': {
        'REQUIRE_EMAIL_VERIFICATION': os.getenv('REQUIRE_EMAIL_VERIFICATION', 'True').lower() == 'true',
        'PASSWORD_RESET_TIMEOUT_DAYS': int(os.getenv('PASSWORD_RESET_TIMEOUT_DAYS', '1')),
        'ACCOUNT_LOCKOUT_THRESHOLD': int(os.getenv('ACCOUNT_LOCKOUT_THRESHOLD', '5')),
        'ACCOUNT_LOCKOUT_DURATION_MINUTES': int(os.getenv('ACCOUNT_LOCKOUT_DURATION_MINUTES', '30')),
        'ENABLE_TWO_FACTOR_AUTH': os.getenv('ENABLE_TWO_FACTOR_AUTH', 'True').lower() == 'true',
        'REQUIRE_STRONG_PASSWORDS': os.getenv('REQUIRE_STRONG_PASSWORDS', 'True').lower() == 'true',
        'PASSWORD_HISTORY_COUNT': int(os.getenv('PASSWORD_HISTORY_COUNT', '5')),
        'TRUSTED_DEVICE_EXPIRY_DAYS': int(os.getenv('TRUSTED_DEVICE_EXPIRY_DAYS', '30')),
    },
    
    # Security configuration
    'SECURITY': {
        'ENABLE_AUDIT_LOGGING': os.getenv('ENABLE_AUDIT_LOGGING', 'True').lower() == 'true',
        'AUDIT_LOG_RETENTION_DAYS': int(os.getenv('AUDIT_LOG_RETENTION_DAYS', '90')),
        'ENABLE_RATE_LIMITING': os.getenv('ENABLE_RATE_LIMITING', 'True').lower() == 'true',
        'ENABLE_IP_WHITELISTING': os.getenv('ENABLE_IP_WHITELISTING', 'False').lower() == 'true',
        'ALLOWED_IP_RANGES': os.getenv('ALLOWED_IP_RANGES', '').split(',') if os.getenv('ALLOWED_IP_RANGES') else [],
        'ENABLE_GEOLOCATION_BLOCKING': os.getenv('ENABLE_GEOLOCATION_BLOCKING', 'False').lower() == 'true',
        'BLOCKED_COUNTRIES': os.getenv('BLOCKED_COUNTRIES', '').split(',') if os.getenv('BLOCKED_COUNTRIES') else [],
    },
    
    # API configuration
    'API': {
        'ENABLE_API_VERSIONING': os.getenv('ENABLE_API_VERSIONING', 'True').lower() == 'true',
        'DEFAULT_API_VERSION': os.getenv('DEFAULT_API_VERSION', 'v1'),
        'ENABLE_API_DOCUMENTATION': DEBUG,
        'MAX_UPLOAD_SIZE_MB': int(os.getenv('MAX_UPLOAD_SIZE_MB', '50')),
        'ENABLE_BULK_OPERATIONS': os.getenv('ENABLE_BULK_OPERATIONS', 'True').lower() == 'true',
        'MAX_BULK_OPERATION_SIZE': int(os.getenv('MAX_BULK_OPERATION_SIZE', '100')),
    },
    
    # Organization configuration
    'ORGANIZATION': {
        'REQUIRE_DOMAIN_VERIFICATION': os.getenv('REQUIRE_DOMAIN_VERIFICATION', 'True').lower() == 'true',
        'AUTO_CREATE_PUBLISHER_ROLE': os.getenv('AUTO_CREATE_PUBLISHER_ROLE', 'True').lower() == 'true',
        'MAX_USERS_PER_ORG': int(os.getenv('MAX_USERS_PER_ORG', '1000')),
        'ENABLE_ORG_INVITATIONS': os.getenv('ENABLE_ORG_INVITATIONS', 'True').lower() == 'true',
        'INVITATION_EXPIRY_DAYS': int(os.getenv('INVITATION_EXPIRY_DAYS', '7')),
    },
    
    # Performance and monitoring
    'PERFORMANCE': {
        'ENABLE_QUERY_OPTIMIZATION': os.getenv('ENABLE_QUERY_OPTIMIZATION', 'True').lower() == 'true',
        'ENABLE_CACHING': os.getenv('ENABLE_CACHING', 'True').lower() == 'true',
        'CACHE_TIMEOUT_SECONDS': int(os.getenv('CACHE_TIMEOUT_SECONDS', '300')),
        'ENABLE_METRICS_COLLECTION': os.getenv('ENABLE_METRICS_COLLECTION', 'True').lower() == 'true',
        'METRICS_RETENTION_DAYS': int(os.getenv('METRICS_RETENTION_DAYS', '30')),
    }
}

# File Upload Configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * int(float(os.getenv('FILE_UPLOAD_MAX_MEMORY_SIZE_MB', '2.5')))  # 2.5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Session Configuration
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE_SECONDS', '3600'))  # 1 hour

# Trust Management Secret Key
TRUST_MANAGEMENT_SECRET_KEY = os.getenv('TRUST_MANAGEMENT_SECRET_KEY', SECRET_KEY)