# 🧪 CRISP User Management - Testing Commands Summary

## 🚀 Quick Test Commands (Essential)

### 1. File Structure Validation
```bash
# Check all files exist and have valid syntax
python3 validate_files.py
```

### 2. Complete Test Suite
```bash
# Run all tests with summary report
./run_all_tests.sh
```

### 3. System Integration Test
```bash
# Test complete authentication flow
python3 test_system.py
```

### 4. Django Health Check
```bash
# Validate Django configuration
python3 manage.py check
```

## 🧪 Unit Testing Commands

### Run All Tests
```bash
# All UserManagement tests
python3 manage.py test UserManagement

# With verbose output
python3 manage.py test UserManagement --verbosity=2

# Specific test categories
python3 manage.py test UserManagement.tests.test_authentication
python3 manage.py test UserManagement.tests.test_security
python3 manage.py test UserManagement.tests.test_user_management
python3 manage.py test UserManagement.tests.test_integration
```

### Test Coverage
```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run --source='UserManagement' manage.py test UserManagement
coverage report
coverage html  # Creates htmlcov/ directory
```

## 🌐 API Testing Commands

### Authentication API
```bash
# Test login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test profile (replace TOKEN)
TOKEN="your_access_token_here"
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer $TOKEN"
```

### Admin API
```bash
# List users (admin only)
curl -X GET http://127.0.0.1:8000/api/admin/users/ \
  -H "Authorization: Bearer $TOKEN"

# User dashboard
curl -X GET http://127.0.0.1:8000/api/user/dashboard/ \
  -H "Authorization: Bearer $TOKEN"
```

## 🛡️ Security Testing Commands

### Rate Limiting Test
```bash
# Test rate limiting (should get blocked after attempts)
for i in {1..10}; do
  curl -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "wrong"}'
  sleep 1
done
```

### Security Headers Check
```bash
# Check security headers
curl -I http://127.0.0.1:8000/api/auth/login/ | grep -E "(X-XSS-Protection|X-Content-Type-Options|X-Frame-Options)"
```

## 🗄️ Database Testing Commands

### Model Validation
```bash
# Check database status
python3 manage.py showmigrations UserManagement

# Test models directly
python3 manage.py shell -c "
from UserManagement.models import CustomUser, Organization, UserSession, AuthenticationLog
print(f'Users: {CustomUser.objects.count()}')
print(f'Organizations: {Organization.objects.count()}')
print(f'Sessions: {UserSession.objects.count()}')
print(f'Auth Logs: {AuthenticationLog.objects.count()}')
"
```

### Authentication Service Test
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

print(f'Authentication Success: {result[\"success\"]}')
print(f'User: {result.get(\"user\")}')
"
```

## 🎯 Component Testing Commands

### Test User Factory
```bash
python3 manage.py shell -c "
from UserManagement.factories.user_factory import UserFactory
from UserManagement.models import Organization

org = Organization.objects.first()
user_data = {
    'username': 'test_user',
    'email': 'test@example.com',
    'password': 'TestPass123!',
    'organization': org
}

try:
    user = UserFactory.create_user('viewer', user_data)
    print(f'✅ User created: {user.username}')
    user.delete()  # Cleanup
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### Test Password Validation
```bash
python3 manage.py shell -c "
from UserManagement.validators import validate_password_strength
from django.core.exceptions import ValidationError

test_passwords = ['weak', 'password123', 'StrongPass123!']

for pwd in test_passwords:
    try:
        validate_password_strength(pwd)
        print(f'✅ {pwd}: Valid')
    except ValidationError as e:
        print(f'❌ {pwd}: {e.message}')
"
```

### Test JWT Tokens
```bash
python3 manage.py shell -c "
from rest_framework_simplejwt.tokens import AccessToken
from UserManagement.models import CustomUser

user = CustomUser.objects.get(username='admin')
token = AccessToken.for_user(user)
print(f'Token created: {str(token)[:50]}...')

# Verify token
try:
    verified = AccessToken(str(token))
    print(f'✅ Token verified for user: {verified.get(\"user_id\")}')
except Exception as e:
    print(f'❌ Token verification failed: {e}')
"
```

## 🔧 Admin Interface Testing

### Admin Access Test
```bash
# Test admin interface
curl -I http://127.0.0.1:8000/admin/

# Test admin login page
curl -s http://127.0.0.1:8000/admin/login/ | grep -o "<title>.*</title>"
```

## 📊 Performance Testing Commands

### Simple Load Test
```bash
# Test concurrent requests
for i in {1..5}; do
  (curl -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' \
    -w "Time: %{time_total}s\n" -s) &
done
wait
```

### Database Performance
```bash
python3 manage.py shell -c "
import time
from UserManagement.models import CustomUser, AuthenticationLog

start = time.time()
users = list(CustomUser.objects.select_related('organization').all())
user_time = time.time() - start

start = time.time()
logs = list(AuthenticationLog.objects.select_related('user').all()[:100])
log_time = time.time() - start

print(f'User query: {user_time:.4f}s ({len(users)} users)')
print(f'Log query: {log_time:.4f}s ({len(logs)} logs)')
"
```

## 🧹 Maintenance Commands

### Reset Test Environment
```bash
# Reset admin password
python3 manage.py shell -c "
from UserManagement.models import CustomUser
admin = CustomUser.objects.get(username='admin')
admin.set_password('admin123')
admin.failed_login_attempts = 0
admin.account_locked_until = None
admin.save()
print('Admin account reset')
"

# Clear test data
python3 manage.py shell -c "
from UserManagement.models import UserSession, AuthenticationLog
UserSession.objects.filter(session_token__startswith='test_').delete()
print('Test sessions cleared')
"
```

### Generate System Report
```bash
python3 manage.py shell -c "
from UserManagement.models import *
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import django

print('=== CRISP System Health Report ===')
print(f'Django Version: {django.get_version()}')
print(f'Debug Mode: {settings.DEBUG}')
print(f'Database: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print()
print('=== Model Counts ===')
print(f'Users: {CustomUser.objects.count()}')
print(f'Organizations: {Organization.objects.count()}')
print(f'Active Sessions: {UserSession.objects.filter(is_active=True).count()}')
print(f'Recent Auth Logs: {AuthenticationLog.objects.filter(timestamp__gte=timezone.now() - timedelta(days=1)).count()}')
print()
print(f'Report generated: {timezone.now()}')
"
```

## 🎯 One-Command Test Everything

```bash
# Ultimate test command - run everything
echo "🧪 Running Complete CRISP Test Suite..." && \
python3 validate_files.py && \
echo -e "\n🔧 Running Django checks..." && \
python3 manage.py check && \
echo -e "\n🧪 Running unit tests..." && \
python3 manage.py test UserManagement --verbosity=0 && \
echo -e "\n🌐 Testing API..." && \
python3 test_system.py && \
echo -e "\n✅ All tests completed successfully!"
```

## 📱 Test Credentials

### Default Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: System Administrator
- **Organization**: CRISP Organization

### Test API Token
```bash
# Get access token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['tokens']['access'])")

echo "Access Token: $TOKEN"
```

## 📋 Testing Checklist

- [ ] File structure validation passes
- [ ] Django configuration check passes
- [ ] All unit tests pass
- [ ] API authentication works
- [ ] Admin interface accessible
- [ ] Security headers present
- [ ] Rate limiting functional
- [ ] Database queries optimized
- [ ] JWT tokens working
- [ ] All models functional

---

**📖 For detailed testing instructions, see: `COMPREHENSIVE_TESTING_GUIDE.md`**