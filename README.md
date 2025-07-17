# CRISP - Cyber Risk Information Sharing Platform

## Overview

CRISP (Cyber Risk Information Sharing Platform) is a comprehensive cybersecurity threat intelligence management system that integrates user management, trust management, and automated email alerting capabilities. The platform enables organizations to securely share threat intelligence, manage user access, establish trust relationships, and receive real-time threat alerts.

## Architecture

The system is built with a clean, professional architecture consisting of:

- **Django Backend** - RESTful API with comprehensive business logic
- **React Frontend** - Modern, responsive user interface
- **PostgreSQL Database** - Robust data persistence
- **Redis Cache** - Optional caching layer for performance

### Core Components
- **core/** - Contains all core functionality including user management, trust management, and services
- **crisp/** - Contains the Django project configuration and React frontend

## Key Features

### 🔐 User Management System
- **Authentication & Authorization** - JWT-based secure authentication
- **Organization Management** - Multi-tenant organization support
- **Role-Based Access Control** - Granular permissions (Admin, Publisher, Viewer)
- **Session Management** - Secure session handling with audit trails
- **Account Security** - Account lockout, password policies, failed login tracking
- **User Profiles** - Comprehensive user profile management

### 🤝 Trust Management System
- **Trust Relationships** - Establish trust between organizations
- **Trust Groups** - Manage collections of trusted organizations
- **Trust Levels** - Configurable trust levels (Basic, Standard, Premium)
- **Trust Metrics** - Monitor and analyze trust relationships
- **Trust Patterns** - Observer, Factory, Repository, and Decorator patterns
- **Trust Inheritance** - Hierarchical trust relationship management

### 📧 Email Alert System
- **Gmail SMTP Integration** - Professional email alerts via Gmail
- **SMTP2GO Support** - Alternative email provider support
- **Threat Alerts** - Automated threat intelligence notifications
- **Feed Notifications** - Real-time feed update alerts
- **Email Templates** - Customizable HTML email templates
- **Email Statistics** - Comprehensive email delivery tracking
- **Connection Testing** - Built-in email service health checks

### 🛡️ Security Features
- **JWT Authentication** - Secure token-based authentication
- **Comprehensive Audit Logging** - Full activity tracking and compliance
- **Rate Limiting** - API endpoint protection
- **CORS Protection** - Secure cross-origin resource sharing
- **Middleware Security** - Custom security middleware
- **Environment-based Configuration** - Secure secret management

### 📊 Admin Dashboard
- **System Health Monitoring** - Real-time system status
- **User Management** - Admin user creation and management
- **Audit Log Viewing** - Comprehensive audit trail analysis
- **Trust Overview** - System-wide trust relationship insights
- **Email Statistics** - Email system performance metrics

## Prerequisites

- **Python 3.10+** (Tested on 3.10.12)
- **PostgreSQL 13+** (Primary database)
- **Node.js 18+** (For React frontend)
- **npm 9+** (Package management)
- **Git** (Version control)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd CRISP
```

### 2. Backend Setup

#### Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Backend Dependencies
```bash
pip install -r requirements.txt
# Or for specific environments:
# pip install -r crisp/requirements/development.txt
```

#### Set up PostgreSQL Database
```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create database and user
CREATE USER crisp_user WITH PASSWORD 'crisp_password';
CREATE DATABASE crisp_trust_db OWNER crisp_user;
GRANT ALL PRIVILEGES ON DATABASE crisp_trust_db TO crisp_user;
ALTER USER crisp_user CREATEDB;  # For running tests
\q
```

#### Configure Environment Variables
Copy and update the `.env.example` file:
```bash
cp .env.example .env
```

Update `.env` with your configuration:
```env
# Security
SECRET_KEY=your-super-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=crisp_trust_db
DB_USER=crisp_user
DB_PASSWORD=crisp_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=noreply@crisp-trust.example.com

# CRISP Email Settings
CRISP_SENDER_NAME=CRISP Threat Intelligence
CRISP_SENDER_EMAIL=your-gmail-email@gmail.com

# Optional: Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

#### Apply Database Migrations
```bash
cd crisp
python3 manage.py makemigrations
python3 manage.py migrate
```

#### Create Superuser
```bash
python3 manage.py createsuperuser
```

### 3. Frontend Setup

#### Install Frontend Dependencies
```bash
cd crisp/frontend/crisp-react
npm install
```

#### Configure Frontend Environment
Create `crisp/frontend/crisp-react/.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_APP_NAME=CRISP
```

### 4. Database Population (Optional)

For testing and development, you can populate the database with realistic data:

#### Standard Population (Recommended for development)
```bash
python3 populate_database.py
```
- 25 organizations
- 75-375 users
- 200-500 audit logs

#### Massive Population (For stress testing and demos)
```bash
python3 populate_massive_database.py
```
- 200 organizations
- 3,000-10,000 users
- 1,000 trust relationships
- 50 trust groups
- 10,000 user sessions
- 50,000 audit logs

**Default login credentials after population:**
- **Super Admins**: `admin`, `demo`, `test` with password `AdminPass123!`
- **Regular Users**: All users have password `UserPass123!`
- **Username Format**: `firstname.lastname@organization.domain`

## Running the Application

### Development Mode

#### Start Backend Server
```bash
cd crisp
python3 manage.py runserver
```
Backend API: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

#### Start Frontend Development Server
```bash
cd crisp/frontend/crisp-react
npm run dev
```
Frontend UI: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)

### Production Mode

#### Backend (using Gunicorn)
```bash
cd crisp
pip install gunicorn
gunicorn crisp.TrustManagement.wsgi:application --bind 0.0.0.0:8000
```

#### Frontend (build and serve)
```bash
cd crisp/frontend/crisp-react
npm run build
# Serve with nginx, Apache, or any static file server
```

## Testing

### Comprehensive Test Suite

The application includes 953+ comprehensive tests with 83% code coverage.

#### Run All Tests
```bash
# Django tests with coverage
coverage run --source='core' crisp/manage.py test --keepdb
coverage report
coverage html

# Frontend tests
cd crisp/frontend/crisp-react
npm test
```

#### Run Specific Test Categories
```bash
# User management tests
python3 crisp/manage.py test core.user_management.tests --keepdb

# Trust management tests
python3 crisp/manage.py test core.trust.tests --keepdb

# Service tests
python3 crisp/manage.py test core.tests.test_services --keepdb

# Integration tests
python3 crisp/manage.py test core.tests.test_integration --keepdb
```

#### Run Tests with Parallel Execution (faster)
```bash
python3 crisp/manage.py test --parallel --keepdb
```

#### Integration Testing
```bash
# Start the servers first, then:
python3 test_comprehensive.py
```

## API Documentation

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login/` | User authentication |
| POST | `/api/v1/auth/logout/` | User logout |
| GET | `/api/v1/auth/dashboard/` | User dashboard data |
| POST | `/api/v1/auth/change-password/` | Change user password |

### User Management Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/profile/` | Get user profile |
| PUT | `/api/v1/users/profile/` | Update user profile |
| POST | `/api/v1/users/create/` | Create new user |
| GET | `/api/v1/users/list/` | List users (admin) |

### Organization Management Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/organizations/list/` | List organizations |
| POST | `/api/v1/organizations/create/` | Create organization |
| GET | `/api/v1/organizations/<id>/` | Get organization details |
| PUT | `/api/v1/organizations/<id>/` | Update organization |

### Trust Management Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/trust/relationships/` | List trust relationships |
| POST | `/api/v1/trust/relationships/create/` | Create trust relationship |
| GET | `/api/v1/trust/groups/` | List trust groups |
| POST | `/api/v1/trust/groups/create/` | Create trust group |
| GET | `/api/v1/trust/metrics/` | Get trust metrics |

### Email Alert Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/alerts/threat/` | Send threat alert |
| POST | `/api/v1/alerts/feed/` | Send feed notification |
| GET | `/api/v1/alerts/test-connection/` | Test email connection |
| GET | `/api/v1/alerts/statistics/` | Email statistics |
| POST | `/api/v1/alerts/test-email/` | Send test email |

### Admin Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/dashboard/` | Admin dashboard |
| GET | `/api/v1/admin/system-health/` | System health check |
| GET | `/api/v1/admin/audit-logs/` | Audit logs |
| GET | `/api/v1/admin/users/` | User management |
| GET | `/api/v1/admin/trust-overview/` | Trust system overview |

## Gmail Configuration

### Setup Gmail App Password

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Update Environment Variables**:
   ```env
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-digit-app-password
   CRISP_SENDER_EMAIL=your-email@gmail.com
   ```

### Test Email Configuration
```bash
# Via API
curl -X GET http://127.0.0.1:8000/api/v1/alerts/test-connection/

# Via Django shell
python3 crisp/manage.py shell
>>> from core.services.gmail_smtp_service import GmailSMTPService
>>> service = GmailSMTPService()
>>> service.test_connection()
```

## Project Structure

```
CRISP/
├── README.md                                  # This file
├── .env.example                              # Environment template
├── .gitignore                                # Git ignore rules
├── populate_database.py                     # Standard data population
├── populate_massive_database.py             # Massive data population
├── test_comprehensive.py                    # Integration tests
├── requirements.txt                          # Python dependencies
│
├── core/                                     # Core application logic
│   ├── __init__.py
│   ├── middleware/                           # Custom middleware
│   │   ├── __init__.py
│   │   └── audit_middleware.py              # Audit logging middleware
│   │
│   ├── patterns/                             # Design patterns
│   │   └── observer/                         # Observer pattern
│   │       ├── __init__.py
│   │       ├── alert_system_observer.py
│   │       └── email_notification_observer.py
│   │
│   ├── services/                             # Business services
│   │   ├── __init__.py
│   │   ├── audit_service.py                 # Audit logging service
│   │   ├── gmail_smtp_service.py            # Gmail SMTP service
│   │   ├── smtp2go_service.py               # SMTP2GO service
│   │   ├── alerts_views.py                  # Alert API views
│   │   └── alerts_urls.py                   # Alert URL patterns
│   │
│   ├── trust/                                # Trust management
│   │   ├── __init__.py
│   │   ├── admin.py                         # Django admin config
│   │   ├── apps.py                          # App configuration
│   │   ├── models/                          # Trust models
│   │   │   ├── __init__.py
│   │   │   └── trust_models.py
│   │   ├── services/                        # Trust services
│   │   │   ├── __init__.py
│   │   │   ├── trust_service.py
│   │   │   └── trust_group_service.py
│   │   ├── patterns/                        # Trust patterns
│   │   │   ├── __init__.py
│   │   │   ├── decorator/
│   │   │   ├── factory/
│   │   │   ├── observer/
│   │   │   ├── repository/
│   │   │   └── strategy/
│   │   ├── migrations/                      # Database migrations
│   │   ├── tests/                           # Trust tests
│   │   ├── urls.py                          # URL patterns
│   │   ├── validators.py                    # Trust validators
│   │   └── signals.py                       # Django signals
│   │
│   ├── user_management/                      # User management
│   │   ├── __init__.py
│   │   ├── admin.py                         # Django admin config
│   │   ├── apps.py                          # App configuration
│   │   ├── models/                          # User models
│   │   │   ├── __init__.py
│   │   │   └── user_models.py
│   │   ├── services/                        # User services
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── organization_service.py
│   │   │   ├── access_control_service.py
│   │   │   └── trust_aware_service.py
│   │   ├── views/                           # API views
│   │   │   ├── __init__.py
│   │   │   ├── auth_views.py
│   │   │   ├── user_views.py
│   │   │   ├── organization_views.py
│   │   │   └── admin_views.py
│   │   ├── factories/                       # Test factories
│   │   │   ├── __init__.py
│   │   │   └── user_factory.py
│   │   ├── migrations/                      # Database migrations
│   │   ├── tests/                           # User tests
│   │   ├── urls.py                          # URL patterns
│   │   ├── validators.py                    # User validators
│   │   └── signals.py                       # Django signals
│   │
│   ├── tests/                                # Comprehensive test suite
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── factories.py                     # Test data factories
│   │   ├── test_models.py                   # Model tests
│   │   ├── test_services.py                 # Service tests
│   │   ├── test_views.py                    # View tests
│   │   ├── test_integration.py              # Integration tests
│   │   ├── test_audit_service_comprehensive.py
│   │   ├── test_admin_views_comprehensive.py
│   │   ├── test_alerts_views_comprehensive.py
│   │   ├── test_trust_services_comprehensive.py
│   │   └── ... (50+ comprehensive test files)
│   │
│   ├── signals.py                            # Global signals
│   └── urls.py                               # Core URL patterns
│
└── crisp/                                    # Django project
    ├── TrustManagement/                      # Django settings
    │   ├── __init__.py
    │   ├── settings.py                       # Main settings
    │   ├── urls.py                           # URL configuration
    │   ├── wsgi.py                           # WSGI config
    │   └── asgi.py                           # ASGI config
    │
    ├── frontend/                             # React frontend
    │   └── crisp-react/
    │       ├── src/
    │       │   ├── main.jsx                  # Entry point
    │       │   ├── App.jsx                   # Main component
    │       │   ├── api.js                    # API integration
    │       │   ├── crisp_login.jsx           # Login component
    │       │   ├── crisp_help.jsx            # Help component
    │       │   ├── construction.jsx          # Construction page
    │       │   ├── components/               # React components
    │       │   │   ├── UserManagement.jsx
    │       │   │   └── ChangePassword.jsx
    │       │   └── assets/                   # Static assets
    │       │       ├── crisp_help.css
    │       │       └── construction.css
    │       ├── public/                       # Public assets
    │       ├── package.json                  # NPM dependencies
    │       ├── vite.config.js               # Vite configuration
    │       └── index.html                    # HTML template
    │
    ├── staticfiles/                          # Collected static files
    ├── media/                                # User uploads
    ├── requirements/                         # Python requirements
    │   ├── base.txt                         # Base requirements
    │   ├── development.txt                  # Development requirements
    │   └── production.txt                   # Production requirements
    ├── pytest.ini                           # Pytest configuration
    └── manage.py                             # Django management
```

## Design Patterns Used

### Observer Pattern
- **Email Alert System** - Observers notify on trust events
- **Trust Event Notifications** - Real-time trust relationship updates
- **Audit Logging** - Automatic event logging

### Factory Pattern
- **User Creation** - Standardized user creation across roles
- **Trust Object Creation** - Consistent trust relationship creation
- **Email Template Generation** - Dynamic email content creation

### Repository Pattern
- **Data Access Layer** - Abstracted database operations
- **Trust Data Management** - Centralized trust data operations
- **User Data Management** - Consistent user data access

### Decorator Pattern
- **Trust Validation** - Runtime trust level validation
- **Permission Checking** - Dynamic permission decoration
- **Audit Logging** - Automatic method auditing

## Security Features

### Authentication & Authorization
- **JWT Token Authentication** - Secure, stateless authentication
- **Role-Based Access Control** - Granular permission system
- **Session Management** - Secure session handling
- **Multi-Factor Authentication** - Optional MFA support

### Security Middleware
- **Audit Middleware** - Automatic request/response logging
- **Rate Limiting** - API endpoint protection
- **CORS Configuration** - Secure cross-origin requests
- **CSRF Protection** - Cross-site request forgery protection

### Data Protection
- **Environment Variables** - Secure configuration management
- **Password Hashing** - Argon2 password hashing
- **Database Encryption** - Sensitive field encryption
- **Audit Trails** - Comprehensive activity logging

## Performance Features

### Caching
- **Redis Integration** - Optional caching layer
- **Database Query Optimization** - Efficient database operations
- **Static File Caching** - Frontend asset optimization

### Scalability
- **Database Indexing** - Optimized database performance
- **Async Operations** - Non-blocking email sending
- **Connection Pooling** - Efficient database connections

## Monitoring & Logging

### Comprehensive Audit System
- **User Actions** - All user activities logged
- **Trust Operations** - Trust relationship changes tracked
- **Email Activities** - Email sending and delivery tracked
- **System Events** - Administrative actions logged
- **Security Events** - Authentication and authorization events

### Health Monitoring
- **System Health Checks** - Real-time system status
- **Database Connectivity** - Database connection monitoring
- **Email Service Status** - Email provider health checks
- **API Endpoint Monitoring** - Service availability tracking

## Development Tools

### Code Quality
- **Coverage Reports** - 83% test coverage achieved
- **Linting** - Code style enforcement
- **Type Checking** - Static type analysis
- **Security Scanning** - Vulnerability detection

### Development Workflow
- **Hot Reloading** - Real-time development updates
- **Debug Toolbar** - Django debug information
- **API Documentation** - Automated API docs
- **Test Database** - Isolated test environment

## Deployment

### Production Checklist
- [ ] Update `SECRET_KEY` in production
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up SSL/TLS certificates
- [ ] Configure production database
- [ ] Set up Redis for caching
- [ ] Configure email provider
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Set up log aggregation

### Docker Support
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Cloud Deployment
The application is ready for deployment on:
- **AWS** (EC2, RDS, ElastiCache)
- **Google Cloud Platform** (Compute Engine, Cloud SQL, Memorystore)
- **Azure** (Virtual Machines, Database, Redis Cache)
- **Heroku** (With PostgreSQL and Redis add-ons)

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Reset database
python3 crisp/manage.py flush
python3 crisp/manage.py migrate
```

#### Email Configuration Issues
```bash
# Test email configuration
python3 crisp/manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

#### Frontend Build Issues
```bash
# Clear node modules and reinstall
cd crisp/frontend/crisp-react
rm -rf node_modules package-lock.json
npm install
```

### Performance Issues
```bash
# Check database performance
python3 crisp/manage.py dbshell
# Run EXPLAIN ANALYZE on slow queries

# Monitor memory usage
htop

# Check logs
tail -f /var/log/postgresql/postgresql-13-main.log
```

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow code style guidelines
4. Add comprehensive tests
5. Update documentation
6. Submit pull request

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Follow ESLint configuration
- **Git**: Use conventional commit messages
- **Documentation**: Update README for any changes

### Testing Requirements
- All new features must include tests
- Maintain minimum 80% code coverage
- All tests must pass before submission
- Include integration tests for API changes

## License

This project is part of the University of Pretoria Capstone project for 2025.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the comprehensive test suite for examples
3. Check the API documentation
4. Create an issue in the repository

---

**CRISP - Secure, Scalable, Professional Threat Intelligence Platform**