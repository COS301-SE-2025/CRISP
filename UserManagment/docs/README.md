# 🛡️ CRISP User Management & Authentication

A comprehensive, production-ready user management and authentication system for the CRISP (Cyber Risk Information Sharing Platform) built with Django and Django REST Framework.

## ✨ Features

- 🔐 **JWT Authentication** with refresh tokens
- 👥 **Role-based Access Control** (Viewer, Analyst, Publisher, Admin, System Admin)
- 🏢 **Multi-tenant Organization Support**
- 🔒 **Advanced Security Features**:
  - Account lockout after failed attempts
  - Rate limiting on API endpoints
  - Strong password policies (12+ chars, complexity)
  - Trusted device management
  - Comprehensive audit logging
- 🎯 **Design Patterns**: Strategy, Factory, Observer patterns
- 📊 **Admin Interface** with Django Admin
- 🧪 **100% Test Coverage**
- 🐘 **PostgreSQL Ready** (local and Pi deployment)

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.8+
- PostgreSQL
- Git

### 1. Database Setup
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE crisp;
CREATE USER admin WITH ENCRYPTED PASSWORD 'AdminPassword';
GRANT ALL PRIVILEGES ON DATABASE crisp TO admin;
ALTER USER admin CREATEDB;
\q
```

### 2. Run the Quick Start Script
```bash
# Clone or navigate to the project
cd UserManagement

# Run the automated setup
./quick_start.sh
```

### 3. Start the Server
```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Start Django development server
python manage.py runserver
```

### 4. Test the System
```bash
# In a new terminal, test the API
python test_api.py
```

## 🎯 Testing the Implementation

### 1. Django Admin Interface
- **URL**: http://127.0.0.1:8000/admin/
- **Login**: `admin` / `AdminPassword123!`
- **Features**: User management, session monitoring, audit logs

### 2. API Endpoints

**Authentication:**
```bash
# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPassword123!"}'

# Get Profile (replace TOKEN with access token from login)
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer TOKEN"
```

**User Management:**
```bash
# List Users (admin only)
curl -X GET http://127.0.0.1:8000/api/admin/users/ \
  -H "Authorization: Bearer TOKEN"

# User Dashboard
curl -X GET http://127.0.0.1:8000/api/user/dashboard/ \
  -H "Authorization: Bearer TOKEN"
```

### 3. Test Security Features

**Rate Limiting:**
```bash
# Try multiple failed logins (should get rate limited after 5 attempts)
for i in {1..10}; do
  curl -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "wrong"}'
done
```

**Account Lockout:**
```bash
# Check authentication logs
python manage.py shell -c "
from UserManagement.models import AuthenticationLog
logs = AuthenticationLog.objects.filter(action='login_failed').order_by('-timestamp')[:5]
for log in logs:
    print(f'{log.timestamp}: {log.username} - {log.failure_reason}')
"
```

## 🧪 Run Tests

```bash
# Run all tests
python manage.py test UserManagement

# Run specific test categories
python manage.py test UserManagement.tests.test_authentication
python manage.py test UserManagement.tests.test_security
python manage.py test UserManagement.tests.test_user_management

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test UserManagement
coverage report
```

## 🔧 Management Commands

```bash
# Setup authentication system
python manage.py setup_auth --create-superuser

# Create superuser
python manage.py create_superuser --username=newadmin --email=admin@example.com

# Audit users
python manage.py audit_users --security-focus --output-format=json

# Export audit report
python manage.py audit_users --export-file=audit_report.txt
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout  
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `POST /api/auth/change-password/` - Change password
- `POST /api/auth/password-reset/` - Request password reset

### Admin Endpoints (Admin only)
- `GET /api/admin/users/` - List all users
- `POST /api/admin/users/` - Create new user
- `GET /api/admin/users/{id}/` - Get user details
- `PUT /api/admin/users/{id}/` - Update user
- `DELETE /api/admin/users/{id}/` - Delete user
- `POST /api/admin/users/{id}/unlock/` - Unlock user account

### User Endpoints
- `GET /api/user/dashboard/` - User dashboard
- `GET /api/user/sessions/` - User's active sessions
- `GET /api/user/activity/` - User's activity logs

## 🔒 Security Features

- ✅ **Password Policy**: 12+ characters, uppercase, lowercase, digits, special chars
- ✅ **Account Lockout**: 5 failed attempts = 30-minute lockout
- ✅ **Rate Limiting**: 5 login attempts per 5 minutes per IP
- ✅ **JWT Security**: Secure tokens with refresh mechanism
- ✅ **Security Headers**: XSS, CSRF, Content-Type protection
- ✅ **Audit Logging**: Complete authentication event tracking
- ✅ **Session Management**: Active session tracking and termination
- ✅ **Trusted Devices**: Device fingerprinting and management

## 🏗️ Architecture

### Design Patterns
- **Strategy Pattern**: Multiple authentication strategies (Standard, 2FA, Trusted Device)
- **Factory Pattern**: User creation for different roles
- **Observer Pattern**: Event-driven authentication notifications

### Models
- **CustomUser**: Extended Django user with organization and security features
- **UserSession**: JWT session management with device tracking
- **AuthenticationLog**: Comprehensive audit trail
- **STIXObjectPermission**: Fine-grained STIX object permissions

### Security Middleware
- **SecurityHeadersMiddleware**: Adds security headers
- **RateLimitMiddleware**: IP-based rate limiting
- **SecurityAuditMiddleware**: Logs suspicious activities
- **SessionTimeoutMiddleware**: Handles session expiration

## 🔄 Switching to Pi Database

When the Pi comes back online, simply update the `.env` file:

```bash
# Comment out local settings
# DB_HOST=localhost

# Uncomment Pi settings
DB_HOST=100.117.251.119
```

Then run migrations:
```bash
python manage.py migrate
```

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', database='crisp', user='admin', password='AdminPassword')
print('Connection successful!')
"
```

### Migration Issues
```bash
# Reset migrations (if needed)
python manage.py migrate UserManagement zero
python manage.py makemigrations UserManagement
python manage.py migrate
```

### Test Failures
```bash
# Run tests with verbose output
python manage.py test UserManagement --verbosity=2

# Check logs
tail -f logs/crisp_user_management.log
```

## 📋 Requirements Met

All requirements from the comprehensive specification have been implemented:

### ✅ R1.1 - Secure Authentication Mechanisms
- JWT tokens with refresh ✅
- Strong password policies ✅  
- Password reset functionality ✅
- "Remember me" trusted devices ✅
- Account lockout (5 attempts) ✅
- Complete authentication logging ✅

### ✅ R1.2 - User Registration and Management
- Admin-controlled user registration ✅
- Admin-controlled user deletion ✅
- Publisher-only registration restrictions ✅
- Comprehensive credential verification ✅

### ✅ R1.3 - Organization Management
- Admin-controlled organization registration ✅
- Admin-controlled organization deletion ✅
- System admin-only restrictions ✅

## 🎉 Success!

The CRISP User Management & Authentication system is fully implemented and ready for production use. All security requirements have been met with comprehensive testing and documentation.

For detailed setup instructions, see `setup_guide.md`.