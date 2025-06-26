# 🛡️ CRISP User Management System - Comprehensive User Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Installation & Setup](#installation--setup)
4. [User Roles & Permissions](#user-roles--permissions)
5. [Authentication & Security](#authentication--security)
6. [API Reference](#api-reference)
7. [Admin Interface](#admin-interface)
8. [Testing & Validation](#testing--validation)
9. [Database Management](#database-management)
10. [Configuration](#configuration)
11. [Troubleshooting](#troubleshooting)
12. [Security Best Practices](#security-best-practices)

---

## System Overview

The CRISP (Cyber Risk Information Sharing Platform) User Management System is a comprehensive Django-based authentication and authorization platform designed for cybersecurity threat intelligence sharing. It provides secure user management with multi-organizational support, role-based access control, and comprehensive audit logging.

### Key Features
- **Multi-tenant Organization Support**: Users belong to organizations with domain-based validation
- **Role-Based Access Control**: Three-tier role system (Viewer, Publisher, BlueVision Admin)
- **Enterprise Security**: Account lockout, failed login tracking, session management
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Comprehensive Audit Logging**: All authentication events tracked and logged
- **STIX Object Permissions**: Fine-grained permissions for threat intelligence data
- **RESTful API**: Complete REST API for integration with frontend applications
- **Security Middleware**: Rate limiting, security headers, session management

---

## Architecture & Technology Stack

### Backend Framework
- **Django 4.2.23**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Primary database
- **JWT (Simple JWT)**: Token-based authentication
- **Python 3.8+**: Programming language

### Security Components
- Custom middleware for rate limiting and security headers
- Account lockout mechanism (5 failed attempts = 30-minute lockout)
- Session management with device tracking
- Password validation with complexity requirements
- CSRF protection and XSS prevention

### Database Models
- **CustomUser**: Extended Django user with organization affiliation
- **Organization**: Multi-tenant organization management
- **UserSession**: JWT session tracking with device fingerprinting
- **AuthenticationLog**: Comprehensive audit trail
- **STIXObjectPermission**: Granular permissions for threat intelligence

---

## Installation & Setup

### Prerequisites
```bash
# Python 3.8+
python3 --version

# PostgreSQL (optional - can use SQLite for development)
psql --version

# Git
git --version
```

### Quick Setup
```bash
# 1. Clone and navigate to the project
cd /path/to/CRISP/UserManagment

# 2. Install dependencies (if needed)
pip install django djangorestframework djangorestframework-simplejwt psycopg2-binary python-dotenv

# 3. Set up database
python3 manage.py migrate

# 4. Create superuser
python3 manage.py createsuperuser

# 5. Start the development server
python3 manage.py runserver
```

### Environment Configuration
The system uses `.env` file for configuration:

```bash
# Development Mode
DEBUG=True
SECRET_KEY=crisp-local-development-secret-key-change-in-production

# Database Configuration
DB_NAME=crisp
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Security Settings
ALLOWED_HOSTS=localhost,127.0.0.1
LOGIN_ATTEMPTS_LIMIT=5
RATELIMIT_ENABLE=True
```

---

## User Roles & Permissions

### Role Hierarchy

#### 1. Viewer (`viewer`)
- **Default role** for new users
- **Permissions**: Read-only access to threat intelligence
- **Capabilities**:
  - View STIX objects they have permissions for
  - Access user dashboard
  - View organization users (if same organization)

#### 2. Publisher (`publisher`)
- **Enhanced role** for content creators
- **Permissions**: Read/write access to threat intelligence
- **Capabilities**:
  - All Viewer permissions
  - Create and publish threat intelligence feeds
  - Edit STIX objects they created
  - Grant read permissions to other users

#### 3. BlueVision Admin (`BlueVisionAdmin`)
- **Administrative role** within organization
- **Permissions**: Full administrative access within organization
- **Capabilities**:
  - All Publisher permissions
  - Manage users within their organization
  - Grant/revoke permissions for STIX objects
  - View audit logs for their organization
  - Unlock user accounts

### Permission Matrix

| Action | Viewer | Publisher | BlueVision Admin |
|--------|--------|-----------|------------------|
| View STIX Objects | ✅ (with permission) | ✅ | ✅ |
| Create STIX Objects | ❌ | ✅ | ✅ |
| Edit Own STIX Objects | ❌ | ✅ | ✅ |
| Manage Organization Users | ❌ | ❌ | ✅ |
| View Audit Logs | ❌ | ❌ | ✅ |
| Grant Permissions | ❌ | ✅ (read only) | ✅ (all) |

---

## Authentication & Security

### Login Process
```bash
# Login endpoint
POST /api/auth/login/
{
    "username": "your_username",
    "password": "your_password"
}

# Successful response
{
    "message": "Login successful",
    "user": {
        "id": "uuid",
        "username": "your_username",
        "role": "viewer",
        "organization": "Your Organization"
    },
    "tokens": {
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token"
    }
}
```

### Security Features

#### Account Lockout
- **Threshold**: 5 failed login attempts
- **Lockout Duration**: 30 minutes
- **Auto-unlock**: Account automatically unlocks after duration
- **Manual unlock**: Admins can unlock accounts via API

#### Session Management
- **JWT Tokens**: Access tokens valid for 60 minutes
- **Refresh Tokens**: Valid for 7 days with rotation
- **Device Tracking**: Each session tracks device information
- **IP Logging**: Login IP addresses recorded for audit

#### Password Requirements
- **Minimum Length**: 12 characters
- **Complexity**: Must include:
  - 1+ uppercase letter
  - 1+ lowercase letter
  - 2+ digits
  - 1+ special character

### Default Credentials
```bash
# Admin Account (created during setup)
Username: admin
Password: admin123  # Change immediately in production!

# Test Accounts (for development)
Username: viewer_user
Password: ViewerPass123!

Username: publisher_user
Password: PublisherPass123!
```

---

## API Reference

### Base URL
```
http://127.0.0.1:8000/api/
```

### Authentication Required
Most endpoints require JWT token in Authorization header:
```bash
Authorization: Bearer <your_jwt_token>
```

### Core Endpoints

#### Authentication Endpoints
```bash
# Login
POST /api/auth/login/
Body: {"username": "user", "password": "pass"}

# Logout
POST /api/auth/logout/
Headers: Authorization: Bearer <token>

# Get Profile
GET /api/auth/profile/
Headers: Authorization: Bearer <token>

# Refresh Token
POST /api/auth/refresh/
Body: {"refresh": "refresh_token"}

# Change Password
POST /api/auth/change-password/
Body: {"old_password": "old", "new_password": "new"}

# Password Reset Request
POST /api/auth/password-reset/
Body: {"email": "user@example.com"}

# Password Reset Confirm
POST /api/auth/password-reset-confirm/
Body: {"token": "reset_token", "new_password": "new_pass"}
```

#### Admin Endpoints (BlueVision Admin only)
```bash
# List Users
GET /api/admin/users/
Headers: Authorization: Bearer <admin_token>

# Create User
POST /api/admin/users/
Body: {
    "username": "newuser",
    "email": "user@org.com",
    "password": "SecurePass123!",
    "role": "viewer",
    "organization": "org_id"
}

# Get User Details
GET /api/admin/users/{user_id}/
Headers: Authorization: Bearer <admin_token>

# Update User
PUT /api/admin/users/{user_id}/
Body: {"role": "publisher", "is_publisher": true}

# Unlock User Account
POST /api/admin/users/{user_id}/unlock/
Headers: Authorization: Bearer <admin_token>

# View Authentication Logs
GET /api/admin/logs/
Headers: Authorization: Bearer <admin_token>

# View Active Sessions
GET /api/admin/sessions/
Headers: Authorization: Bearer <admin_token>

# Terminate Session
DELETE /api/admin/sessions/{session_id}/
Headers: Authorization: Bearer <admin_token>
```

#### User Endpoints
```bash
# User Dashboard
GET /api/user/dashboard/
Headers: Authorization: Bearer <token>

# User Sessions
GET /api/user/sessions/
Headers: Authorization: Bearer <token>

# User Activity Log
GET /api/user/activity/
Headers: Authorization: Bearer <token>

# User Statistics
GET /api/user/stats/
Headers: Authorization: Bearer <token>

# Organization Users
GET /api/user/organization-users/
Headers: Authorization: Bearer <token>

# Search Users
GET /api/user/search/?q=search_term
Headers: Authorization: Bearer <token>
```

### Example API Usage

#### Complete Login Flow
```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Use token for authenticated request
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. Refresh token when needed
curl -X POST http://127.0.0.1:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

---

## Admin Interface

### Django Admin Access
- **URL**: `http://127.0.0.1:8000/admin/`
- **Username**: `admin`
- **Password**: `admin123`

### Admin Capabilities
- **User Management**: Create, edit, delete users
- **Organization Management**: Manage organizations and domains
- **Session Monitoring**: View and terminate active sessions
- **Audit Logs**: Review authentication and security events
- **Permission Management**: Grant/revoke STIX object permissions

### Admin Web Interface Features
- User search and filtering
- Bulk user operations
- Organization user overview
- Security event monitoring
- Session management dashboard

---

## Testing & Validation

### Automated Test Suite
```bash
# Run all tests
./run_all_tests.sh

# Individual test modules
python3 manage.py test UserManagement.tests.test_authentication
python3 manage.py test UserManagement.tests.test_user_management
python3 manage.py test UserManagement.tests.test_security
python3 manage.py test UserManagement.tests.test_integration
```

### Quick System Test
```bash
# Test basic functionality
python3 test_system.py

# Test with curl
python3 test_login_curl.sh

# Test admin functionality
python3 test_admin_functionality.py
```

### Test Accounts
```bash
# Admin Account
Username: admin
Password: admin123
Role: BlueVision Admin

# Test Viewer
Username: test_viewer
Password: ViewerPass123!
Role: Viewer

# Test Publisher  
Username: test_publisher
Password: PublisherPass123!
Role: Publisher
```

### Validation Checklist
- [ ] Server starts without errors
- [ ] Admin login works
- [ ] JWT tokens generate correctly
- [ ] Account lockout functions properly
- [ ] Password reset flow works
- [ ] API endpoints respond correctly
- [ ] Database migrations applied
- [ ] Security middleware active

---

## Database Management

### Database Schema
The system uses PostgreSQL with the following key tables:

#### Core Tables
- `UserManagement_customuser`: User accounts with organization affiliation
- `UserManagement_organization`: Organization/tenant management
- `UserManagement_usersession`: Active JWT sessions
- `UserManagement_authenticationlog`: Security audit trail
- `UserManagement_stixobjectpermission`: Granular permissions

### Common Database Operations
```bash
# Create migrations
python3 manage.py makemigrations

# Apply migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Database shell
python3 manage.py dbshell

# Django shell for data manipulation
python3 manage.py shell
```

### Sample Data Creation
```python
# In Django shell (python3 manage.py shell)
from UserManagement.models import Organization, CustomUser

# Create organization
org = Organization.objects.create(
    name="Example Corp",
    domain="example.com",
    description="Example organization"
)

# Create user
user = CustomUser.objects.create_user(
    username="john_doe",
    email="john@example.com",
    password="SecurePass123!",
    organization=org,
    role="viewer"
)
```

---

## Configuration

### Environment Variables
```bash
# Core Settings
DEBUG=True|False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=comma,separated,hosts

# Database
DB_NAME=database_name
DB_USER=db_username
DB_PASSWORD=db_password
DB_HOST=localhost
DB_PORT=5432

# Security
LOGIN_ATTEMPTS_LIMIT=5
RATELIMIT_ENABLE=True
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Email (for password reset)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Security Configuration
```python
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
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
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

---

## Troubleshooting

### Common Issues

#### 1. Line Ending Issues (Windows/WSL)
```bash
# Error: /bin/bash^M: bad interpreter
# Solution:
dos2unix run_all_tests.sh
dos2unix quick_start.sh
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status
sudo service postgresql status

# Reset database
python3 manage.py flush
python3 manage.py migrate
```

#### 3. JWT Token Issues
```bash
# Clear token blacklist
python3 manage.py shell
>>> from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
>>> OutstandingToken.objects.all().delete()
```

#### 4. Permission Denied Errors
```bash
# Make scripts executable
chmod +x run_all_tests.sh
chmod +x quick_start.sh
chmod +x test_login_curl.sh
```

#### 5. Port Already in Use
```bash
# Kill process on port 8000
sudo lsof -t -i tcp:8000 | xargs kill -9

# Use different port
python3 manage.py runserver 8001
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run with verbose output
python3 manage.py runserver --verbosity=2
```

### Log Files
```bash
# View Django logs
tail -f /path/to/logs/django.log

# Check authentication logs via API
curl -X GET http://127.0.0.1:8000/api/admin/logs/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Security Best Practices

### Production Deployment
1. **Change Default Credentials**: Update all default passwords
2. **Environment Variables**: Use secure environment variable management
3. **HTTPS Only**: Enable SSL/TLS with proper certificates
4. **Database Security**: Use strong database passwords and restricted access
5. **Rate Limiting**: Enable and configure rate limiting
6. **Log Monitoring**: Set up log aggregation and monitoring
7. **Regular Updates**: Keep dependencies updated

### Security Monitoring
- Monitor failed login attempts
- Track unusual access patterns
- Review audit logs regularly
- Set up alerts for security events
- Regular security assessments

### API Security
- Always use HTTPS in production
- Implement proper CORS policies
- Validate all input data
- Use strong JWT secrets
- Implement proper session management
- Regular token rotation

---

## Quick Reference Commands

### Development Workflow
```bash
# Start development server
python3 manage.py runserver

# Run tests
./run_all_tests.sh

# Test login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Create new user
curl -X POST http://127.0.0.1:8000/api/admin/users/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "user@org.com", "password": "SecurePass123!"}'
```

### Production Commands
```bash
# Collect static files
python3 manage.py collectstatic

# Run with Gunicorn
gunicorn crisp_project.wsgi:application

# Database backup
pg_dump crisp > backup.sql

# Database restore
psql crisp < backup.sql
```

---

## Support & Documentation

### Additional Resources
- `/docs/README.md` - Detailed technical documentation
- `/docs/QUICK_START.md` - Quick setup guide
- `/docs/COMPREHENSIVE_TESTING_GUIDE.md` - Complete testing procedures
- `CRISP_USER_GUIDE.txt` - Original user guide

### API Documentation
- **API Root**: `GET /api/` - Lists all available endpoints
- **OpenAPI Schema**: Available via Django REST Framework
- **Interactive Testing**: Use Django REST Framework browsable API

### Getting Help
For technical support or questions about the CRISP User Management System:
1. Review this user guide
2. Check the troubleshooting section
3. Review log files for error details
4. Test with the provided test scripts
5. Consult the additional documentation in `/docs/`

---

*Last Updated: June 2025*
*CRISP User Management System v1.0*