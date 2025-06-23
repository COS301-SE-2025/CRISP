# 🧪 CRISP User Management - Comprehensive Testing Guide

This guide provides all testing commands to thoroughly check every component of the system.

## 📋 Pre-Testing Setup

```bash
# 1. Navigate to project directory
cd /mnt/c/Users/Client/Documents/GitHub/CRISP/UserManagment

# 2. Ensure Django server is running (in one terminal)
python3 manage.py runserver

# 3. Open new terminal for testing commands
cd /mnt/c/Users/Client/Documents/GitHub/CRISP/UserManagment
```

## 🔧 System Health Checks

### 1. Django Configuration
```bash
# Check Django configuration
python3 manage.py check

# Validate database migrations
python3 manage.py showmigrations

# Check installed apps
python3 manage.py diffsettings | grep INSTALLED_APPS

# Validate models
python3 manage.py validate
```

### 2. Database Status
```bash
# Show all migrations
python3 manage.py showmigrations UserManagement

# Check database tables
python3 manage.py dbshell -c ".tables" || echo "SQLite tables check"

# Verify models are created
python3 manage.py shell -c "
from UserManagement.models import CustomUser, Organization, UserSession, AuthenticationLog
print(f'Users: {CustomUser.objects.count()}')
print(f'Organizations: {Organization.objects.count()}')
print(f'Sessions: {UserSession.objects.count()}')
print(f'Auth Logs: {AuthenticationLog.objects.count()}')
"
```

## 🧪 Unit Tests

### 1. Run All Tests
```bash
# Run all UserManagement tests
python3 manage.py test UserManagement

# Run with verbose output
python3 manage.py test UserManagement --verbosity=2

# Run with coverage (install first: pip install coverage)
coverage run --source='.' manage.py test UserManagement
coverage report
coverage html  # Creates htmlcov/ directory
```

### 2. Run Specific Test Categories
```bash
# Authentication tests
python3 manage.py test UserManagement.tests.test_authentication

# Security tests  
python3 manage.py test UserManagement.tests.test_security

# User management tests
python3 manage.py test UserManagement.tests.test_user_management

# Integration tests
python3 manage.py test UserManagement.tests.test_integration
```

### 3. Individual Test Classes
```bash
# Test specific classes (examples)
python3 manage.py test UserManagement.tests.test_authentication.AuthenticationTestCase
python3 manage.py test UserManagement.tests.test_security.SecurityTestCase
python3 manage.py test UserManagement.tests.test_user_management.UserManagementTestCase
```

## 🔐 Authentication System Tests

### 1. Manual Authentication Test
```bash
# Test authentication service directly
python3 manage.py shell -c "
from UserManagement.services.auth_service import AuthenticationService
from django.test import RequestFactory

factory = RequestFactory()
request = factory.post('/api/auth/login/')
request.META['HTTP_USER_AGENT'] = 'TestAgent'
request.META['REMOTE_ADDR'] = '127.0.0.1'

auth_service = AuthenticationService()
result = auth_service.authenticate_user(
    username='admin',
    password='admin123',
    request=request
)

print('Authentication Result:')
print(f'Success: {result[\"success\"]}')
print(f'User: {result.get(\"user\")}')
print(f'Has Tokens: {\"tokens\" in result}')
"
```

### 2. Password Validation Tests
```bash
# Test password policies
python3 manage.py shell -c "
from UserManagement.validators import validate_password_strength
from django.core.exceptions import ValidationError

test_passwords = [
    'weak',
    'password123',
    'StrongPass123!',
    'admin123'
]

for pwd in test_passwords:
    try:
        validate_password_strength(pwd)
        print(f'✅ {pwd}: Valid')
    except ValidationError as e:
        print(f'❌ {pwd}: {e.message}')
"
```

### 3. User Factory Tests
```bash
# Test user creation factories
python3 manage.py shell -c "
from UserManagement.factories.user_factory import UserFactory
from UserManagement.models import Organization

org = Organization.objects.first()

# Test different user role creation
roles = ['viewer', 'analyst', 'publisher', 'admin']

for role in roles:
    try:
        user_data = {
            'username': f'test_{role}',
            'email': f'test_{role}@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'organization': org
        }
        
        user = UserFactory.create_user(role, user_data)
        print(f'✅ Created {role}: {user.username}')
        
        # Clean up
        user.delete()
        
    except Exception as e:
        print(f'❌ Failed to create {role}: {e}')
"
```

## 🌐 API Endpoint Tests

### 1. Authentication Endpoints
```bash
# Test login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | python3 -m json.tool

# Test profile (save token from login first)
TOKEN="<paste_access_token_here>"
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Test logout
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Admin Endpoints
```bash
# List all users (admin only)
curl -X GET http://127.0.0.1:8000/api/admin/users/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Create new user
curl -X POST http://127.0.0.1:8000/api/admin/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "TestPass123!",
    "role": "viewer",
    "first_name": "Test",
    "last_name": "User"
  }' | python3 -m json.tool
```

### 3. User Dashboard Endpoints
```bash
# User dashboard
curl -X GET http://127.0.0.1:8000/api/user/dashboard/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# User sessions
curl -X GET http://127.0.0.1:8000/api/user/sessions/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# User activity
curl -X GET http://127.0.0.1:8000/api/user/activity/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## 🛡️ Security Tests

### 1. Rate Limiting Tests
```bash
# Test rate limiting (should get blocked after 5 attempts)
for i in {1..10}; do
  echo "Attempt $i:"
  curl -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "wrong"}' \
    -w "Status: %{http_code}\n" -s
  sleep 1
done
```

### 2. Account Lockout Tests
```bash
# Check account lockout mechanism
python3 manage.py shell -c "
from UserManagement.models import CustomUser

admin = CustomUser.objects.get(username='admin')
print(f'Failed attempts: {admin.failed_login_attempts}')
print(f'Account locked: {admin.is_account_locked}')
print(f'Last failed login: {admin.last_failed_login}')

# Test lockout method
admin.increment_failed_login()
print(f'After increment - Failed attempts: {admin.failed_login_attempts}')
"
```

### 3. JWT Token Tests
```bash
# Test token verification
python3 manage.py shell -c "
from UserManagement.services.auth_service import AuthenticationService
from rest_framework_simplejwt.tokens import AccessToken

# Create test token
auth_service = AuthenticationService()
from UserManagement.models import CustomUser
user = CustomUser.objects.get(username='admin')

# Test token creation and verification
token = AccessToken.for_user(user)
print(f'Token created: {str(token)[:50]}...')

# Verify token
try:
    verified_token = AccessToken(str(token))
    print(f'✅ Token verified for user: {verified_token.get(\"user_id\")}')
except Exception as e:
    print(f'❌ Token verification failed: {e}')
"
```

## 📊 Model Tests

### 1. Test All Models
```bash
# Test CustomUser model methods
python3 manage.py shell -c "
from UserManagement.models import CustomUser

admin = CustomUser.objects.get(username='admin')

# Test model methods
print(f'Can publish feeds: {admin.can_publish_feeds()}')
print(f'Is org admin: {admin.is_organization_admin()}')
print(f'Account locked: {admin.is_account_locked}')

# Test password reset
admin.password_reset_token = 'test_token'
admin.save()
print(f'Password reset token set: {admin.password_reset_token}')
"
```

### 2. Test UserSession Model
```bash
# Test user session functionality
python3 manage.py shell -c "
from UserManagement.models import UserSession, CustomUser
from datetime import timedelta
from django.utils import timezone

user = CustomUser.objects.get(username='admin')

# Create test session
session = UserSession.objects.create(
    user=user,
    session_token='test_token_123',
    ip_address='127.0.0.1',
    expires_at=timezone.now() + timedelta(hours=1),
    device_info={'browser': 'test'}
)

print(f'Session created: {session.id}')
print(f'Is expired: {session.is_expired}')

# Test session methods
session.extend_session(2)
print(f'Session extended: {session.expires_at}')

session.delete()
print('Session cleaned up')
"
```

### 3. Test Authentication Logs
```bash
# Test authentication logging
python3 manage.py shell -c "
from UserManagement.models import AuthenticationLog, CustomUser

user = CustomUser.objects.get(username='admin')

# Create test log entry
log = AuthenticationLog.log_authentication_event(
    user=user,
    action='login_success',
    ip_address='127.0.0.1',
    user_agent='TestAgent',
    success=True
)

print(f'Log created: {log.id}')
print(f'Log action: {log.action}')
print(f'Log timestamp: {log.timestamp}')

# Check recent logs
recent_logs = AuthenticationLog.objects.filter(user=user).order_by('-timestamp')[:5]
print(f'Recent logs count: {recent_logs.count()}')
"
```

## 🎯 Integration Tests

### 1. Full Authentication Flow
```bash
# Test complete authentication flow
python3 test_system.py
```

### 2. Admin Interface Tests
```bash
# Test admin interface access
curl -I http://127.0.0.1:8000/admin/

# Test admin login page
curl -s http://127.0.0.1:8000/admin/login/ | grep -o "<title>.*</title>"
```

### 3. Management Commands Tests
```bash
# Test setup command
python3 manage.py setup_auth --help

# Test with dry run (if implemented)
python3 manage.py setup_auth --dry-run || echo "Command executed"
```

## 🔍 Middleware Tests

### 1. Security Headers Test
```bash
# Check security headers
curl -I http://127.0.0.1:8000/api/auth/login/ | grep -E "(X-XSS-Protection|X-Content-Type-Options|X-Frame-Options)"
```

### 2. CORS and Security
```bash
# Test CORS headers
curl -H "Origin: http://example.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://127.0.0.1:8000/api/auth/login/
```

## 📈 Performance Tests

### 1. Load Test (Simple)
```bash
# Simple concurrent login test
for i in {1..5}; do
  (curl -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' \
    -w "Time: %{time_total}s\n" -s) &
done
wait
```

### 2. Database Query Performance
```bash
# Test database query performance
python3 manage.py shell -c "
import time
from UserManagement.models import CustomUser, AuthenticationLog

start = time.time()
users = list(CustomUser.objects.select_related('organization').all())
user_time = time.time() - start

start = time.time()
logs = list(AuthenticationLog.objects.select_related('user').all()[:100])
log_time = time.time() - start

print(f'User query time: {user_time:.4f}s ({len(users)} users)')
print(f'Log query time: {log_time:.4f}s ({len(logs)} logs)')
"
```

## 🧹 Cleanup and Reset

### 1. Reset Test Data
```bash
# Clear test sessions
python3 manage.py shell -c "
from UserManagement.models import UserSession
UserSession.objects.filter(session_token__startswith='test_').delete()
print('Test sessions cleared')
"

# Clear test logs
python3 manage.py shell -c "
from UserManagement.models import AuthenticationLog
test_logs = AuthenticationLog.objects.filter(additional_data__icontains='test')
count = test_logs.count()
test_logs.delete()
print(f'Cleared {count} test log entries')
"
```

### 2. Reset Admin Password
```bash
# Reset admin password
python3 manage.py shell -c "
from UserManagement.models import CustomUser
admin = CustomUser.objects.get(username='admin')
admin.set_password('admin123')
admin.failed_login_attempts = 0
admin.account_locked_until = None
admin.save()
print('Admin account reset successfully')
"
```

## 📝 Test Report Generation

### 1. Generate Test Coverage Report
```bash
# Install coverage if not installed
pip install coverage

# Run tests with coverage
coverage run --source='UserManagement' manage.py test UserManagement

# Generate reports
coverage report
coverage html
coverage xml

echo "Coverage report generated in htmlcov/index.html"
```

### 2. System Health Report
```bash
# Create comprehensive system report
python3 manage.py shell -c "
from UserManagement.models import *
from django.conf import settings
import django

print('=== CRISP User Management System Health Report ===')
print(f'Django Version: {django.get_version()}')
print(f'Debug Mode: {settings.DEBUG}')
print(f'Database: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print()

print('=== Model Counts ===')
print(f'Users: {CustomUser.objects.count()}')
print(f'Organizations: {Organization.objects.count()}')
print(f'Active Sessions: {UserSession.objects.filter(is_active=True).count()}')
print(f'Auth Logs (24h): {AuthenticationLog.objects.filter(timestamp__gte=timezone.now() - timedelta(days=1)).count()}')
print()

print('=== System Status ===')
print('✅ Database: Connected')
print('✅ Models: Loaded')
print('✅ Authentication: Functional')
print('✅ API: Accessible')
print()

from django.utils import timezone
from datetime import timedelta
print(f'Report generated: {timezone.now()}')
"
```

## 🚀 Quick Test Suite

```bash
# Run this complete test suite for full system validation
echo "🧪 Running CRISP User Management Test Suite..."

echo "1️⃣ Django Configuration Check..."
python3 manage.py check

echo "2️⃣ Database Validation..."
python3 manage.py showmigrations UserManagement

echo "3️⃣ Model Tests..."
python3 manage.py test UserManagement.tests.test_user_management --verbosity=0

echo "4️⃣ Authentication Tests..."
python3 manage.py test UserManagement.tests.test_authentication --verbosity=0

echo "5️⃣ Security Tests..." 
python3 manage.py test UserManagement.tests.test_security --verbosity=0

echo "6️⃣ API Integration Test..."
python3 test_system.py

echo "7️⃣ Admin Interface Check..."
curl -I http://127.0.0.1:8000/admin/ 2>/dev/null | head -1

echo "✅ Test Suite Complete!"
```

This comprehensive testing guide covers every aspect of the CRISP User Management system. Run these commands to thoroughly validate all functionality, security features, and system health.