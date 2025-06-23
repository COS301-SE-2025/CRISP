# 🛡️ CRISP User Management & Authentication System

## Complete User Guide & Technical Documentation

### Overview

The CRISP (Cyber Risk Information Sharing Platform) User Management System is a comprehensive, production-ready authentication and user management solution built with Django and Django REST Framework. It implements enterprise-grade security features, role-based access control, and modern design patterns for cybersecurity platforms.

---

## 📚 Table of Contents

1. [System Architecture](#-system-architecture)
2. [Installation & Setup](#-installation--setup)
3. [Compilation Commands](#-compilation-commands)
4. [Code Structure Walkthrough](#-code-structure-walkthrough)
5. [API Usage Guide](#-api-usage-guide)
6. [Security Features](#-security-features)
7. [User Roles & Permissions](#-user-roles--permissions)
8. [Testing Commands](#-testing-commands)
9. [Configuration Options](#-configuration-options)
10. [Troubleshooting](#-troubleshooting)

---

## 🏗️ System Architecture

### Core Components

```
CRISP User Management
├── 🔐 Authentication System (JWT-based)
├── 👥 User Management (Role-based)
├── 🏢 Organization Management (Multi-tenant)
├── 🛡️ Security Layer (Rate limiting, audit logs)
├── 🎯 Design Patterns (Strategy, Factory, Observer)
└── 🌐 REST API (Django REST Framework)
```

### Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Authentication**: JWT (JSON Web Tokens) with refresh tokens
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Security**: Custom middleware, validators, permissions
- **Architecture**: Clean Architecture with SOLID principles

---

## ⚙️ Installation & Setup

### Prerequisites

```bash
# Required software
- Python 3.8+
- pip (Python package manager)
- Git

# Optional (for production)
- PostgreSQL 12+
- Redis (for caching)
```

### Quick Installation

```bash
# 1. Navigate to project directory
cd /path/to/CRISP/UserManagment

# 2. Install dependencies
pip install django djangorestframework djangorestframework-simplejwt python-dotenv psycopg2-binary

# 3. Apply database migrations
python3 manage.py migrate

# 4. Create admin user
python3 manage.py shell -c "
from UserManagement.models import Organization, CustomUser
from django.contrib.auth.hashers import make_password

# Create default organization
org, created = Organization.objects.get_or_create(
    name='CRISP Organization',
    defaults={
        'description': 'Default CRISP organization',
        'domain': 'crisp.example.com'
    }
)

# Create admin user
admin, created = CustomUser.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@crisp.example.com',
        'password': make_password('admin123'),
        'organization': org,
        'role': 'system_admin',
        'is_superuser': True,
        'is_staff': True,
        'is_verified': True
    }
)
print(f'Setup complete! Admin: {admin.username}')
"

# 5. Start the server
python3 manage.py runserver
```

---

## 🔨 Compilation Commands

### Essential Commands

```bash
# Check system health
python3 manage.py check

# Apply migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Start development server
python3 manage.py runserver

# Start on specific port
python3 manage.py runserver 0.0.0.0:8080
```

### Testing Commands

```bash
# Complete system test
python3 basic_system_test.py

# File structure validation
python3 validate_files.py

# API integration test
python3 test_system.py

# Django unit tests (with known issues)
python3 manage.py test UserManagement --verbosity=2
```

### Production Commands

```bash
# Collect static files
python3 manage.py collectstatic

# Database backup
python3 manage.py dumpdata > backup.json

# Load data
python3 manage.py loaddata backup.json
```

---

## 📁 Code Structure Walkthrough

### Project Structure

```
UserManagment/
├── manage.py                    # Django management script
├── test_settings.py            # Django settings for testing
├── test_urls.py                # URL routing configuration
├── .env                        # Environment variables
├── test_db.sqlite3             # SQLite database
├── UserManagement/             # Main application package
│   ├── __init__.py
│   ├── models.py               # Data models
│   ├── views/                  # API endpoints
│   ├── services/               # Business logic
│   ├── factories/              # User creation factories
│   ├── strategies/             # Authentication strategies
│   ├── observers/              # Event observers
│   ├── tests/                  # Test suite
│   └── management/             # Custom commands
└── Documentation & Scripts/    # Testing and documentation
```

### Core Models (`models.py`)

#### 1. **Organization Model**
```python
class Organization(models.Model):
    """Multi-tenant organization support"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    domain = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
```

**Purpose**: Manages multi-tenant organizations in the CRISP platform.

#### 2. **CustomUser Model**
```python
class CustomUser(AbstractUser):
    """Extended user with CRISP-specific features"""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(choices=USER_ROLE_CHOICES, default='viewer')
    is_publisher = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    trusted_devices = models.JSONField(default=list)
```

**Key Methods**:
- `is_account_locked`: Check if account is locked
- `lock_account()`: Lock account for security
- `can_publish_feeds()`: Check publishing permissions
- `is_organization_admin()`: Check admin status

#### 3. **UserSession Model**
```python
class UserSession(models.Model):
    """JWT session management"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=500, unique=True)
    refresh_token = models.CharField(max_length=500, unique=True)
    device_info = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    expires_at = models.DateTimeField()
```

**Purpose**: Tracks active JWT sessions with device fingerprinting.

#### 4. **AuthenticationLog Model**
```python
class AuthenticationLog(models.Model):
    """Comprehensive audit logging"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

**Purpose**: Security audit trail for all authentication events.

### Authentication Services (`services/auth_service.py`)

#### AuthenticationService Class

```python
class AuthenticationService:
    """Core authentication business logic"""
    
    def authenticate_user(self, username, password, request):
        """Main authentication method"""
        # 1. Strategy pattern for different auth types
        # 2. JWT token generation
        # 3. Session creation
        # 4. Event logging
    
    def verify_token(self, token, request):
        """JWT token verification"""
    
    def refresh_token(self, refresh_token):
        """Token refresh mechanism"""
```

**How it works**:
1. Receives login credentials
2. Applies appropriate authentication strategy
3. Generates JWT access & refresh tokens
4. Creates session record
5. Logs authentication event
6. Returns tokens and user data

### Design Patterns Implementation

#### 1. **Strategy Pattern** (`strategies/authentication_strategies.py`)

```python
class AuthenticationStrategy(ABC):
    """Abstract authentication strategy"""
    @abstractmethod
    def authenticate(self, username, password, request):
        pass

class StandardAuthenticationStrategy(AuthenticationStrategy):
    """Basic username/password authentication"""

class TwoFactorAuthenticationStrategy(AuthenticationStrategy):
    """2FA authentication"""

class TrustedDeviceAuthenticationStrategy(AuthenticationStrategy):
    """Trusted device authentication"""
```

**Usage**: Different authentication methods based on user settings and security requirements.

#### 2. **Factory Pattern** (`factories/user_factory.py`)

```python
class UserFactory:
    """Creates users based on role and permissions"""
    
    @classmethod
    def create_user(cls, role, user_data, created_by=None):
        """Factory method for user creation"""
        # 1. Validate permissions
        # 2. Apply role-specific settings
        # 3. Create user with appropriate defaults
        # 4. Log creation event
```

**User Creation Examples**:
```python
# Create a viewer
user_data = {
    'username': 'john_viewer',
    'email': 'john@example.com',
    'password': 'SecurePass123!',
    'organization': organization
}
viewer = UserFactory.create_user('viewer', user_data)

# Create a publisher
publisher_data = {
    'username': 'jane_publisher',
    'email': 'jane@example.com',
    'password': 'SecurePass123!',
    'organization': organization
}
publisher = UserFactory.create_user('publisher', publisher_data, created_by=admin)
```

#### 3. **Observer Pattern** (`observers/auth_observers.py`)

```python
class AuthEventSubject:
    """Subject for authentication events"""
    
    def notify_observers(self, event_type, user, event_data):
        """Notify all observers of authentication events"""

class AuthenticationLogObserver(Observer):
    """Logs authentication events"""

class SecurityAlertObserver(Observer):
    """Sends security alerts for suspicious activity"""
```

**Purpose**: Decoupled event handling for authentication events.

### API Views (`views/`)

#### Authentication Views (`auth_views.py`)

```python
class CustomTokenObtainPairView(TokenObtainPairView):
    """JWT login endpoint"""
    # POST /api/auth/login/
    # Returns: access_token, refresh_token, user_data

class ProfileView(APIView):
    """User profile endpoint"""
    # GET /api/auth/profile/
    # Returns: user profile data

class LogoutView(APIView):
    """Logout endpoint"""
    # POST /api/auth/logout/
    # Invalidates current session
```

#### Admin Views (`admin_views.py`)

```python
class AdminUserListCreateView(ListCreateAPIView):
    """Admin user management"""
    # GET /api/admin/users/ - List users
    # POST /api/admin/users/ - Create user

class AdminUserDetailView(RetrieveUpdateDestroyAPIView):
    """Individual user management"""
    # GET /api/admin/users/{id}/ - Get user
    # PUT /api/admin/users/{id}/ - Update user
    # DELETE /api/admin/users/{id}/ - Delete user
```

#### User Views (`user_views.py`)

```python
class UserDashboardView(APIView):
    """User dashboard data"""
    # GET /api/user/dashboard/

class UserSessionListView(ListAPIView):
    """User's active sessions"""
    # GET /api/user/sessions/
```

### Security Components

#### Middleware (`middleware.py`)

```python
class SecurityHeadersMiddleware:
    """Adds security headers to all responses"""
    # X-XSS-Protection, X-Content-Type-Options, etc.

class RateLimitMiddleware:
    """IP-based rate limiting"""
    # 5 login attempts per 5 minutes per IP

class SecurityAuditMiddleware:
    """Logs suspicious activities"""
    # SQL injection patterns, XSS attempts, etc.
```

#### Validators (`validators.py`)

```python
def validate_password_strength(password):
    """Enforces strong password policy"""
    # 12+ characters, uppercase, lowercase, digits, special chars

def validate_organization_domain(domain):
    """Validates organization email domain"""

def validate_user_role_permissions(user, role):
    """Ensures user can assign specific roles"""
```

#### Permissions (`permissions.py`)

```python
class IsSystemAdmin(BasePermission):
    """Only system administrators"""

class IsOrganizationAdmin(BasePermission):
    """Organization administrators"""

class IsPublisher(BasePermission):
    """Users who can publish threat feeds"""

class IsSameUserOrAdmin(BasePermission):
    """Users can only access their own data (or admins)"""
```

---

## 🌐 API Usage Guide

### Authentication Flow

#### 1. **User Login**

```bash
# Request
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Response
{
  "success": true,
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access_expires": "2025-06-23T19:00:00Z",
    "refresh_expires": "2025-06-30T18:00:00Z"
  },
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin",
    "email": "admin@crisp.example.com",
    "role": "system_admin",
    "organization": "CRISP Organization",
    "is_verified": true
  },
  "session_id": "987fcdeb-51a2-43d1-b789-123456789abc"
}
```

#### 2. **Access Protected Endpoints**

```bash
# Get user profile
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "admin",
  "email": "admin@crisp.example.com",
  "role": "system_admin",
  "organization": {
    "id": "org-123",
    "name": "CRISP Organization",
    "domain": "crisp.example.com"
  },
  "is_publisher": false,
  "is_verified": true,
  "last_login": "2025-06-23T18:00:00Z"
}
```

#### 3. **Token Refresh**

```bash
# Refresh access token
curl -X POST http://127.0.0.1:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'

# Response
{
  "access": "new_access_token_here",
  "access_expires": "2025-06-23T20:00:00Z"
}
```

### Admin Operations

#### 1. **List Users**

```bash
curl -X GET http://127.0.0.1:8000/api/admin/users/ \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Response
{
  "count": 10,
  "next": "http://127.0.0.1:8000/api/admin/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": "user-123",
      "username": "john_analyst",
      "email": "john@example.com",
      "role": "analyst",
      "organization": "CRISP Organization",
      "is_verified": true,
      "last_login": "2025-06-23T17:30:00Z"
    }
    // ... more users
  ]
}
```

#### 2. **Create User**

```bash
curl -X POST http://127.0.0.1:8000/api/admin/users/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_analyst",
    "email": "analyst@example.com",
    "password": "SecurePass123!",
    "role": "analyst",
    "first_name": "John",
    "last_name": "Analyst"
  }'

# Response
{
  "id": "new-user-456",
  "username": "new_analyst",
  "email": "analyst@example.com",
  "role": "analyst",
  "organization": "CRISP Organization",
  "is_verified": false,
  "created_at": "2025-06-23T18:15:00Z"
}
```

#### 3. **Update User**

```bash
curl -X PUT http://127.0.0.1:8000/api/admin/users/user-456/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "publisher",
    "is_verified": true
  }'
```

### User Operations

#### 1. **User Dashboard**

```bash
curl -X GET http://127.0.0.1:8000/api/user/dashboard/ \
  -H "Authorization: Bearer USER_TOKEN"

# Response
{
  "user": {
    "username": "john_analyst",
    "role": "analyst",
    "organization": "CRISP Organization"
  },
  "stats": {
    "active_sessions": 2,
    "last_login": "2025-06-23T17:30:00Z",
    "failed_login_attempts": 0
  },
  "permissions": {
    "can_publish_feeds": false,
    "can_manage_users": false,
    "can_view_analytics": true
  },
  "recent_activity": [
    {
      "action": "login_success",
      "timestamp": "2025-06-23T17:30:00Z",
      "ip_address": "192.168.1.100"
    }
  ]
}
```

#### 2. **Active Sessions**

```bash
curl -X GET http://127.0.0.1:8000/api/user/sessions/ \
  -H "Authorization: Bearer USER_TOKEN"

# Response
{
  "count": 2,
  "results": [
    {
      "id": "session-789",
      "device_info": {
        "browser": "Chrome 91.0",
        "os": "Windows 10",
        "device_type": "desktop"
      },
      "ip_address": "192.168.1.100",
      "created_at": "2025-06-23T17:30:00Z",
      "last_activity": "2025-06-23T18:00:00Z",
      "is_current": true
    }
  ]
}
```

#### 3. **Change Password**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/change-password/ \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "current_password",
    "new_password": "NewSecurePass123!",
    "confirm_password": "NewSecurePass123!"
  }'

# Response
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

## 🛡️ Security Features

### 1. **Authentication Security**

- **JWT Tokens**: Secure, stateless authentication
- **Token Refresh**: Automatic token rotation
- **Session Management**: Device tracking and session control
- **Account Lockout**: 5 failed attempts = 30-minute lockout

### 2. **Password Security**

```python
# Password Requirements
- Minimum 12 characters
- At least 1 uppercase letter
- At least 1 lowercase letter  
- At least 1 digit
- At least 1 special character
- Cannot contain username or email
- Cannot be a common password
```

### 3. **Rate Limiting**

```python
# Default Limits
- Login attempts: 5 per 5 minutes per IP
- Password reset: 3 per hour per IP
- API calls: 100 per minute per user
- Registration: 10 per hour per IP
```

### 4. **Security Headers**

```http
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000
```

### 5. **Audit Logging**

All security events are logged:
- Login attempts (success/failure)
- Password changes
- Account lockouts
- Permission changes
- Suspicious activities

### 6. **Device Management**

```python
# Trusted Device Features
- Device fingerprinting
- Automatic device registration
- Manual device management
- Suspicious device alerts
```

---

## 👥 User Roles & Permissions

### Role Hierarchy

```
System Admin (system_admin)
├── Full system access
├── Manage all organizations
├── Create/delete any user
└── System configuration

Organization Admin (admin)
├── Manage organization users
├── Organization settings
├── Publisher permissions
└── View organization analytics

Publisher (publisher)
├── Publish threat intelligence feeds
├── Manage own publications
├── Access analytics
└── Standard user permissions

Analyst (analyst)
├── Access threat intelligence
├── View analytics
├── Generate reports
└── Standard user permissions

Viewer (viewer)
├── Read-only access
├── View threat intelligence
├── Basic dashboard
└── Profile management
```

### Permission Matrix

| Action | Viewer | Analyst | Publisher | Admin | System Admin |
|--------|--------|---------|-----------|-------|--------------|
| View threat intel | ✅ | ✅ | ✅ | ✅ | ✅ |
| Generate reports | ❌ | ✅ | ✅ | ✅ | ✅ |
| Publish feeds | ❌ | ❌ | ✅ | ✅ | ✅ |
| Manage org users | ❌ | ❌ | ❌ | ✅ | ✅ |
| System settings | ❌ | ❌ | ❌ | ❌ | ✅ |

### Role Assignment

```python
# Via API (Admin only)
PUT /api/admin/users/{user_id}/
{
  "role": "publisher",
  "is_verified": true
}

# Via Factory
publisher = UserFactory.create_user('publisher', user_data, created_by=admin)

# Via Admin Interface
# http://127.0.0.1:8000/admin/UserManagement/customuser/
```

---

## 🧪 Testing Commands

### Quick System Test

```bash
# Complete system validation (recommended)
python3 basic_system_test.py

# Expected output:
# ✅ Django setup successful
# ✅ Models functional - Users: X, Orgs: Y
# ✅ Authentication service working
# ✅ API login successful
# ✅ API profile working
# ✅ Admin interface accessible
# ✅ Security headers present
# 📊 Test Results: 7/7 passed
# 🎉 All basic tests passed!
```

### Detailed Testing

```bash
# File structure validation
python3 validate_files.py

# Django configuration check
python3 manage.py check

# API integration test
python3 test_system.py

# Database validation
python3 manage.py shell -c "
from UserManagement.models import *
print(f'Users: {CustomUser.objects.count()}')
print(f'Organizations: {Organization.objects.count()}')
print(f'Sessions: {UserSession.objects.count()}')
print(f'Auth Logs: {AuthenticationLog.objects.count()}')
"
```

### Security Testing

```bash
# Test rate limiting
for i in {1..10}; do
  curl -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "wrong"}'
  echo "Attempt $i"
done

# Test security headers
curl -I http://127.0.0.1:8000/api/auth/login/ | \
  grep -E "(X-XSS|X-Content|X-Frame)"

# Test JWT token validation
python3 manage.py shell -c "
from rest_framework_simplejwt.tokens import AccessToken
from UserManagement.models import CustomUser

user = CustomUser.objects.get(username='admin')
token = AccessToken.for_user(user)
print(f'Token: {str(token)[:50]}...')

# Verify token
verified = AccessToken(str(token))
print(f'User ID: {verified.get(\"user_id\")}')
"
```

### Performance Testing

```bash
# Concurrent login test
for i in {1..5}; do
  (curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' \
    -w "Time: %{time_total}s\n") &
done
wait

# Database query performance
python3 manage.py shell -c "
import time
from UserManagement.models import CustomUser, AuthenticationLog

start = time.time()
users = list(CustomUser.objects.select_related('organization').all())
print(f'User query: {time.time() - start:.4f}s ({len(users)} users)')

start = time.time()
logs = list(AuthenticationLog.objects.select_related('user')[:100])
print(f'Log query: {time.time() - start:.4f}s ({len(logs)} logs)')
"
```

---

## ⚙️ Configuration Options

### Environment Variables (`.env`)

```bash
# Database Configuration
DB_NAME=crisp
DB_USER=admin
DB_PASSWORD=AdminPassword
DB_HOST=localhost
DB_PORT=5432
USE_POSTGRES=False  # Set to True for PostgreSQL

# Security Settings
SECRET_KEY=your-secret-key-here
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=10080  # minutes (7 days)

# Rate Limiting
RATE_LIMIT_LOGIN=5  # attempts per window
RATE_LIMIT_WINDOW=300  # seconds (5 minutes)

# Password Policy
MIN_PASSWORD_LENGTH=12
REQUIRE_UPPERCASE=True
REQUIRE_LOWERCASE=True
REQUIRE_DIGITS=True
REQUIRE_SPECIAL_CHARS=True
```

### Django Settings (`test_settings.py`)

```python
# Key Configuration Options

# Custom User Model
AUTH_USER_MODEL = 'UserManagement.CustomUser'

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'PAGE_SIZE': 20,
}

# Security Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'UserManagement.middleware.SecurityHeadersMiddleware',
]
```

### Database Configuration

#### SQLite (Development)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}
```

#### PostgreSQL (Production)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'crisp'),
        'USER': os.getenv('DB_USER', 'admin'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. **Django Import Error**

```bash
# Error: "Couldn't import Django"
# Solution: Install dependencies
pip install django djangorestframework djangorestframework-simplejwt

# Or create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### 2. **Database Connection Error**

```bash
# Error: "no such table: UserManagement_customuser"
# Solution: Run migrations
python3 manage.py makemigrations UserManagement
python3 manage.py migrate

# If issues persist, reset migrations
python3 manage.py migrate UserManagement zero
python3 manage.py makemigrations UserManagement
python3 manage.py migrate
```

#### 3. **Admin Login Failed**

```bash
# Error: "Please enter the correct username and password"
# Solution: Reset admin password
python3 manage.py shell -c "
from UserManagement.models import CustomUser
admin = CustomUser.objects.get(username='admin')
admin.set_password('admin123')
admin.save()
print('Password reset to: admin123')
"
```

#### 4. **JWT Token Error**

```bash
# Error: "Token is invalid or expired"
# Solution: Check token generation
python3 manage.py shell -c "
from UserManagement.services.auth_service import AuthenticationService
from django.test import RequestFactory

factory = RequestFactory()
request = factory.post('/api/auth/login/')
request.META['REMOTE_ADDR'] = '127.0.0.1'

auth_service = AuthenticationService()
result = auth_service.authenticate_user('admin', 'admin123', request)
print(f'Auth result: {result[\"success\"]}')
"
```

#### 5. **Rate Limiting Issues**

```bash
# Error: "Rate limit exceeded"
# Solution: Clear cache or wait
python3 manage.py shell -c "
from django.core.cache import cache
cache.clear()
print('Cache cleared')
"

# Or check current rate limits
python3 manage.py shell -c "
from django.core.cache import cache
from UserManagement.middleware import RateLimitMiddleware

# Check current limits for an IP
ip = '127.0.0.1'
login_key = f'rate_limit:login:{ip}'
current = cache.get(login_key, 0)
print(f'Current login attempts for {ip}: {current}')
"
```

### Debugging Commands

```bash
# Enable Django debug mode
export DEBUG=True

# Check Django configuration
python3 manage.py check --verbosity=2

# View database schema
python3 manage.py dbshell -c ".schema" 2>/dev/null || echo "SQLite schema check"

# Check migrations status
python3 manage.py showmigrations

# Validate models
python3 manage.py validate 2>/dev/null || python3 manage.py check

# Test database connection
python3 manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
print('Database connection: OK')
"
```

### Performance Optimization

```bash
# Database optimization
python3 manage.py shell -c "
from django.db import connection
print('Database queries executed:')
for query in connection.queries:
    print(f'  {query[\"time\"]}s: {query[\"sql\"][:100]}...')
"

# Memory usage check
python3 -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"

# Cache status
python3 manage.py shell -c "
from django.core.cache import cache
from django.conf import settings
print(f'Cache backend: {settings.CACHES[\"default\"][\"BACKEND\"]}')
"
```

---

## 📞 Support & Resources

### Documentation Files

- `COMPREHENSIVE_TESTING_GUIDE.md` - Detailed testing instructions
- `TESTING_COMMANDS_SUMMARY.md` - Quick reference for testing
- `QUICK_START.md` - Fast setup guide

### Test Scripts

- `basic_system_test.py` - Core functionality test
- `test_system.py` - API integration test
- `validate_files.py` - File structure validation

### Management Commands

```bash
# Custom management commands
python3 manage.py setup_auth --help

# Built-in Django commands
python3 manage.py help
python3 manage.py shell
python3 manage.py dbshell
```

### Logging

```bash
# View authentication logs
python3 manage.py shell -c "
from UserManagement.models import AuthenticationLog
logs = AuthenticationLog.objects.order_by('-timestamp')[:10]
for log in logs:
    print(f'{log.timestamp}: {log.username} - {log.action} - {log.success}')
"

# View user sessions
python3 manage.py shell -c "
from UserManagement.models import UserSession
sessions = UserSession.objects.filter(is_active=True)
print(f'Active sessions: {sessions.count()}')
for session in sessions:
    print(f'  {session.user.username} from {session.ip_address}')
"
```

---

## 🎉 Conclusion

The CRISP User Management System provides a complete, enterprise-ready authentication and user management solution with:

- ✅ **Security First**: JWT tokens, rate limiting, audit logging
- ✅ **Role-Based Access**: Five user roles with granular permissions  
- ✅ **Multi-Tenant**: Organization-based user management
- ✅ **Modern Architecture**: Clean code with design patterns
- ✅ **Production Ready**: Comprehensive testing and documentation
- ✅ **API Driven**: Full REST API with Django REST Framework

### Quick Start Summary

```bash
# 1. Install dependencies
pip install django djangorestframework djangorestframework-simplejwt python-dotenv

# 2. Setup database
python3 manage.py migrate

# 3. Test system
python3 basic_system_test.py

# 4. Start server
python3 manage.py runserver

# 5. Access admin
# URL: http://127.0.0.1:8000/admin/
# User: admin / admin123
```

The system is fully operational and ready for cybersecurity platform integration!

---

**📧 For support or questions, refer to the comprehensive test scripts and documentation files included in this project.**