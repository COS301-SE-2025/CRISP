"""
Django settings for CRISP Trust Management project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-please-change-in-production')

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# For development in Docker/WSL, allow all hosts when DEBUG is True
if DEBUG:
    ALLOWED_HOSTS.append('*')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # CRISP core applications
    'core.trust',
    'core.user_management',
    'core.tests',
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
    
    # CRISP custom middleware
    'core.middleware.audit_middleware.AuditMiddleware',
]

ROOT_URLCONF = 'crisp.TrustManagement.urls'

# Custom user model
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

WSGI_APPLICATION = 'crisp.TrustManagement.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'crisp_trust_db'),
        'USER': os.getenv('DB_USER', 'crisp_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'crisp_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Test configuration
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_DISCOVERY_PATTERNS = ['test*.py', '*_test.py', '*_tests.py']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'login': '5/min'
    }
}

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
            'filename': BASE_DIR / 'crisp' / 'logs' / 'trust_management.log',
            'formatter': 'verbose',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'crisp' / 'logs' / 'audit.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'crisp' / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.trust': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.user_management': {
            'handlers': ['file', 'audit_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.services.audit_service': {
            'handlers': ['audit_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.middleware.audit_middleware': {
            'handlers': ['audit_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# JWT Configuration
from datetime import timedelta

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
    'ISSUER': 'crisp-trust-management',
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only allow all origins in development

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session Configuration
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE_SECONDS', '3600'))  # 1 hour

# CSRF Configuration
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'crisp_trust',
        'TIMEOUT': 300,
    } if os.getenv('REDIS_URL') else {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'crisp-trust-cache',
    }
}

# Email Configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@crisp-trust.example.com')

# CRISP Trust Management System Configuration
CRISP_SETTINGS = {
    # Trust system configuration
    'TRUST_SYSTEM': {
        'DEFAULT_TRUST_LEVEL': 'restricted',
        'AUTO_APPROVE_TRUST_RELATIONSHIPS': False,
        'TRUST_RELATIONSHIP_EXPIRY_DAYS': int(os.getenv('TRUST_RELATIONSHIP_EXPIRY_DAYS', '365')),
        'MAX_TRUST_GROUPS_PER_ORG': int(os.getenv('MAX_TRUST_GROUPS_PER_ORG', '10')),
        'ENABLE_TRUST_INHERITANCE': True,
    },
    
    # User management configuration
    'USER_MANAGEMENT': {
        'REQUIRE_EMAIL_VERIFICATION': True,
        'PASSWORD_RESET_TIMEOUT_DAYS': 1,
        'ACCOUNT_LOCKOUT_THRESHOLD': int(os.getenv('ACCOUNT_LOCKOUT_THRESHOLD', '5')),
        'ACCOUNT_LOCKOUT_DURATION_MINUTES': int(os.getenv('ACCOUNT_LOCKOUT_DURATION_MINUTES', '30')),
        'ENABLE_TWO_FACTOR_AUTH': True,
        'REQUIRE_STRONG_PASSWORDS': True,
        'PASSWORD_HISTORY_COUNT': 5,
        'TRUSTED_DEVICE_EXPIRY_DAYS': int(os.getenv('TRUSTED_DEVICE_EXPIRY_DAYS', '30')),
    },
    
    # Security configuration
    'SECURITY': {
        'ENABLE_AUDIT_LOGGING': True,
        'AUDIT_LOG_RETENTION_DAYS': int(os.getenv('AUDIT_LOG_RETENTION_DAYS', '90')),
        'ENABLE_RATE_LIMITING': True,
        'ENABLE_IP_WHITELISTING': False,
        'ALLOWED_IP_RANGES': os.getenv('ALLOWED_IP_RANGES', '').split(',') if os.getenv('ALLOWED_IP_RANGES') else [],
        'ENABLE_GEOLOCATION_BLOCKING': False,
        'BLOCKED_COUNTRIES': os.getenv('BLOCKED_COUNTRIES', '').split(',') if os.getenv('BLOCKED_COUNTRIES') else [],
    },
    
    # API configuration
    'API': {
        'ENABLE_API_VERSIONING': True,
        'DEFAULT_API_VERSION': 'v1',
        'ENABLE_API_DOCUMENTATION': DEBUG,
        'MAX_UPLOAD_SIZE_MB': int(os.getenv('MAX_UPLOAD_SIZE_MB', '50')),
        'ENABLE_BULK_OPERATIONS': True,
        'MAX_BULK_OPERATION_SIZE': int(os.getenv('MAX_BULK_OPERATION_SIZE', '100')),
    },
    
    # Organization configuration
    'ORGANIZATION': {
        'REQUIRE_DOMAIN_VERIFICATION': True,
        'AUTO_CREATE_PUBLISHER_ROLE': True,
        'MAX_USERS_PER_ORG': int(os.getenv('MAX_USERS_PER_ORG', '1000')),
        'ENABLE_ORG_INVITATIONS': True,
        'INVITATION_EXPIRY_DAYS': int(os.getenv('INVITATION_EXPIRY_DAYS', '7')),
    },
    
    # Performance and monitoring
    'PERFORMANCE': {
        'ENABLE_QUERY_OPTIMIZATION': True,
        'ENABLE_CACHING': True,
        'CACHE_TIMEOUT_SECONDS': int(os.getenv('CACHE_TIMEOUT_SECONDS', '300')),
        'ENABLE_METRICS_COLLECTION': True,
        'METRICS_RETENTION_DAYS': int(os.getenv('METRICS_RETENTION_DAYS', '30')),
    }
}

# File Upload Configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * int(float(os.getenv('FILE_UPLOAD_MAX_MEMORY_SIZE_MB', '2.5')))  # 2.5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Internationalization
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')

# Create logs directory if it doesn't exist
logs_dir = BASE_DIR / 'crisp' / 'logs'
logs_dir.mkdir(parents=True, exist_ok=True)