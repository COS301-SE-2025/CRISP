# 🛡️ CRISP User Management & Authentication Implementation Guide

**COMPREHENSIVE CLAUDE CODE PROMPT FOR PERFECT USER MANAGEMENT & AUTHENTICATION**

## 🎯 MISSION STATEMENT

You are implementing the **User Management and Authentication** module for the CRISP (Cyber Risk Information Sharing Platform) system. This implementation must follow the CRISP domain model EXACTLY as specified and implement ALL functional requirements with PERFECT adherence to the existing architecture, design patterns, and code quality standards.

## 📋 CRITICAL IMPLEMENTATION REQUIREMENTS

### R1. Authentication and User Management Requirements
**MUST implement ALL of these requirements with 100% functional parity:**

#### R1.1. Secure Authentication Mechanisms
- **R1.1.1**: Username and password authentication with JWT tokens
- **R1.1.2**: Strong password policies (min 12 chars, complexity requirements)
- **R1.1.3**: Password reset functionality with secure token generation
- **R1.1.4**: "Remember me" functionality for trusted devices
- **R1.1.5**: Account lockout after multiple failed login attempts (5 attempts)
- **R1.1.6**: Complete authentication activity logging

#### R1.2. User Registration and Management
- **R1.2.1**: Administrator-controlled user registration
- **R1.2.2**: Administrator-controlled user deletion with soft delete
- **R1.2.3**: User registration restricted to authorized publishers only
- **R1.2.4**: Comprehensive user credential verification during authentication

#### R1.3. Organization Registration and Management
- **R1.3.1**: Administrator-controlled organization registration
- **R1.3.2**: Administrator-controlled organization deletion with cascade handling
- **R1.3.3**: Organization registration restricted to system administrators only

## 🏗️ DOMAIN MODEL ARCHITECTURE COMPLIANCE

### Existing CRISP Domain Entities (DO NOT MODIFY)
The following entities are already implemented and MUST be preserved:

```python
# EXISTING MODELS - DO NOT CHANGE
class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    identity_class = models.CharField(max_length=100, default='organization')
    sectors = models.JSONField(default=list, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    stix_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_organizations')
```

### Required New Domain Entities
**You MUST implement these new models in the UserManagement folder:**

#### 1. CustomUser Model (extends Django User)
```python
class CustomUser(AbstractUser):
    """
    Extended User model following CRISP domain specifications.
    MUST integrate with existing Organization model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('crisp_threat_intel.Organization', on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=50, choices=USER_ROLE_CHOICES)
    is_publisher = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    trusted_devices = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2. UserSession Model (for JWT and session management)
```python
class UserSession(models.Model):
    """
    Track user sessions and JWT tokens for security.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sessions')
    session_token = models.CharField(max_length=500, unique=True)
    refresh_token = models.CharField(max_length=500, unique=True, null=True, blank=True)
    device_info = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    is_trusted_device = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
```

#### 3. AuthenticationLog Model
```python
class AuthenticationLog(models.Model):
    """
    Comprehensive authentication activity logging.
    """
    ACTION_CHOICES = [
        ('login_success', 'Login Success'),
        ('login_failed', 'Login Failed'),
        ('logout', 'Logout'),
        ('password_reset', 'Password Reset'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('password_changed', 'Password Changed'),
        ('token_refresh', 'Token Refresh'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='auth_logs', null=True, blank=True)
    username = models.CharField(max_length=150)  # Store even if user is deleted
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField()
    failure_reason = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_data = models.JSONField(default=dict)
```

## 🔧 DESIGN PATTERNS IMPLEMENTATION

### Strategy Pattern for Authentication
**MUST implement following the existing CRISP Strategy pattern architecture:**

```python
# UserManagement/strategies/authentication_strategies.py
class AuthenticationStrategy(ABC):
    """Abstract base for authentication strategies"""
    @abstractmethod
    def authenticate(self, username: str, password: str, request=None) -> dict:
        pass

class StandardAuthenticationStrategy(AuthenticationStrategy):
    """Standard username/password authentication"""
    
class TwoFactorAuthenticationStrategy(AuthenticationStrategy):
    """Two-factor authentication strategy"""

class TrustedDeviceAuthenticationStrategy(AuthenticationStrategy):
    """Trusted device authentication with reduced requirements"""
```

### Factory Pattern for User Creation
**MUST follow the existing CRISP Factory pattern:**

```python
# UserManagement/factories/user_factory.py
class UserCreator(ABC):
    """Abstract user creator following CRISP Factory pattern"""
    @abstractmethod
    def create_user(self, user_data: dict) -> CustomUser:
        pass

class StandardUserCreator(UserCreator):
    """Creates standard users"""

class PublisherUserCreator(UserCreator):
    """Creates publisher users with additional validation"""

class AdminUserCreator(UserCreator):
    """Creates admin users with full privileges"""
```

### Observer Pattern for Authentication Events
**MUST integrate with existing CRISP Observer pattern:**

```python
# UserManagement/observers/auth_observers.py
class AuthenticationObserver(ABC):
    """Observer for authentication events"""
    @abstractmethod
    def notify(self, event_type: str, user: CustomUser, event_data: dict):
        pass

class SecurityAuditObserver(AuthenticationObserver):
    """Logs security events"""

class AccountLockoutObserver(AuthenticationObserver):
    """Handles account lockout logic"""

class NotificationObserver(AuthenticationObserver):
    """Sends notifications for auth events"""
```

## 🛢️ DATABASE INTEGRATION

### Local Development Database Configuration
**MUST set up PostgreSQL locally for development:**

```python
# Database settings for LOCAL DEVELOPMENT
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crisp',
        'USER': 'admin',
        'PASSWORD': 'AdminPassword', 
        'HOST': 'localhost',  # Local PostgreSQL
        'PORT': '5432',
    }
}

# Pi PostgreSQL Configuration (COMMENTED OUT - UNCOMMENT WHEN PI IS BACK ONLINE)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'crisp',
#         'USER': 'admin', 
#         'PASSWORD': 'AdminPassword',
#         'HOST': '100.117.251.119',  # Pi host
#         'PORT': '5432',
#     }
# }
```

### Local PostgreSQL Setup
**MUST install and configure PostgreSQL locally:**

```bash
# Install PostgreSQL locally
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Windows:
# Download from https://www.postgresql.org/download/windows/

# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create local database and user (SAME CREDENTIALS AS PI)
sudo -u postgres psql
CREATE DATABASE crisp;
CREATE USER admin WITH ENCRYPTED PASSWORD 'AdminPassword';
GRANT ALL PRIVILEGES ON DATABASE crisp TO admin;
ALTER USER admin CREATEDB;  # Allow creating test databases
\q
```

### Environment Configuration
**MUST create .env file for easy switching between local and Pi:**

```bash
# .env file for LOCAL DEVELOPMENT
DEBUG=True
SECRET_KEY=your-local-development-secret-key

# Local Database Configuration
DB_NAME=crisp
DB_USER=admin
DB_PASSWORD=AdminPassword
DB_HOST=localhost
DB_PORT=5432

# Pi Database Configuration (COMMENTED OUT)
# DB_HOST=100.117.251.119  # Uncomment when Pi is back online

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Security Settings
ALLOWED_HOSTS=localhost,127.0.0.1
# ALLOWED_HOSTS=localhost,127.0.0.1,100.117.251.119  # Uncomment for Pi

# Other settings remain the same for both local and Pi
OTX_API_KEY=your-otx-api-key-if-available
```

**Settings.py configuration for easy switching:**
```python
# settings.py - Use environment variables for easy switching
import os
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'crisp'),
        'USER': os.getenv('DB_USER', 'admin'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'AdminPassword'),
        'HOST': os.getenv('DB_HOST', 'localhost'),  # Change to '100.117.251.119' for Pi
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Easy Pi switching: Just change DB_HOST in .env file
# From: DB_HOST=localhost
# To:   DB_HOST=100.117.251.119
```

### Migration Strategy
**Local development approach:**
- All development done with local PostgreSQL
- Migrations created and tested locally
- When Pi comes back online, migrations can be synced using existing `scripts/sync_migrations.sh`
- Database configuration easily switched by uncommenting Pi config

**Pi Integration (when Pi comes back online):**
```bash
# Uncomment Pi database configuration in settings.py
# Comment out local database configuration
# Use existing sync script:
./scripts/sync_migrations.sh
```

## 🔐 JWT AUTHENTICATION IMPLEMENTATION

### JWT Configuration
```python
# settings.py additions
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

# Custom JWT serializers required
AUTH_USER_MODEL = 'UserManagement.CustomUser'
```

### JWT Views and Serializers
**MUST implement these exact endpoints:**

```python
# UserManagement/views/auth_views.py
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token generation with enhanced security"""

class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh with security logging"""

class CustomTokenVerifyView(TokenVerifyView):
    """Token verification with activity tracking"""

class PasswordResetView(APIView):
    """Secure password reset implementation"""

class TrustedDeviceView(APIView):
    """Manage trusted devices"""
```

## 📁 EXACT FOLDER STRUCTURE

**MUST create this EXACT folder structure:**

```
UserManagement/
├── __init__.py
├── models.py                     # CustomUser, UserSession, AuthenticationLog
├── admin.py                      # Django admin for user management
├── apps.py                       # App configuration
├── serializers.py                # DRF serializers for API
├── permissions.py                # Custom permissions and authorization
├── authentication.py             # Custom authentication backends
├── middleware.py                 # Security middleware
├── validators.py                 # Password and input validation
├── utils.py                      # Utility functions
├── signals.py                    # Django signals for user events
├── strategies/
│   ├── __init__.py
│   └── authentication_strategies.py  # Strategy pattern implementation
├── factories/
│   ├── __init__.py
│   └── user_factory.py          # Factory pattern for user creation
├── observers/
│   ├── __init__.py
│   └── auth_observers.py        # Observer pattern for auth events
├── services/
│   ├── __init__.py
│   ├── auth_service.py          # Core authentication business logic
│   ├── user_service.py          # User management business logic
│   └── session_service.py       # Session and JWT management
├── views/
│   ├── __init__.py
│   ├── auth_views.py            # Authentication API endpoints
│   ├── user_views.py            # User management API endpoints
│   └── admin_views.py           # Admin-only endpoints
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── create_superuser.py   # Enhanced superuser creation
│       ├── setup_auth.py         # Authentication setup command
│       └── audit_users.py        # User audit command
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py          # Initial migration
├── tests/
│   ├── __init__.py
│   ├── test_authentication.py    # Auth tests
│   ├── test_user_management.py   # User management tests
│   ├── test_jwt.py              # JWT functionality tests
│   ├── test_security.py         # Security feature tests
│   └── test_integration.py      # Integration tests
└── templates/
    └── auth/
        ├── login.html           # Login page template
        ├── password_reset.html  # Password reset template
        └── account_locked.html  # Account locked template
```

## 🔧 REQUIRED DEPENDENCIES

**Add these to requirements.txt:**
```txt
# Environment configuration
python-dotenv==1.0.0

# JWT Authentication
djangorestframework-simplejwt==5.3.0
PyJWT==2.8.0

# Password validation and security
django-password-validators==1.7.1
bcrypt==4.1.2

# Rate limiting and security
django-ratelimit==4.1.0
django-axes==6.1.1

# Additional security
django-security==0.17.0
```

## 🧪 COMPREHENSIVE TESTING REQUIREMENTS

### Test Coverage Requirements
**MUST achieve 100% test coverage with these test categories:**

#### 1. Authentication Tests (`test_authentication.py`)
```python
class AuthenticationTestCase(TestCase):
    """
    MUST test ALL authentication scenarios:
    - Username/password authentication
    - JWT token generation and validation
    - Password reset flow
    - Account lockout after failed attempts
    - Trusted device authentication
    - Two-factor authentication (if implemented)
    """
```

#### 2. User Management Tests (`test_user_management.py`)
```python
class UserManagementTestCase(TestCase):
    """
    MUST test ALL user management scenarios:
    - User creation by admins
    - User deletion with soft delete
    - Role-based permissions
    - Organization assignment
    - Publisher privilege management
    """
```

#### 3. Security Tests (`test_security.py`)
```python
class SecurityTestCase(TestCase):
    """
    MUST test ALL security features:
    - Password policy enforcement
    - Rate limiting
    - Session security
    - SQL injection prevention
    - XSS prevention
    - CSRF protection
    """
```

#### 4. Integration Tests (`test_integration.py`)
```python
class IntegrationTestCase(TestCase):
    """
    MUST test integration with existing CRISP components:
    - Organization model integration
    - STIX object permissions
    - TAXII authentication
    - Feed publishing permissions
    """
```

### Test Execution Requirements
**MUST create these test runners:**

```python
# UserManagement/run_auth_tests.py
def run_comprehensive_auth_tests():
    """
    Run all authentication and user management tests.
    MUST achieve 100% pass rate.
    """
```

## 🌐 API ENDPOINTS SPECIFICATION

**MUST implement these EXACT endpoints:**

### Authentication Endpoints
```python
# POST /api/auth/login/          - User login with JWT
# POST /api/auth/logout/         - User logout
# POST /api/auth/refresh/        - Refresh JWT token
# POST /api/auth/verify/         - Verify JWT token
# POST /api/auth/password-reset/ - Request password reset
# POST /api/auth/password-confirm/ - Confirm password reset
# POST /api/auth/change-password/ - Change password
# GET  /api/auth/profile/        - Get user profile
# PUT  /api/auth/profile/        - Update user profile
```

### Admin User Management Endpoints
```python
# GET    /api/admin/users/           - List all users (admin only)
# POST   /api/admin/users/           - Create new user (admin only)
# GET    /api/admin/users/{id}/      - Get user details (admin only)
# PUT    /api/admin/users/{id}/      - Update user (admin only)
# DELETE /api/admin/users/{id}/      - Delete user (admin only)
# POST   /api/admin/users/{id}/unlock/ - Unlock user account (admin only)
```

### Organization Management Endpoints
```python
# GET    /api/admin/organizations/     - List organizations (admin only)
# POST   /api/admin/organizations/     - Create organization (admin only)
# GET    /api/admin/organizations/{id}/ - Get organization (admin only)
# PUT    /api/admin/organizations/{id}/ - Update organization (admin only)
# DELETE /api/admin/organizations/{id}/ - Delete organization (admin only)
```

## 🔒 SECURITY IMPLEMENTATION REQUIREMENTS

### Password Policy
```python
# MUST implement these exact password requirements:
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
```

### Rate Limiting
```python
# MUST implement rate limiting on these endpoints:
@ratelimit(key='ip', rate='5/m', method='POST')  # Login attempts
@ratelimit(key='ip', rate='3/h', method='POST')  # Password reset
@ratelimit(key='user', rate='10/m', method='GET')  # API calls
```

### Session Security
```python
# MUST implement these security settings:
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

## 📊 INTEGRATION WITH EXISTING CRISP COMPONENTS

### STIX Object Permissions
**MUST integrate with existing STIXObject model:**
```python
class STIXObjectPermission(models.Model):
    """
    Permissions for STIX objects based on user roles and organization trust.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stix_object = models.ForeignKey('crisp_threat_intel.STIXObject', on_delete=models.CASCADE)
    permission_level = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    granted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    created_at = models.DateTimeField(auto_now_add=True)
```

### TAXII Authentication Integration
**MUST integrate with existing TAXII endpoints:**
```python
# crisp_threat_intel/taxii/views.py modifications needed
class TaxiiAuthenticationMixin:
    """
    Add JWT authentication support to existing TAXII views.
    """
    def check_authentication(self, request):
        # Integrate with UserManagement authentication
        pass
```

### Feed Publishing Permissions
**MUST integrate with existing Feed model:**
```python
def check_feed_publish_permission(user: CustomUser, feed: 'crisp_threat_intel.Feed') -> bool:
    """
    Check if user has permission to publish feed based on:
    - User role (publisher or admin)
    - Organization ownership of feed collection
    - Trust relationship between organizations
    """
```

## 🚀 DEPLOYMENT AND MIGRATION STRATEGY

### Local Development Setup
1. **Install Local PostgreSQL:**
   ```bash
   # Follow PostgreSQL installation instructions above
   # Create local database with same credentials as Pi
   ```

2. **Local Development:**
   ```bash
   # Create migrations locally
   python manage.py makemigrations UserManagement
   python manage.py migrate
   
   # Run tests locally
   python UserManagement/run_auth_tests.py --all
   ```

3. **Local Testing and Development:**
   ```bash
   # All development and testing done locally
   python manage.py runserver
   # Access at http://localhost:8000
   ```

### Pi Integration (When Pi Comes Back Online)
1. **Switch Database Configuration:**
   ```python
   # In settings.py - Comment out local config:
   # DATABASES = {
   #     'default': {
   #         'ENGINE': 'django.db.backends.postgresql',
   #         'NAME': 'crisp',
   #         'USER': 'admin',
   #         'PASSWORD': 'AdminPassword', 
   #         'HOST': 'localhost',  # Local PostgreSQL
   #         'PORT': '5432',
   #     }
   # }
   
   # Uncomment Pi config:
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'crisp',
           'USER': 'admin', 
           'PASSWORD': 'AdminPassword',
           'HOST': '100.117.251.119',  # Pi host
           'PORT': '5432',
       }
   }
   ```

2. **Pi Deployment:**
   ```bash
   # Use existing sync script when Pi is back online
   ./scripts/sync_migrations.sh
   ```

3. **Pi Testing:**
   ```bash
   # Test migrations and functionality on Pi
   python UserManagement/run_auth_tests.py --all
   ```

### Database Schema Migration
**MUST ensure these migration steps work both locally and on Pi:**
1. Create CustomUser model with foreign key to existing Organization
2. Create UserSession model for JWT management
3. Create AuthenticationLog model for audit trail
4. Update existing models to reference CustomUser instead of Django User
5. Migrate existing User data to CustomUser (if any exists)
6. Ensure all migrations work identically on local PostgreSQL and Pi PostgreSQL

## 🎯 SUCCESS CRITERIA

### Functional Requirements Validation
**ALL of these MUST be implemented and tested:**

✅ **R1.1.1**: Username/password authentication with JWT tokens  
✅ **R1.1.2**: Strong password policies enforced  
✅ **R1.1.3**: Password reset functionality working  
✅ **R1.1.4**: "Remember me" functionality for trusted devices  
✅ **R1.1.5**: Account lockout after 5 failed attempts  
✅ **R1.1.6**: Complete authentication activity logging  
✅ **R1.2.1**: Admin-controlled user registration  
✅ **R1.2.2**: Admin-controlled user deletion  
✅ **R1.2.3**: Publisher-only user registration enforcement  
✅ **R1.2.4**: Comprehensive credential verification  
✅ **R1.3.1**: Admin-controlled organization registration  
✅ **R1.3.2**: Admin-controlled organization deletion  
✅ **R1.3.3**: System admin-only organization management  

### Code Quality Requirements
✅ **Clean Code**: Professional, maintainable code with zero technical debt  
✅ **Design Patterns**: Proper Strategy, Factory, and Observer pattern implementation  
✅ **CRISP Integration**: Perfect integration with existing domain model  
✅ **Database Integration**: Seamless PostgreSQL Pi integration  
✅ **Test Coverage**: 100% test coverage with comprehensive test suite  
✅ **Security**: Production-ready security implementation  
✅ **Documentation**: Complete code documentation and API docs  

### Integration Requirements
✅ **Organization Model**: Perfect integration with existing Organization model  
✅ **STIX Objects**: Proper permissions for STIX object access  
✅ **TAXII API**: JWT authentication for existing TAXII endpoints  
✅ **Feed Publishing**: Role-based feed publishing permissions  
✅ **Anonymization**: Integration with existing anonymization strategies  

## 📚 IMPLEMENTATION NOTES

### Development Approach
1. **Start with Models**: Implement CustomUser, UserSession, AuthenticationLog
2. **Add Authentication**: Implement JWT authentication with security features
3. **Implement Patterns**: Add Strategy, Factory, Observer patterns
4. **Create APIs**: Build all required REST API endpoints
5. **Add Security**: Implement all security features and validations
6. **Write Tests**: Create comprehensive test suite
7. **Integration**: Integrate with existing CRISP components
8. **Documentation**: Complete all documentation

### Critical Integration Points
- **CustomUser.organization**: MUST link to existing Organization model
- **JWT Authentication**: MUST work with existing TAXII endpoints
- **Permissions**: MUST integrate with STIX object access control
- **Audit Logging**: MUST integrate with existing logging infrastructure

### Testing Strategy
- **Unit Tests**: Test each component individually
- **Integration Tests**: Test integration with existing CRISP components
- **Security Tests**: Test all security features thoroughly
- **Performance Tests**: Ensure authentication doesn't impact performance
- **End-to-End Tests**: Test complete user workflows

## 🛡️ FINAL IMPLEMENTATION CHECKLIST

Before considering the implementation complete, verify ALL of these:

### Core Functionality
- [ ] All R1.1.x authentication requirements implemented and tested
- [ ] All R1.2.x user management requirements implemented and tested  
- [ ] All R1.3.x organization management requirements implemented and tested
- [ ] JWT authentication working with all specified features
- [ ] Password policies enforced with custom validators
- [ ] Account lockout working after failed attempts
- [ ] Password reset flow complete and secure
- [ ] Trusted device functionality implemented
- [ ] Complete authentication logging implemented

### Design Patterns
- [ ] Strategy pattern implemented for authentication methods
- [ ] Factory pattern implemented for user creation
- [ ] Observer pattern implemented for authentication events
- [ ] All patterns follow existing CRISP architecture

### Database Integration
- [ ] All models created with proper relationships
- [ ] Migrations created and tested locally
- [ ] Pi PostgreSQL integration working
- [ ] Existing Organization model integration complete
- [ ] Data integrity constraints implemented

### API Implementation
- [ ] All authentication endpoints implemented
- [ ] All admin user management endpoints implemented
- [ ] All organization management endpoints implemented
- [ ] Proper serializers and permissions implemented
- [ ] API documentation complete

### Security Implementation
- [ ] Strong password policies enforced
- [ ] Rate limiting implemented on critical endpoints
- [ ] Session security configured properly
- [ ] CSRF, XSS, and injection prevention implemented
- [ ] Secure headers configured
- [ ] JWT security best practices followed

### Testing
- [ ] 100% test coverage achieved
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All security tests passing
- [ ] Performance tests passing
- [ ] Test runner scripts created

### Integration
- [ ] STIX object permissions working
- [ ] TAXII authentication integration complete
- [ ] Feed publishing permissions implemented
- [ ] Anonymization strategy integration working
- [ ] Observer pattern notifications working

---

## 🚀 START IMPLEMENTATION NOW

**YOU HAVE EVERYTHING YOU NEED TO IMPLEMENT PERFECT USER MANAGEMENT & AUTHENTICATION FOR CRISP!**

Begin with creating the UserManagement folder and implementing the models, then follow the exact structure and requirements outlined above. Every requirement is specified, every pattern is defined, and every integration point is documented.

**IMPLEMENT WITH ABSOLUTE PRECISION AND COMPREHENSIVE TESTING!**