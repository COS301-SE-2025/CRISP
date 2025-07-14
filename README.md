# CRISP - Cyber Risk Information Sharing Platform

## Overview

CRISP (Cyber Risk Information Sharing Platform) is a comprehensive cybersecurity threat intelligence management system that integrates user management, trust management, and automated email alerting capabilities. The platform enables organizations to securely share threat intelligence, manage user access, establish trust relationships, and receive real-time threat alerts.

## Architecture

The system is built with a clean, professional architecture consisting of two main directories:

- **core/** - Contains all core functionality including user management, trust management, and alert services
- **crisp/** - Contains the Django project configuration and React frontend

## Key Features

### User Management System
- User authentication and authorization
- Organization management
- Role-based access control
- Session management
- Account security features (lockout, password policies)

### Trust Management System
- Trust relationship establishment between organizations
- Trust groups for managing multiple trust relationships
- Trust metrics and monitoring
- Trust inheritance capabilities

### Gmail Alerts Integration
- Automated threat alert emails via Gmail SMTP
- Feed notification emails
- Customizable email templates
- Email statistics and monitoring
- Connection testing capabilities

### Security Features
- JWT-based authentication
- Comprehensive audit logging
- Rate limiting
- CORS protection
- Secure session management
- Environment-based configuration

## Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Node.js 16+ (for React frontend)
- Redis 6+ (optional, for caching)

## Environment Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd CRISP
```

2. **Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install backend dependencies**
```bash
cd crisp
pip install -r requirements/base.txt
```

4. **Install frontend dependencies**
```bash
cd frontend/crisp-react
npm install
```

5. **Configure environment variables**

Create a `.env` file in the project root (it's already created with template values):

```env
# Security
SECRET_KEY=your-secret-key-here-please-change-in-production
DEBUG=True

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
```

6. **Set up the PostgreSQL database**
```bash
sudo -u postgres psql
CREATE USER crisp_user WITH PASSWORD 'crisp_password';
CREATE DATABASE crisp_trust_db;
GRANT ALL PRIVILEGES ON DATABASE crisp_trust_db TO crisp_user;
\q
```

7. **Apply migrations**
```bash
cd crisp
python manage.py makemigrations
python manage.py migrate
```

8. **Create a superuser**
```bash
python manage.py createsuperuser
```

## Running the Application

### Start the Backend Server

```bash
cd crisp
python manage.py runserver
```

The backend API will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Start the Frontend Development Server

```bash
cd crisp/frontend/crisp-react
npm run dev
```

The frontend will be available at [http://127.0.0.1:5173/](http://127.0.0.1:5173/)

## API Endpoints

### User Management
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/dashboard/` - User dashboard data
- `GET /api/v1/users/profile/` - Get user profile
- `PUT /api/v1/users/profile/` - Update user profile
- `POST /api/v1/users/create/` - Create new user

### Trust Management
- `GET /api/v1/organizations/list/` - List organizations
- `POST /api/v1/organizations/create/` - Create organization
- `GET /api/v1/organizations/trust-metrics/` - Get trust metrics
- `POST /api/v1/organizations/<id>/trust-relationship/` - Create trust relationship

### Gmail Alerts
- `POST /api/v1/alerts/threat/` - Send threat alert email
- `POST /api/v1/alerts/feed/` - Send feed notification email
- `GET /api/v1/alerts/test-connection/` - Test Gmail connection
- `GET /api/v1/alerts/statistics/` - Get email statistics
- `POST /api/v1/alerts/test-email/` - Send test email

### Admin Functions
- `GET /api/v1/admin/dashboard/` - Admin dashboard
- `GET /api/v1/admin/system-health/` - System health status
- `GET /api/v1/admin/audit-logs/` - Audit logs
- `GET /api/v1/admin/trust-overview/` - Trust system overview

## Gmail Configuration

To enable Gmail alerts, you need to:

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password** for CRISP
3. **Update the .env file** with your Gmail credentials:
   ```env
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   CRISP_SENDER_EMAIL=your-email@gmail.com
   ```

## Testing

### Backend Tests
```bash
cd crisp
python manage.py test --settings=test_settings
```

### Frontend Tests
```bash
cd crisp/frontend/crisp-react
npm test
```

## Project Structure

```
CRISP/
├── README.md
├── .env                                    # Environment variables
├── .gitignore                             # Git ignore file
├── core/                                  # Core functionality
│   ├── middleware/                        # Custom middleware
│   │   └── audit_middleware.py           # Audit logging middleware
│   ├── patterns/                          # Design patterns
│   │   └── observer/                      # Observer pattern implementation
│   │       ├── alert_system_observer.py
│   │       └── email_notification_observer.py
│   ├── services/                          # Business logic services
│   │   ├── audit_service.py
│   │   ├── gmail_smtp_service.py          # Gmail SMTP service
│   │   ├── alerts_views.py                # Alert API views
│   │   └── alerts_urls.py                 # Alert URL patterns
│   ├── trust/                             # Trust management
│   │   ├── models/
│   │   ├── services/
│   │   ├── patterns/                      # Trust-specific patterns
│   │   └── migrations/
│   ├── user_management/                   # User management
│   │   ├── models/
│   │   ├── services/
│   │   ├── views/
│   │   ├── factories/
│   │   └── migrations/
│   └── tests/                             # Comprehensive test suite
└── crisp/                                 # Django project
    ├── TrustManagement/                   # Django configuration
    │   ├── settings.py                    # Main settings
    │   ├── urls.py                        # URL configuration
    │   └── wsgi.py
    ├── frontend/                          # React frontend
    │   └── crisp-react/
    │       ├── src/
    │       │   ├── api.js                 # API integration
    │       │   ├── components/            # React components
    │       │   └── assets/                # Static assets
    │       ├── package.json
    │       └── vite.config.js
    ├── requirements/                      # Python dependencies
    │   ├── base.txt
    │   ├── development.txt
    │   └── production.txt
    └── manage.py                          # Django management script
```

## Security Considerations

- All sensitive configuration is stored in environment variables
- JWT tokens are used for API authentication
- CORS is properly configured for frontend-backend communication
- Comprehensive audit logging is implemented
- Rate limiting is enforced on API endpoints
- Session security is properly configured

## Development Features

- Hot reloading for both frontend and backend development
- Comprehensive test coverage
- Code quality tools (ESLint, Black, isort)
- Docker support available
- CI/CD ready configuration

## Contributing

1. Follow the existing code style and patterns
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass before submitting

## License

This project is part of the CRISP (Cyber Risk Information Sharing Platform) system.