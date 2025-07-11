# CRISP - Cyber Risk Information Sharing Platform

[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![REST API](https://img.shields.io/badge/API-REST-orange.svg)](https://www.django-rest-framework.org/)

A comprehensive trust management and user management platform for secure cyber risk information sharing between organizations.

## 🏗️ Architecture

CRISP is built as an integrated platform with two main components:

### **Core System** (`core/`)
- **Trust Management** (`core/trust/`) - Handles trust relationships between organizations
- **User Management** (`core/user_management/`) - Manages users, organizations, and authentication
- **Audit & Security** (`core/services/`, `core/middleware/`) - Comprehensive logging and security

### **CRISP Platform** (`crisp/`)
- **Django Project** (`crisp/TrustManagement/`) - Main application settings and configuration
- **Tools & Scripts** (`crisp/tools/`, `crisp/scripts/`) - Development and deployment utilities
- **Configuration** (`crisp/config/`) - Testing and development configuration
- **Requirements** (`crisp/requirements/`) - Python package dependencies

## 🚀 Quick Start

### Docker Setup (Recommended)

**One-command setup with Docker:**
```bash
git clone <repository-url>
cd Capstone
docker-compose up --build -d
```

Access the platform at:
- **Web Interface**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin/ 
- **API**: http://localhost:8000/api/v1/

**Test Users (auto-created):**
- Admin: `admin_test_user` / `AdminTestPass123!`
- User: `regular_test_user` / `RegularTestPass123!`

**Docker Commands:**
```bash
docker-compose up -d          # Start services
docker-compose down           # Stop services  
docker-compose logs -f web    # View logs
docker-compose down -v        # Reset everything
```

### Manual Setup

#### Prerequisites
- **Python 3.10+**
- **PostgreSQL 13+**
- **Redis** (optional, for caching)

#### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd CRISP/UserTrust

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r crisp/requirements/development.txt
```

#### 2. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres createdb crisp_trust_db
sudo -u postgres createuser crisp_user --password

# Set environment variables (or use .env file)
export DB_NAME=crisp_trust_db
export DB_USER=crisp_user
export DB_PASSWORD=crisp_password
```

#### 3. Run Django Setup
```bash
# Navigate to Django project directory
cd crisp

# **IMPORTANT: Make sure virtual environment is activated**
# You should see (venv) in your terminal prompt

# Run migrations
python3 manage.py migrate

# Create superuser (optional)
python3 manage.py createsuperuser

# Start the development server
python3 manage.py runserver
```

#### 4. Verify Setup
```bash
# Check Django installation
python3 -c "import django; print(django.get_version())"

# Check system configuration
python3 manage.py check

# Run tests
python3 manage.py test
```


 Method 1: Simple command (from the crisp directory)
  cd /mnt/c/Users/Client/Documents/GitHub/CRISP/UserTrust/crisp
  python3 manage.py runserver 0.0.0.0:8000

  Method 2: Using the startup script (from UserTrust directory)
  cd /mnt/c/Users/Client/Documents/GitHub/CRISP/UserTrust
  ./run_server.sh

### Quick Commands

```bash
# **IMPORTANT: Always activate virtual environment first**
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run comprehensive tests
cd crisp
python3 manage.py test

# Start the platform
cd crisp
python3 manage.py runserver

# The API will be available at:
# http://localhost:8000/api/v1/
# Admin interface: http://localhost:8000/admin/
```

## 🔧 Configuration

### Frontend UI Setup

The React frontend is located in `/UI/crisp-react/` and is configured to connect to the UserTrust Django backend.

```bash
# Navigate to UI directory
cd UI/crisp-react

# Install dependencies
npm install

# Start development server
npm run dev

# The UI will be available at:
# http://localhost:5173
```

**Frontend Configuration:**
- API Base URL: `http://localhost:8000/api/v1/`
- The UI is configured to use the UserTrust Django server endpoints
- CORS is configured to allow requests from `localhost:5173`

### Environment Variables

Create a `.env` file in the `crisp/` directory:

```env
# Database
DB_NAME=crisp_trust_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Security
SECRET_KEY=your-secret-key
DEBUG=True

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Trust System
TRUST_RELATIONSHIP_EXPIRY_DAYS=365
ACCOUNT_LOCKOUT_THRESHOLD=5

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379/1
```

## 📋 Testing

### Run All Tests

```bash
# **IMPORTANT: Make sure virtual environment is activated**
source venv/bin/activate

cd crisp

# Run comprehensive test suite
python3 manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML coverage report
```

### Test Specific Components

```bash
# Test user management
python3 manage.py test core.user_management

# Test trust management
python3 manage.py test core.trust

# Test integration
python3 manage.py test core.tests.test_integration
```

### API Testing

```bash
# Test API endpoints
python3 crisp/tools/test_runners/run_tests.py

# Test with different scenarios
python3 crisp/legacy_tests/test_api_endpoints.py
```

## 🌐 API Documentation

### Authentication Endpoints

```bash
# Login
POST /api/v1/auth/login/
{
  "username": "user@example.com",
  "password": "password"
}

# Token refresh
POST /api/v1/auth/refresh/
{
  "refresh_token": "your_refresh_token"
}

# Logout
POST /api/v1/auth/logout/
```

### User Management

```bash
# Create user
POST /api/v1/users/create/

# List users
GET /api/v1/users/list/

# User profile
GET /api/v1/users/profile/
```

### Organization Management

```bash
# Create organization
POST /api/v1/organizations/create/

# List organizations
GET /api/v1/organizations/list/

# Create trust relationship
POST /api/v1/organizations/{id}/trust-relationship/
```

### Admin Features

```bash
# Admin dashboard
GET /api/v1/admin/dashboard/

# System health
GET /api/v1/admin/system-health/

# Comprehensive audit logs
GET /api/v1/admin/comprehensive-audit-logs/

# Security events
GET /api/v1/admin/security-events/
```

## 👥 User Roles

### **Viewer**
- View shared intelligence within trust relationships
- Access basic organization information

### **Publisher**
- All Viewer permissions
- Share intelligence with trusted organizations
- Manage organization users
- Create and manage trust relationships

### **BlueVision Administrator**
- Full system access
- Manage all organizations and users
- System monitoring and analytics
- Audit log access

## 🔐 Security Features

- **JWT Authentication** with refresh tokens
- **Role-based Access Control** (RBAC)
- **Trust-aware Permissions** - Access based on organizational trust relationships
- **Comprehensive Audit Logging** - All actions tracked
- **Account Lockout Protection** - Prevents brute force attacks
- **Session Management** - Secure session handling
- **Rate Limiting** - API endpoint protection

## 🗃️ Database Schema

### Core Models

- **CustomUser** - Enhanced user model with roles and organization
- **Organization** - Organizations that participate in information sharing
- **TrustRelationship** - Trust connections between organizations
- **TrustLevel** - Defines levels of trust (public, trusted, restricted)
- **AuthenticationLog** - Comprehensive audit trail
- **UserSession** - Active user session tracking

## 📊 Monitoring & Analytics

### System Health Monitoring

```bash
# Check system health
GET /api/v1/admin/system-health/

# View audit statistics  
GET /api/v1/admin/audit-statistics/

# Security event monitoring
GET /api/v1/admin/security-events/?severity=high
```

### Log Files

- **Application Logs**: `crisp/logs/trust_management.log`
- **Audit Logs**: `crisp/logs/audit.log`
- **Security Logs**: `crisp/logs/security.log`

## 🛠️ Development

### Code Quality

```bash
# Run code quality checks
bash crisp/scripts/code_quality_check.sh

# Format code
black .
isort .

# Linting
flake8 .
```

### Database Management

```bash
# **IMPORTANT: Make sure virtual environment is activated**
source venv/bin/activate

# Reset database (development only)
cd crisp
python3 reset_database.py

# Create new migrations
python3 manage.py makemigrations

# Apply migrations
python3 manage.py migrate
```

## 📚 Documentation

Documentation is available in the codebase:

- **API Documentation**: Available through Django REST framework at `/api/v1/`
- **Model Documentation**: See model files in `core/trust/models/` and `core/user_management/models/`
- **Testing Examples**: Review test files in `core/tests/` for usage examples

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   export DEBUG=False
   export ALLOWED_HOSTS=your-domain.com
   export SECRET_KEY=production-secret-key
   ```

2. **Database Setup**
   ```bash
   # Create production database
   python3 manage.py migrate --settings=crisp.TrustManagement.settings
   ```

3. **Static Files**
   ```bash
   python3 manage.py collectstatic
   ```

4. **WSGI/ASGI Deployment**
   - Use `crisp/TrustManagement/wsgi.py` for WSGI servers
   - Use `crisp/TrustManagement/asgi.py` for ASGI servers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python manage.py test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is part of the University of Pretoria Capstone project for Cyber Risk Information Sharing.

## 🆘 Troubleshooting

### Common Issues

**Virtual Environment Issues**
```bash
# If you get "ModuleNotFoundError: No module named 'django'"
# 1. Make sure virtual environment is activated
source venv/bin/activate  # You should see (venv) in your prompt

# 2. Install dependencies again
pip install -r crisp/requirements/development.txt

# 3. Verify Django is installed
python3 -c "import django; print(django.get_version())"

# 4. If still issues, recreate virtual environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r crisp/requirements/development.txt
```

**Database Connection Issues**
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Verify database exists
psql -l | grep crisp_trust_db
```

**Migration Issues**
```bash
# Reset migrations (development only)
cd crisp
python3 reset_database.py
```

**Permission Issues**
```bash
# Check user roles
python3 manage.py shell
>>> from core.user_management.models import CustomUser
>>> user = CustomUser.objects.get(username='your_username')
>>> print(user.role, user.organization)
```

## 📞 Support

For support and questions:
- Review test files in `core/tests/` for usage examples
- Check model definitions in `core/trust/models/` and `core/user_management/models/`
- Check logs in `crisp/logs/` for debugging information

---

**CRISP Platform** - Secure. Trusted. Connected.