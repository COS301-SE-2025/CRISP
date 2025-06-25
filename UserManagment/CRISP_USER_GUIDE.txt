===============================================================================
                    CRISP USER MANAGEMENT SYSTEM - COMPLETE USER GUIDE
===============================================================================

TABLE OF CONTENTS
=================
1. System Overview
2. Technology Stack & Architecture
3. Installation & Setup
4. Creating Institutions (Organizations)
5. User Management & Roles
6. Authentication & Security
7. API Usage
8. Testing & Validation
9. Administrative Functions
10. Troubleshooting

===============================================================================
1. SYSTEM OVERVIEW
===============================================================================

The CRISP (Cyber Risk Information Sharing Platform) User Management System is
a comprehensive Django-based application designed for secure user authentication,
authorization, and management in cybersecurity environments.

KEY FEATURES:
- Multi-tenant organization support
- Role-based access control (RBAC)
- Advanced authentication strategies
- Comprehensive audit logging
- STIX object permission management
- RESTful API interface
- Enterprise-grade security controls

SUPPORTED ROLES HIERARCHY:
- viewer (lowest privileges)
- analyst
- publisher
- admin
- system_admin (highest privileges)

===============================================================================
2. TECHNOLOGY STACK & ARCHITECTURE
===============================================================================

DJANGO-BASED ARCHITECTURE:
Yes, the functionality is PURELY in Django with these components:

CORE DJANGO COMPONENTS:
- Django 4.x Framework
- Django REST Framework (DRF) for APIs
- Django ORM for database operations
- Django Admin for administrative interface
- Django Authentication System (extended)

CUSTOM DJANGO APPLICATIONS:
- UserManagement app (main application)
- Custom models extending Django's User model
- Custom middleware for security
- Custom validators and permissions
- Custom management commands

DATABASE:
- SQLite (default, for development)
- PostgreSQL/MySQL (recommended for production)
- All operations through Django ORM

SECURITY FEATURES:
- JWT token authentication
- Django's built-in CSRF protection
- Custom security middleware
- Rate limiting
- Password validation

API LAYER:
- Django REST Framework serializers
- ViewSets and API views
- Token-based authentication
- Permission classes

NO EXTERNAL SERVICES REQUIRED:
- No microservices
- No external authentication providers
- Self-contained Django application
- Can run entirely offline

===============================================================================
3. INSTALLATION & SETUP
===============================================================================

SYSTEM REQUIREMENTS:
- Python 3.8+
- Django 4.x
- See requirements.txt for full dependencies

INSTALLATION STEPS:

1. Clone/Navigate to the project:
   cd /path/to/CRISP/UserManagment

2. Install dependencies:
   pip install -r requirements.txt

3. Run database migrations:
   python3 manage.py makemigrations
   python3 manage.py migrate

4. Create superuser (system administrator):
   python3 manage.py createsuperuser
   
   Follow prompts to create:
   - Username
   - Email
   - Password

5. Start the development server:
   python3 manage.py runserver

6. Access the system:
   - Web Interface: http://127.0.0.1:8000/
   - Admin Interface: http://127.0.0.1:8000/admin/
   - API Base: http://127.0.0.1:8000/api/

INITIAL SETUP VERIFICATION:
   python3 manage.py test
   ./run_all_tests.sh

===============================================================================
4. CREATING INSTITUTIONS (ORGANIZATIONS)
===============================================================================

Organizations represent institutions, companies, or entities in the system.
Each user belongs to exactly one organization.

METHOD 1: DJANGO ADMIN INTERFACE (Recommended for beginners)
------------------------------------------------------------

1. Access admin interface:
   http://127.0.0.1:8000/admin/

2. Login with superuser credentials

3. Navigate to "Organizations" section

4. Click "Add Organization"

5. Fill required fields:
   - Name: Institution name (e.g., "ACME Cybersecurity Corp")
   - Domain: Email domain (e.g., "acmecyber.com")
   - Description: Optional description
   - Is Active: Check this box (default)

6. Click "Save"

METHOD 2: DJANGO SHELL (Programmatic)
--------------------------------------

1. Access Django shell:
   python3 manage.py shell

2. Create organization:
   from UserManagement.models import Organization
   
   # Method A: Direct creation
   org = Organization.objects.create(
       name="CyberDefense Institute",
       domain="cyberdef.org",
       description="Leading cybersecurity research institution"
   )
   print(f"Created organization: {org.name} with ID: {org.id}")
   
   # Method B: Safe creation (prevents duplicates)
   org, created = Organization.objects.get_or_create(
       name="Threat Intelligence Corp",
       defaults={
           'domain': 'threatintel.com',
           'description': 'Commercial threat intelligence provider'
       }
   )
   print(f"Organization: {org.name} ({'created' if created else 'already exists'})")

3. Exit shell:
   exit()

METHOD 3: MANAGEMENT COMMAND (Create this for easy use)
-------------------------------------------------------

Create file: UserManagement/management/commands/create_org.py

from django.core.management.base import BaseCommand
from UserManagement.models import Organization

class Command(BaseCommand):
    help = 'Create a new organization'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Organization name')
        parser.add_argument('domain', type=str, help='Organization domain')
        parser.add_argument('--description', type=str, help='Organization description')

    def handle(self, *args, **options):
        try:
            org, created = Organization.objects.get_or_create(
                name=options['name'],
                defaults={
                    'domain': options['domain'],
                    'description': options.get('description', '')
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created: {org.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Exists: {org.name}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

Usage:
python3 manage.py create_org "ACME Security" "acme.com" --description="Enterprise security"

VIEWING ORGANIZATIONS:
---------------------

Django Shell:
from UserManagement.models import Organization

# List all organizations
for org in Organization.objects.all():
    print(f"Name: {org.name}, Domain: {org.domain}, Users: {org.customuser_set.count()}")

Admin Interface:
- Go to http://127.0.0.1:8000/admin/
- Click "Organizations" to view all

===============================================================================
5. USER MANAGEMENT & ROLES
===============================================================================

ROLE HIERARCHY (from lowest to highest privileges):
1. viewer      - Can view threat intelligence data
2. analyst     - Can analyze and annotate data
3. publisher   - Can publish threat intelligence
4. admin       - Organization administrator
5. system_admin - System-wide administrator

CREATING USERS:

METHOD 1: DJANGO ADMIN INTERFACE
--------------------------------

1. Access: http://127.0.0.1:8000/admin/
2. Go to "Users" section
3. Click "Add User"
4. Fill required fields:
   - Username: Unique username
   - Email: Valid email address
   - Password: Strong password
   - Organization: Select from dropdown
   - Role: Choose appropriate role
   - First/Last Name: Optional
   - Is Active: Check (default)
   - Is Verified: Check for immediate access

METHOD 2: USER FACTORY (Programmatic)
-------------------------------------

Django Shell:
python3 manage.py shell

from UserManagement.models import Organization, CustomUser
from UserManagement.factories.user_factory import UserFactory

# Get organization
org = Organization.objects.get(name="Your Organization Name")

# Create different types of users

# 1. Standard Viewer User
user_data = {
    'username': 'john.viewer',
    'email': 'john@yourorg.com',
    'password': 'SecurePass123!',
    'first_name': 'John',
    'last_name': 'Doe',
    'organization': org,
    'created_by': None,  # or specify creating user
    'auto_generate_password': False
}

viewer = UserFactory.create_user('viewer', user_data, created_by=None)
print(f"Created viewer: {viewer.username}")

# 2. Publisher User
publisher_data = {
    'username': 'jane.publisher',
    'email': 'jane@yourorg.com',
    'password': 'PublisherPass456!',
    'first_name': 'Jane',
    'last_name': 'Smith',
    'organization': org
}

publisher = UserFactory.create_user('publisher', publisher_data)
print(f"Created publisher: {publisher.username}")

# 3. Admin User
admin_data = {
    'username': 'admin.user',
    'email': 'admin@yourorg.com',
    'password': 'AdminPass789!',
    'organization': org
}

admin = UserFactory.create_user('admin', admin_data)
print(f"Created admin: {admin.username}")

METHOD 3: DIRECT MODEL CREATION
-------------------------------

from UserManagement.models import Organization, CustomUser

org = Organization.objects.get(name="Your Organization")

# Create user directly
user = CustomUser.objects.create_user(
    username='direct.user',
    email='direct@yourorg.com',
    password='DirectPass123!',
    organization=org,
    role='analyst',
    is_verified=True,
    is_active=True
)

ROLE-SPECIFIC PERMISSIONS:

VIEWER:
- Can view STIX objects within organization
- Read-only access to threat intelligence
- Cannot publish or modify data

ANALYST:
- All viewer permissions
- Can annotate and analyze data
- Can create analysis reports

PUBLISHER:
- All analyst permissions
- Can publish threat intelligence
- Can create and share STIX objects
- Can moderate content

ADMIN:
- All publisher permissions
- Can manage users within organization
- Can modify organization settings
- Cannot access other organizations

SYSTEM_ADMIN:
- All admin permissions across ALL organizations
- Can create/modify organizations
- System-wide administrative access
- Can access any user or data

VIEWING USERS:

Django Shell:
from UserManagement.models import CustomUser

# List all users
for user in CustomUser.objects.all():
    print(f"{user.username} ({user.role}) - {user.organization.name}")

# Users by role
viewers = CustomUser.objects.filter(role='viewer')
admins = CustomUser.objects.filter(role='admin')

# Users by organization
org_users = CustomUser.objects.filter(organization__name="Your Org Name")

===============================================================================
6. AUTHENTICATION & SECURITY
===============================================================================

AUTHENTICATION METHODS:

1. STANDARD AUTHENTICATION (Username/Password)
2. TWO-FACTOR AUTHENTICATION (TOTP)
3. TRUSTED DEVICE AUTHENTICATION

LOGIN PROCESS:

WEB INTERFACE:
1. Navigate to: http://127.0.0.1:8000/api/auth/login/
2. Provide credentials
3. Receive JWT token for API access

API AUTHENTICATION:
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your.username",
    "password": "your.password"
  }'

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid",
    "username": "your.username",
    "role": "viewer",
    "organization": "Your Organization"
  }
}

USING JWT TOKENS:
Include in API requests:
Authorization: Bearer YOUR_ACCESS_TOKEN

SECURITY FEATURES:

1. Password Requirements:
   - Minimum 12 characters
   - At least 1 uppercase letter
   - At least 1 lowercase letter
   - At least 2 digits
   - At least 1 special character
   - No common patterns (123, abc, password, etc.)
   - No personal information

2. Rate Limiting:
   - Login attempts: 5 per IP per minute
   - API calls: Configurable per endpoint
   - Password reset: Limited attempts

3. Account Locking:
   - After 5 failed login attempts
   - Automatic unlock after time period
   - Admin can manually unlock

4. Session Management:
   - JWT token expiration
   - Session timeout
   - Device tracking
   - IP address logging

5. Audit Logging:
   - All authentication events logged
   - Failed login attempts tracked
   - Administrative actions recorded
   - Security events monitored

===============================================================================
7. API USAGE
===============================================================================

The system provides RESTful APIs for all operations.

BASE URL: http://127.0.0.1:8000/api/

AUTHENTICATION ENDPOINTS:
------------------------

Login:
POST /api/auth/login/
{
  "username": "user",
  "password": "pass"
}

Logout:
POST /api/auth/logout/
Headers: Authorization: Bearer TOKEN

Password Change:
POST /api/auth/password/change/
Headers: Authorization: Bearer TOKEN
{
  "old_password": "current",
  "new_password": "new"
}

Token Refresh:
POST /api/auth/token/refresh/
{
  "refresh_token": "refresh_token"
}

USER MANAGEMENT ENDPOINTS:
-------------------------

List Users (organization-scoped):
GET /api/users/
Headers: Authorization: Bearer TOKEN

Get User Profile:
GET /api/users/profile/
Headers: Authorization: Bearer TOKEN

Update Profile:
PUT /api/users/profile/
Headers: Authorization: Bearer TOKEN
{
  "first_name": "John",
  "last_name": "Doe"
}

ADMIN ENDPOINTS (admin+ role required):
--------------------------------------

List All Users:
GET /api/admin/users/
Headers: Authorization: Bearer TOKEN

Create User:
POST /api/admin/users/
Headers: Authorization: Bearer TOKEN
{
  "username": "newuser",
  "email": "new@org.com",
  "password": "SecurePass123!",
  "role": "viewer",
  "organization_id": "org-uuid"
}

Update User:
PUT /api/admin/users/{user_id}/
Headers: Authorization: Bearer TOKEN
{
  "role": "publisher",
  "is_active": true
}

Delete User:
DELETE /api/admin/users/{user_id}/
Headers: Authorization: Bearer TOKEN

EXAMPLE API WORKFLOW:
--------------------

# 1. Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Save the access_token from response

# 2. Get user profile
curl -X GET http://127.0.0.1:8000/api/users/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. List organization users
curl -X GET http://127.0.0.1:8000/api/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. Create new user (admin required)
curl -X POST http://127.0.0.1:8000/api/admin/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "new@yourorg.com",
    "password": "SecurePass123!",
    "role": "viewer"
  }'

===============================================================================
8. TESTING & VALIDATION
===============================================================================

BUILT-IN TEST SUITE:
The system includes comprehensive tests covering all functionality.

RUN ALL TESTS:
./run_all_tests.sh

RUN SPECIFIC TEST SUITES:

Authentication Tests:
python3 manage.py test UserManagement.tests.test_authentication

User Management Tests:
python3 manage.py test UserManagement.tests.test_user_management

Security Tests:
python3 manage.py test UserManagement.tests.test_security

Integration Tests:
python3 manage.py test UserManagement.tests.test_integration

MANUAL TESTING PROCEDURES:

1. ORGANIZATION TESTING:
   python3 manage.py shell -c "
   from UserManagement.models import Organization
   org = Organization.objects.create(name='Test Corp', domain='test.com')
   print(f'Created: {org.name}')
   "

2. USER CREATION TESTING:
   python3 manage.py shell -c "
   from UserManagement.models import Organization, CustomUser
   org = Organization.objects.get(name='Test Corp')
   user = CustomUser.objects.create_user(
       username='testuser',
       email='test@test.com',
       password='TestPass123!',
       organization=org
   )
   print(f'Created user: {user.username}')
   "

3. AUTHENTICATION TESTING:
   python3 test_system.py

4. API TESTING:
   Use the API examples above to test endpoints

VALIDATION CHECKLIST:
- [ ] Organizations can be created
- [ ] Users can be created with different roles
- [ ] Authentication works correctly
- [ ] Role-based permissions are enforced
- [ ] API endpoints respond correctly
- [ ] Security features are active
- [ ] Audit logging is working

===============================================================================
9. ADMINISTRATIVE FUNCTIONS
===============================================================================

DJANGO ADMIN INTERFACE:
Access: http://127.0.0.1:8000/admin/

AVAILABLE ADMIN FUNCTIONS:
- User management (create, edit, delete, activate/deactivate)
- Organization management
- Role assignment
- Permission management
- Authentication log viewing
- Session management

MANAGEMENT COMMANDS:

Create Superuser:
python3 manage.py createsuperuser

Database Operations:
python3 manage.py makemigrations
python3 manage.py migrate

System Check:
python3 manage.py check

Shell Access:
python3 manage.py shell

Custom Commands (if created):
python3 manage.py create_org "Name" "domain.com"
python3 manage.py audit_users
python3 manage.py setup_auth

BULK OPERATIONS:

Bulk User Creation (Django Shell):
from UserManagement.models import Organization, CustomUser

org = Organization.objects.get(name="Your Org")
users_data = [
    ('user1', 'user1@org.com', 'viewer'),
    ('user2', 'user2@org.com', 'analyst'),
    ('user3', 'user3@org.com', 'publisher'),
]

for username, email, role in users_data:
    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password='DefaultPass123!',
        organization=org,
        role=role
    )
    print(f"Created: {username} as {role}")

MONITORING:

View Authentication Logs:
from UserManagement.models import AuthenticationLog

recent_logins = AuthenticationLog.objects.filter(
    action='login',
    success=True
).order_by('-timestamp')[:10]

for log in recent_logins:
    print(f"{log.username} logged in from {log.ip_address} at {log.timestamp}")

Security Events:
failed_logins = AuthenticationLog.objects.filter(
    success=False
).order_by('-timestamp')[:10]

===============================================================================
10. TROUBLESHOOTING
===============================================================================

COMMON ISSUES AND SOLUTIONS:

1. "ModuleNotFoundError" when starting:
   Solution: Install requirements
   pip install -r requirements.txt

2. "Database is locked" error:
   Solution: Check for running processes
   ps aux | grep python
   Kill any hanging Django processes

3. "Permission denied" on API calls:
   Solution: Check JWT token is valid and user has required role
   Verify token in Authorization header

4. "Organization does not exist" error:
   Solution: Create organization first
   python3 manage.py shell -c "
   from UserManagement.models import Organization
   Organization.objects.create(name='Default Org', domain='default.com')
   "

5. Password validation errors:
   Solution: Ensure password meets requirements:
   - 12+ characters
   - Mixed case letters
   - Numbers and special characters
   - No common patterns

6. Users can see other organizations' data:
   Solution: Check user role and organization assignment
   System admins can see all data (this is intentional)

7. Tests failing:
   Solution: Run individual test suites to identify issues
   python3 manage.py test UserManagement.tests.test_authentication -v 2

8. Server won't start:
   Solution: Check for port conflicts
   python3 manage.py runserver 8001  # Use different port

9. Database migration issues:
   Solution: Reset migrations (development only)
   rm UserManagement/migrations/0*.py
   python3 manage.py makemigrations UserManagement
   python3 manage.py migrate

10. JWT token expired:
    Solution: Use refresh token or re-authenticate
    POST /api/auth/token/refresh/ with refresh_token

LOGGING AND DEBUGGING:

Enable Debug Mode (development only):
In crisp_project/settings.py:
DEBUG = True

View Django Logs:
python3 manage.py runserver --verbosity=2

Database Query Debugging:
In Django shell:
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('django.db.backends')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

GETTING HELP:

1. Check Django documentation: https://docs.djangoproject.com/
2. Check Django REST Framework docs: https://www.django-rest-framework.org/
3. Review test files for usage examples
4. Use Django shell for debugging
5. Check authentication logs for security issues

===============================================================================
CONCLUSION
===============================================================================

This CRISP User Management System is a comprehensive, Django-based solution
for secure user and organization management in cybersecurity environments.

KEY POINTS:
- Purely Django-based (no external services required)
- Complete role-based access control
- Multi-tenant organization support
- Enterprise-grade security features
- RESTful API interface
- Comprehensive testing suite
- Production-ready architecture

The system can be deployed as a standalone Django application or integrated
into larger cybersecurity platforms. All functionality is contained within
the Django framework, making it self-contained and easy to deploy.

For additional support or customization, refer to the Django documentation
and the extensive test suite included with the system.

===============================================================================