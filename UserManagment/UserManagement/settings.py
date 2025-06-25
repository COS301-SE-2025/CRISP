"""
Django settings for CRISP User Management

This file contains the settings specific to the UserManagement app
that should be integrated into the main CRISP project settings.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# User Management specific settings
USER_MANAGEMENT_SETTINGS = {
    # Custom User Model
    'AUTH_USER_MODEL': 'UserManagement.CustomUser',
    
    # Password Validation
    'AUTH_PASSWORD_VALIDATORS': [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {'min_length': 12,}
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
        {
            'NAME': 'UserManagement.validators.CustomPasswordValidator',
            'OPTIONS': {
                'min_uppercase': 1,
                'min_lowercase': 1,
                'min_digits': 2,
                'min_special': 1,
            }
        }
    ],
    
    # JWT Configuration
    'SIMPLE_JWT': {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', 60))),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', 7))),
        'ROTATE_REFRESH_TOKENS': True,
        'BLACKLIST_AFTER_ROTATION': True,
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': os.getenv('JWT_SECRET_KEY', 'crisp-jwt-secret-key-change-in-production'),
        'AUTH_HEADER_TYPES': ('Bearer',),
        'USER_ID_FIELD': 'id',
        'USER_ID_CLAIM': 'user_id',
        'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
        'TOKEN_TYPE_CLAIM': 'token_type',
    },
    
    # Database Configuration
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'crisp'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {
                'options': '-c default_transaction_isolation=serializable'
            }
        }
    },
    
    # Security Settings
    'SECURITY_HEADERS': {
        'X_XSS_PROTECTION': '1; mode=block',
        'X_CONTENT_TYPE_OPTIONS': 'nosniff',
        'X_FRAME_OPTIONS': 'DENY',
        'REFERRER_POLICY': 'strict-origin-when-cross-origin',
        'CONTENT_SECURITY_POLICY': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "object-src 'none'; "
            "media-src 'self'; "
            "frame-src 'none';"
        )
    },
    
    # Session Security
    'SESSION_SECURITY': {
        'SESSION_COOKIE_SECURE': not bool(os.getenv('DEBUG', 'False').lower() == 'true'),
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Strict',
        'CSRF_COOKIE_SECURE': not bool(os.getenv('DEBUG', 'False').lower() == 'true'),
        'SECURE_BROWSER_XSS_FILTER': True,
        'SECURE_CONTENT_TYPE_NOSNIFF': True,
        'SECURE_HSTS_SECONDS': 31536000 if not bool(os.getenv('DEBUG', 'False').lower() == 'true') else 0,
        'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
        'SECURE_HSTS_PRELOAD': True,
    },
    
    # Rate Limiting
    'RATE_LIMITING': {
        'ENABLE': bool(os.getenv('RATELIMIT_ENABLE', 'True').lower() == 'true'),
        'LOGIN_ATTEMPTS': int(os.getenv('LOGIN_ATTEMPTS_LIMIT', 5)),
        'PASSWORD_RESET_ATTEMPTS': int(os.getenv('PASSWORD_RESET_LIMIT', 3)),
        'API_REQUESTS_PER_MINUTE': 100,
        'LOGIN_WINDOW_MINUTES': 5,
        'PASSWORD_RESET_WINDOW_HOURS': 1,
    },
    
    # Email Configuration
    'EMAIL_CONFIG': {
        'EMAIL_BACKEND': os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'),
        'EMAIL_HOST': os.getenv('EMAIL_HOST', ''),
        'EMAIL_PORT': int(os.getenv('EMAIL_PORT', 587)),
        'EMAIL_USE_TLS': bool(os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'),
        'EMAIL_HOST_USER': os.getenv('EMAIL_HOST_USER', ''),
        'EMAIL_HOST_PASSWORD': os.getenv('EMAIL_HOST_PASSWORD', ''),
        'DEFAULT_FROM_EMAIL': os.getenv('DEFAULT_FROM_EMAIL', 'noreply@crisp.local'),
    },
    
    # Logging Configuration
    'LOGGING_CONFIG': {
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
            'security': {
                'format': 'SECURITY {levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'class': 'logging.FileHandler',
                'filename': 'logs/crisp_user_management.log',
                'formatter': 'verbose',
            },
            'security_file': {
                'level': os.getenv('SECURITY_LOG_LEVEL', 'WARNING'),
                'class': 'logging.FileHandler',
                'filename': 'logs/crisp_security.log',
                'formatter': 'security',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'UserManagement': {
                'handlers': ['file', 'console'],
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'propagate': False,
            },
            'crisp.security': {
                'handlers': ['security_file', 'console'],
                'level': os.getenv('SECURITY_LOG_LEVEL', 'WARNING'),
                'propagate': False,
            },
        },
    },
}

# Middleware configuration to add to MIDDLEWARE setting
USER_MANAGEMENT_MIDDLEWARE = [
    'UserManagement.middleware.SecurityHeadersMiddleware',
    'UserManagement.middleware.RateLimitMiddleware',
    'UserManagement.middleware.SecurityAuditMiddleware',
    'UserManagement.middleware.SessionTimeoutMiddleware',
]

# Apps to add to INSTALLED_APPS
USER_MANAGEMENT_APPS = [
    'UserManagement',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

# DRF Configuration
REST_FRAMEWORK_CONFIG = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# Cache configuration for rate limiting
CACHE_CONFIG = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'crisp_usermgmt',
        'TIMEOUT': 300,
    }
}

# Frontend URL for password reset links
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# CRISP Integration Settings
CRISP_INTEGRATION = {
    'ENABLE_STIX_PERMISSIONS': True,
    'ENABLE_TAXII_INTEGRATION': True,
    'ENABLE_FEED_PERMISSIONS': True,
    'ENABLE_ORGANIZATION_TRUST': True,
    'DEFAULT_ANONYMIZATION_STRATEGY': 'minimal',
    'AUDIT_TRAIL_RETENTION_DAYS': 365,
    'SESSION_CLEANUP_INTERVAL_HOURS': 24,
}


def apply_user_management_settings(settings_dict):
    """
    Apply user management settings to Django settings
    
    Usage in main settings.py:
    from UserManagement.settings import apply_user_management_settings
    apply_user_management_settings(globals())
    """
    
    # Apply core settings
    settings_dict.update(USER_MANAGEMENT_SETTINGS)
    
    # Add middleware
    if 'MIDDLEWARE' in settings_dict:
        # Insert at appropriate positions
        middleware = list(settings_dict['MIDDLEWARE'])
        
        # Add security headers at the beginning
        if 'UserManagement.middleware.SecurityHeadersMiddleware' not in middleware:
            middleware.insert(0, 'UserManagement.middleware.SecurityHeadersMiddleware')
        
        # Add rate limiting after security middleware
        security_index = next((i for i, m in enumerate(middleware) if 'Security' in m), 0)
        if 'UserManagement.middleware.RateLimitMiddleware' not in middleware:
            middleware.insert(security_index + 1, 'UserManagement.middleware.RateLimitMiddleware')
        
        # Add audit middleware
        if 'UserManagement.middleware.SecurityAuditMiddleware' not in middleware:
            middleware.append('UserManagement.middleware.SecurityAuditMiddleware')
        
        # Add session timeout middleware
        if 'UserManagement.middleware.SessionTimeoutMiddleware' not in middleware:
            middleware.append('UserManagement.middleware.SessionTimeoutMiddleware')
        
        settings_dict['MIDDLEWARE'] = middleware
    
    # Add apps
    if 'INSTALLED_APPS' in settings_dict:
        apps = list(settings_dict['INSTALLED_APPS'])
        for app in USER_MANAGEMENT_APPS:
            if app not in apps:
                apps.append(app)
        settings_dict['INSTALLED_APPS'] = apps
    
    # Configure REST framework
    if 'REST_FRAMEWORK' not in settings_dict:
        settings_dict['REST_FRAMEWORK'] = REST_FRAMEWORK_CONFIG
    else:
        settings_dict['REST_FRAMEWORK'].update(REST_FRAMEWORK_CONFIG)
    
    # Configure caching if not already configured
    if 'CACHES' not in settings_dict:
        settings_dict['CACHES'] = CACHE_CONFIG
    
    # Apply security settings
    for key, value in USER_MANAGEMENT_SETTINGS['SESSION_SECURITY'].items():
        settings_dict[key] = value
    
    # Configure logging
    if 'LOGGING' not in settings_dict:
        settings_dict['LOGGING'] = USER_MANAGEMENT_SETTINGS['LOGGING_CONFIG']
    
    # Configure email
    for key, value in USER_MANAGEMENT_SETTINGS['EMAIL_CONFIG'].items():
        settings_dict[key] = value
    
    return settings_dict