import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-z9d&!6rvx0m1k@6uh$#_s&3r_^6b5z-p#-36=(=ug^21&7f*^r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # Restrict in production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oauth2_provider',
    'rest_framework',
    'corsheaders',
    'core',
    'stix_factory',
    'anonymization',
    'taxii_api',
    'trust',
    'audit',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit.middleware.AuditMiddleware',  # Custom audit logging
]

ROOT_URLCONF = 'threat_intel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'threat_intel.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'threat_intel'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
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

# OAuth2 settings
OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 36000,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 36000,
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
    },
    'APPLICATION_MODEL': 'oauth2_provider.Application',
    'ACCESS_TOKEN_MODEL': 'oauth2_provider.AccessToken',
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 600,
    'ROTATE_REFRESH_TOKEN': False,
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# TAXII specific settings
TAXII_SETTINGS = {
    'DISCOVERY_TITLE': 'Educational Threat Intelligence Sharing',
    'DISCOVERY_DESCRIPTION': 'TAXII Server for sharing threat intelligence between educational institutions',
    'DISCOVERY_CONTACT': 'security@example.edu',
    'API_ROOT': '/taxii2/',
    'MAX_CONTENT_LENGTH': 104857600,  # 100MB
    'MEDIA_TYPE_STIX': 'application/stix+json;version=2.1',
    'MEDIA_TYPE_TAXII': 'application/taxii+json;version=2.1',
}

# STIX settings
STIX_SETTINGS = {
    'DEFAULT_IDENTITY': {
        'name': 'Educational Threat Intelligence Sharing Service',
        'identity_class': 'organization',
        'sectors': ['education'],
    },
    'CUSTOM_EXTENSIONS': {},
}

# Anonymization settings
ANONYMIZATION_SETTINGS = {
    'DEFAULT_STRATEGY': 'partial',  # Options: 'none', 'partial', 'full'
    'TARGET_EFFECTIVENESS': 95,  # 95% effectiveness target (SEC1.7)
    'PRESERVED_PATTERNS': [
        # List of patterns to preserve during anonymization
    ],
}

# Trust relationship settings
TRUST_SETTINGS = {
    'TRUST_LEVELS': {
        'high': 1.0,    # No anonymization
        'medium': 0.7,  # Partial anonymization
        'low': 0.4,     # More aggressive anonymization
        'none': 0.0,    # Maximum anonymization
    },
    'DEFAULT_TRUST_LEVEL': 'medium',
}

# Performance settings
PERFORMANCE_SETTINGS = {
    'BULK_PROCESSING_RATE': 100,  # Records per second (P1.6)
    'BATCH_SIZE': 50,
}

# Audit logging settings
AUDIT_SETTINGS = {
    'ENABLED': True,
    'LOG_LEVEL': 'INFO',
    'RETENTION_DAYS': 365,
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False  # Restrict in production
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
    'http://localhost:3000',
]

# Celery settings for background tasks
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE