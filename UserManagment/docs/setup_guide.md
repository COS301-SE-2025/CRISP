# CRISP User Management Setup & Testing Guide

## Quick Start Commands

```bash
# 1. Navigate to the UserManagement directory
cd /path/to/CRISP/UserManagement

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required packages
pip install django==4.2.7
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.0
pip install psycopg2-binary==2.9.7
pip install python-dotenv==1.0.0
pip install django-cors-headers==4.3.1

# 4. Verify .env file exists with correct settings
cat .env

# 5. Test database connection
python -c "
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'crisp'),
        user=os.getenv('DB_USER', 'admin'),
        password=os.getenv('DB_PASSWORD', 'AdminPassword')
    )
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

## Create Django Project Structure

Since we have the UserManagement app, we need a Django project to contain it:

```bash
# Create Django project
django-admin startproject crisp_project .

# The structure should look like:
# .
# ├── crisp_project/
# │   ├── __init__.py
# │   ├── settings.py
# │   ├── urls.py
# │   └── wsgi.py
# ├── UserManagement/
# │   ├── models.py
# │   ├── views/
# │   └── ... (all our files)
# ├── manage.py
# └── .env
```

## Configure Django Settings

Edit `crisp_project/settings.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'crisp-local-development-secret-key')
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
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'UserManagement',
]

MIDDLEWARE = [
    'UserManagement.middleware.SecurityHeadersMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'UserManagement.middleware.RateLimitMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'UserManagement.middleware.SecurityAuditMiddleware',
    'UserManagement.middleware.SessionTimeoutMiddleware',
]

ROOT_URLCONF = 'crisp_project.urls'

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

WSGI_APPLICATION = 'crisp_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'crisp'),
        'USER': os.getenv('DB_USER', 'admin'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'AdminPassword'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'UserManagement.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
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
]

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# REST Framework
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
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Cache (using dummy cache for local testing)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# CORS (for frontend testing)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'UserManagement': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'crisp.security': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}
```

## Configure URLs

Edit `crisp_project/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('UserManagement.urls')),
]
```

## Run Initial Setup

```bash
# Create and run migrations
python manage.py makemigrations UserManagement
python manage.py migrate

# Create superuser
python manage.py setup_auth --create-superuser --username=admin --email=admin@crisp.local --password=AdminPassword123!

# Start development server
python manage.py runserver
```

## 🧪 Test the Implementation

### 1. Test Database Connection
```bash
python manage.py dbshell
\dt  # List tables
\q   # Quit
```

### 2. Test Management Commands
```bash
# Setup authentication system
python manage.py setup_auth --create-superuser --username=testadmin --email=test@crisp.local

# Audit users
python manage.py audit_users --security-focus

# Create additional superuser
python manage.py create_superuser --username=admin2 --email=admin2@crisp.local --non-interactive --password=SecurePassword123!
```

### 3. Test Django Admin
```bash
# Start server
python manage.py runserver

# Visit: http://127.0.0.1:8000/admin/
# Login with: admin / AdminPassword123!
```

### 4. Test API Endpoints

**Test Authentication:**
```bash
# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "AdminPassword123!"
  }'

# Should return JWT tokens
```

**Test User Profile:**
```bash
# Get JWT token from login response, then:
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Test Admin Endpoints:**
```bash
# List users (admin only)
curl -X GET http://127.0.0.1:8000/api/admin/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Test Security Features

**Test Rate Limiting:**
```bash
# Try multiple failed logins (should get rate limited)
for i in {1..10}; do
  curl -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "wrong"}'
done
```

**Test Account Lockout:**
```bash
# Check authentication logs
python manage.py shell
>>> from UserManagement.models import AuthenticationLog
>>> logs = AuthenticationLog.objects.filter(action='login_failed').order_by('-timestamp')
>>> for log in logs[:5]:
...     print(f"{log.timestamp}: {log.username} - {log.failure_reason}")
```

### 6. Run Test Suite
```bash
# Run all tests
python manage.py test UserManagement

# Run specific test categories
python manage.py test UserManagement.tests.test_authentication
python manage.py test UserManagement.tests.test_security
python manage.py test UserManagement.tests.test_user_management

# Run with verbose output
python manage.py test UserManagement --verbosity=2
```

### 7. Test Frontend Integration

Create a simple HTML test page (`test_frontend.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>CRISP Auth Test</title>
</head>
<body>
    <div id="app">
        <h2>CRISP Authentication Test</h2>
        
        <div id="login-section">
            <h3>Login</h3>
            <input type="text" id="username" placeholder="Username" value="admin">
            <input type="password" id="password" placeholder="Password" value="AdminPassword123!">
            <button onclick="login()">Login</button>
        </div>
        
        <div id="user-section" style="display:none;">
            <h3>User Profile</h3>
            <div id="user-info"></div>
            <button onclick="logout()">Logout</button>
        </div>
        
        <div id="result"></div>
    </div>

    <script>
        let accessToken = null;

        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    accessToken = data.tokens.access;
                    document.getElementById('login-section').style.display = 'none';
                    document.getElementById('user-section').style.display = 'block';
                    
                    // Get user profile
                    await getUserProfile();
                } else {
                    document.getElementById('result').innerHTML = 
                        `<p style="color:red;">Login failed: ${data.message}</p>`;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    `<p style="color:red;">Error: ${error.message}</p>`;
            }
        }

        async function getUserProfile() {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/auth/profile/', {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                
                const data = await response.json();
                document.getElementById('user-info').innerHTML = `
                    <p><strong>Username:</strong> ${data.username}</p>
                    <p><strong>Email:</strong> ${data.email}</p>
                    <p><strong>Role:</strong> ${data.role}</p>
                    <p><strong>Organization:</strong> ${data.organization_name}</p>
                    <p><strong>Verified:</strong> ${data.is_verified}</p>
                `;
            } catch (error) {
                console.error('Error fetching profile:', error);
            }
        }

        function logout() {
            accessToken = null;
            document.getElementById('login-section').style.display = 'block';
            document.getElementById('user-section').style.display = 'none';
            document.getElementById('result').innerHTML = '';
        }
    </script>
</body>
</html>
```

Open this file in a browser while the Django server is running to test the frontend integration.

## 🔍 Verification Checklist

- [ ] Database connection successful
- [ ] Migrations applied without errors
- [ ] Superuser created successfully
- [ ] Django admin accessible
- [ ] JWT authentication working
- [ ] API endpoints responding correctly
- [ ] Rate limiting functional
- [ ] Account lockout working
- [ ] Test suite passing (100%)
- [ ] Security headers present
- [ ] Frontend integration working

## 📊 Expected Test Results

When everything is working correctly, you should see:

1. **Database**: All tables created successfully
2. **Admin Interface**: Fully functional with user management
3. **API Tests**: All endpoints returning proper responses
4. **Security Tests**: Rate limiting and lockout mechanisms working
5. **Test Suite**: All tests passing (should be 50+ tests)

## 🐛 Troubleshooting

**Database Connection Issues:**
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check credentials in `.env` file
- Ensure database and user exist

**Migration Issues:**
- Delete migration files and recreate: `python manage.py makemigrations UserManagement`
- Check for missing dependencies

**JWT Token Issues:**
- Verify SECRET_KEY is set
- Check token expiration settings
- Ensure proper headers in requests

**Rate Limiting Issues:**
- Check cache configuration
- Verify middleware order in settings

This comprehensive testing guide will verify that all components of the CRISP User Management & Authentication system are working correctly.