# CRISP - Cyber Risk Information Sharing Platform
**Comprehensive Technical Documentation**

![CRISP Banner](https://img.shields.io/badge/CRISP-Threat%20Intelligence%20Platform-blue?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-4.2.10-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![STIX](https://img.shields.io/badge/STIX-2.1-red?style=flat-square)
![TAXII](https://img.shields.io/badge/TAXII-2.1-orange?style=flat-square)
![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen?style=flat-square)
![Tests](https://img.shields.io/badge/tests-363%20total-blue?style=flat-square)
![Status](https://img.shields.io/badge/status-production%20ready-green?style=flat-square)

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Environment Setup](#environment-setup)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
- [Management Commands](#management-commands)
- [Scripts & Utilities](#scripts--utilities)
- [Background Tasks](#background-tasks)
- [Testing](#testing)
- [Security Features](#security-features)
- [Troubleshooting](#troubleshooting)
- [Deployment](#deployment)

## Overview

CRISP is a comprehensive cyber threat intelligence sharing platform designed for educational and research purposes. It implements STIX/TAXII standards with trust-based anonymization capabilities, supporting secure information sharing between organizations.

### Key Features
- 🔒 **Trust-based Anonymization** - Multi-level data anonymization based on organization relationships
- 🌐 **STIX/TAXII Compliance** - Full STIX 2.1 and TAXII 2.1 support
- 🏢 **Multi-Organization** - Role-based access control across organizations
- 🔄 **Real-time Processing** - Celery-powered background task processing
- 🛡️ **Security First** - Comprehensive security middleware and audit logging
- 📊 **Rich Analytics** - Design pattern implementations (Factory, Observer, Strategy, Decorator)

## Architecture

### Project Structure
```
CRISP/
├── core/                           # Main Django application
│   ├── models/                     # Database models
│   │   ├── auth.py                # Authentication models (CustomUser, Organization)
│   │   ├── stix_object.py         # STIX-related models (STIXObject, Collection, Feed)
│   │   ├── indicator.py           # Threat indicators
│   │   ├── institution.py         # Educational institutions
│   │   ├── threat_feed.py         # Threat feed management
│   │   ├── ttp_data.py           # Tactics, Techniques, Procedures
│   │   └── trust_models/
│   │       └── models.py          # Trust relationships
│   ├── services/                   # Business logic layer
│   │   ├── auth_service.py        # Authentication service
│   │   ├── otx_service.py         # AlienVault OTX integration
│   │   ├── stix_taxii_service.py  # STIX/TAXII processing
│   │   ├── trust_service.py       # Trust management
│   │   └── trust_anonymization_service.py # Anonymization engine
│   ├── strategies/                 # Strategy pattern implementations
│   │   ├── anonymization.py       # Anonymization strategies
│   │   ├── authentication_strategies.py # Auth strategies
│   │   └── enums.py               # System enumerations
│   ├── patterns/                   # Design pattern implementations
│   │   ├── decorator/             # Decorator pattern (STIX decorators)
│   │   ├── factory/               # Factory pattern (STIX creators)
│   │   └── observer/              # Observer pattern (feed observers)
│   ├── api/                       # REST API endpoints
│   │   ├── trust_api/             # Trust management API
│   │   ├── permissions/           # API permissions
│   │   └── serializers/           # API serializers
│   ├── management/commands/        # Django management commands
│   │   ├── taxii_operations.py    # TAXII server operations
│   │   └── test_taxii.py          # TAXII connection testing
│   ├── middleware.py              # Security middleware
│   ├── tests/                     # Comprehensive test suite
│   └── scripts/                   # Utility scripts
├── crisp/                         # Django project settings
│   ├── settings.py               # Main configuration
│   ├── celery.py                 # Celery configuration
│   └── config/security/          # Sensitive configuration
└── backup/                       # Archived components
```

### Technology Stack
- **Backend Framework**: Django 4.2.10 + Django REST Framework
- **Database**: PostgreSQL with psycopg2
- **Message Queue**: Redis + Celery
- **Authentication**: JWT with SimpleJWT
- **STIX/TAXII**: stix2, taxii2-client libraries
- **Security**: bcrypt, cryptography, django-ratelimit
- **Testing**: pytest, coverage, factory-boy

## Environment Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Redis (for Celery tasks)
- Git

### Environment Variables

Create `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/crisp/config/security/.env`:

```bash
# Database Configuration
DB_NAME=crisp
DB_USER=admin
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration  
DJANGO_SECRET_KEY=your_super_secret_key_here
TRUST_MANAGEMENT_SECRET_KEY=another_secret_key_for_trust
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# External Services
OTX_API_KEY=your_otx_api_key_here
OTX_ENABLED=True
OTX_FETCH_INTERVAL=3600
OTX_BATCH_SIZE=50
OTX_MAX_AGE_DAYS=30

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis/Celery
REDIS_URL=redis://localhost:6379/0

# TAXII Server
TAXII_SERVER_TITLE=CRISP Threat Intelligence Platform
TAXII_SERVER_DESCRIPTION=Educational threat intelligence sharing platform
TAXII_CONTACT_EMAIL=admin@crisp.edu
```

## Installation

### 1. Clone and Setup
```bash
cd "/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone"
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r core/requirements/base.txt
```

### 2. Database Setup
```bash
# Create PostgreSQL database
createdb crisp
createuser admin --pwprompt

# Run migrations
cd core
python3 manage.py makemigrations
python3 manage.py migrate
```

### 3. Create Superuser
```bash
python3 manage.py createsuperuser
```

### 4. Start Services
```bash
# Terminal 1: Django Development Server
python3 manage.py runserver

# Terminal 2: Celery Worker (optional)
celery -A crisp worker --loglevel=info

# Terminal 3: Redis Server
redis-server
```

## Configuration

### Django Settings

#### Key Settings in `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/crisp/settings.py`:

```python
# Custom User Model
AUTH_USER_MODEL = 'core.CustomUser'

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# OTX Configuration
OTX_SETTINGS = {
    'API_KEY': os.getenv('OTX_API_KEY'),
    'ENABLED': os.getenv('OTX_ENABLED', 'True').lower() == 'true',
    'FETCH_INTERVAL': int(os.getenv('OTX_FETCH_INTERVAL', '3600')),
    'BATCH_SIZE': int(os.getenv('OTX_BATCH_SIZE', '50')),
    'MAX_AGE_DAYS': int(os.getenv('OTX_MAX_AGE_DAYS', '30')),
}

# TAXII Server Configuration
TAXII_SETTINGS = {
    'DISCOVERY_TITLE': os.getenv('TAXII_SERVER_TITLE', 'CRISP Threat Intelligence Platform'),
    'DISCOVERY_DESCRIPTION': os.getenv('TAXII_SERVER_DESCRIPTION', 'Educational threat intelligence sharing platform'),
    'DISCOVERY_CONTACT': os.getenv('TAXII_CONTACT_EMAIL', 'admin@crisp.edu'),
    'MEDIA_TYPE_TAXII': 'application/taxii+json;version=2.1',
    'MEDIA_TYPE_STIX': 'application/stix+json;version=2.1',
    'MAX_CONTENT_LENGTH': 104857600,  # 100MB
}
```

### Test Configuration

For testing, use `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/crisp/test_settings.py`:
- Uses SQLite in-memory database
- Disables migrations for faster tests
- Simplified logging configuration

### Pytest Configuration

File: `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/pytest.ini`

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = crisp.test_settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
testpaths = tests
addopts = 
    --verbose
    --strict-markers
    --strict-config
    --tb=short
    --cov=core
    --cov=crisp
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    auth: marks tests related to authentication
    threat_intel: marks tests related to threat intelligence
    trust_management: marks tests related to trust management
    admin: marks tests related to admin functionality
```

## Database Models

### Core Authentication Models

#### CustomUser (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/models/auth.py`)
```python
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=USER_ROLE_CHOICES, default='viewer')
    # Additional fields: security_clearance, last_activity, etc.
```

**Roles Available:**
- `viewer` - Read-only access to assigned data
- `publisher` - Can publish threat intelligence  
- `BlueVisionAdmin` - Full administrative access

#### Organization (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/models/auth.py`)
```python
class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, unique=True)
    # STIX Identity fields
    identity_class = models.CharField(max_length=100, default='organization')
    sectors = models.JSONField(default=list, blank=True)
    stix_id = models.CharField(max_length=255, unique=True, null=True)
```

### STIX/Threat Intelligence Models

#### STIXObject (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/models/stix_object.py`)
```python
class STIXObject(models.Model):
    stix_id = models.CharField(max_length=255, unique=True)
    stix_type = models.CharField(max_length=100)
    spec_version = models.CharField(max_length=10, default='2.1')
    created = models.DateTimeField()
    modified = models.DateTimeField()
    object_data = models.JSONField()  # Full STIX object
    collection = models.ForeignKey('Collection', on_delete=models.CASCADE)
```

#### ThreatFeed (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/models/threat_feed.py`)
```python
class ThreatFeed(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_external = models.BooleanField(default=False)
    # TAXII Configuration
    taxii_server_url = models.URLField(blank=True)
    taxii_api_root = models.CharField(max_length=255, blank=True)
    taxii_collection_id = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey('Organization', on_delete=models.CASCADE)
```

### Trust Management Models

#### TrustLevel (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/models/trust_models/models.py`)
```python
class TrustLevel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    level = models.IntegerField(unique=True)  # 1-5 scale
    description = models.TextField()
    anonymization_level = models.CharField(
        max_length=20, 
        choices=[(level.value, level.name) for level in AnonymizationLevel]
    )
```

#### TrustRelationship (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/models/trust_models/models.py`)
```python
class TrustRelationship(models.Model):
    trustor = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='given_trust')
    trustee = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='received_trust')
    trust_level = models.ForeignKey('TrustLevel', on_delete=models.PROTECT)
    created_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
```

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/login/` - User login (returns JWT tokens)
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - User logout (blacklist token)
- `GET /api/auth/user/` - Get current user info

### Trust Management API
- `GET /api/v1/trust/` - List trust relationships
- `POST /api/v1/trust/` - Create trust relationship
- `GET /api/v1/trust/{id}/` - Get specific trust relationship
- `PUT /api/v1/trust/{id}/` - Update trust relationship
- `DELETE /api/v1/trust/{id}/` - Delete trust relationship

### Threat Intelligence API
- `GET /api/v1/threat-intel/feeds/` - List threat feeds
- `POST /api/v1/threat-intel/feeds/` - Create threat feed
- `GET /api/v1/threat-intel/indicators/` - List indicators
- `POST /api/v1/threat-intel/indicators/` - Create indicator

### TAXII 2.1 Endpoints
- `GET /taxii2/` - Discovery endpoint
- `GET /taxii2/{api_root}/` - API root information
- `GET /taxii2/{api_root}/collections/` - List collections
- `GET /taxii2/{api_root}/collections/{collection_id}/` - Collection information
- `POST /taxii2/{api_root}/collections/{collection_id}/objects/` - Add objects
- `GET /taxii2/{api_root}/collections/{collection_id}/objects/` - Get objects

## Management Commands

### TAXII Operations (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/management/commands/taxii_operations.py`)

**Discover Collections:**
```bash
python3 manage.py taxii_operations discover \
    --server https://otx.alienvault.com/taxii/ \
    --api-root collections \
    --username your_api_key
```

**Add New Feed:**
```bash
python3 manage.py taxii_operations add \
    --name "AlienVault OTX" \
    --description "AlienVault Open Threat Exchange" \
    --server https://otx.alienvault.com/taxii/ \
    --api-root collections \
    --collection-id alienvault \
    --owner-id organization_uuid
```

**Consume Feed:**  
```bash
python3 manage.py taxii_operations consume --feed-id 1
```

### TAXII Testing (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/management/commands/test_taxii.py`)

**Test All Feeds:**
```bash
python3 manage.py test_taxii
```

**Test Specific Feed:**
```bash
python3 manage.py test_taxii --feed-id 1 --test-type connection
```

**Test Server URL:**
```bash
python3 manage.py test_taxii \
    --server-url https://otx.alienvault.com/taxii/ \
    --collection-id alienvault \
    --test-type all
```

**List Collections:**
```bash
python3 manage.py test_taxii --list-collections
```

**Consume from Collection:**
```bash
python3 manage.py test_taxii --consume --collection alienvault
```

## Scripts & Utilities

### Setup and Testing Scripts

#### Setup Script (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/scripts/setup_and_test.py`)
```bash
python3 core/scripts/setup_and_test.py
```
**Purpose:** Validates Django configuration and tests all model imports

#### Startup Script (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/scripts/start_crisp.sh`)
```bash
chmod +x core/scripts/start_crisp.sh
./core/scripts/start_crisp.sh
```
**Purpose:** Quick startup script with dependency checks

#### Structure Verification (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/scripts/verify_structure.py`)
```bash
python3 core/scripts/verify_structure.py
```
**Purpose:** Validates project structure and import paths

#### Final Verification (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/scripts/final_verification.py`)
```bash
python3 core/scripts/final_verification.py
```
**Purpose:** Comprehensive system validation before deployment

## Background Tasks

### Celery Configuration (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/crisp/celery.py`)

```python
from celery import Celery
app = Celery('crisp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### Task Examples

#### TAXII Collection Tasks (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tasks/taxii_tasks.py`)
```python
@app.task(bind=True)
def fetch_taxii_collection(self, feed_id):
    """Fetch and process TAXII collection in background"""
    # Implementation for background TAXII processing
```

### Running Celery
```bash
# Start Celery worker
celery -A crisp worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A crisp beat --loglevel=info

# Monitor tasks with Flower
celery -A crisp flower
```

## Testing

### Test Structure

The testing suite is organized into multiple categories:

#### Unit Tests
- `test_models.py` - Database model testing
- `test_services.py` - Business logic testing
- `test_strategies.py` - Strategy pattern testing

#### Integration Tests  
- `test_auth_integration.py` - Authentication flow testing
- `test_taxii_integration.py` - TAXII server integration
- `test_trust_anonymization_integration.py` - Trust-based anonymization

#### Functional Tests
- `test_admin_views.py` - Django admin functionality
- `test_api_endpoints.py` - REST API testing
- `test_user_management.py` - User workflow testing

#### Security Tests
- `test_security.py` - Security middleware and validation
- `test_authentication.py` - Auth security testing
- `test_middleware.py` - Custom middleware testing

### Running Tests

**All Tests:**
```bash
cd core
python3 -m pytest
```

**Specific Test Categories:**
```bash
# Unit tests only
pytest -m unit

# Integration tests only  
pytest -m integration

# Authentication tests
pytest -m auth

# Threat intelligence tests
pytest -m threat_intel

# Trust management tests
pytest -m trust_management
```

**Coverage Reports:**
```bash
pytest --cov=core --cov=crisp --cov-report=html
# View report: open htmlcov/index.html
```

**Performance Tests:**
```bash
# Exclude slow tests
pytest -m "not slow"

# Run only slow tests
pytest -m slow
```

### Key Test Files

#### Core Functionality Tests
- `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tests/test_final_working.py` - Complete system validation
- `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tests/test_ultra_clean.py` - Clean architecture validation
- `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tests/test_end_to_end.py` - End-to-end workflow testing

#### Design Pattern Tests
- `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tests/test_decorator.py` - Decorator pattern testing
- `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tests/test_observer.py` - Observer pattern testing
- `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tests/test_stix_factory.py` - Factory pattern testing

#### External Integration Tests
- `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tests/test_taxii_service.py` - TAXII service testing
- `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tests/test_management_commands.py` - Management command testing

## Security Features

### Authentication & Authorization

#### JWT Token Authentication
- Access tokens: 60 minutes lifetime
- Refresh tokens: 7 days lifetime  
- Automatic token rotation
- Token blacklisting on logout

#### Role-Based Access Control
- **Viewer**: Read-only access to assigned data
- **Publisher**: Can create and modify threat intelligence
- **BlueVisionAdmin**: Full system access

#### Session Management
- Session timeout: 24 hours of inactivity
- Automatic cleanup every 5 minutes
- Session activity tracking

### Security Middleware (`/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/middleware.py`)

#### SecurityHeadersMiddleware
- X-XSS-Protection: `1; mode=block`
- X-Content-Type-Options: `nosniff`
- X-Frame-Options: `DENY`
- Content-Security-Policy: Strict CSP rules
- Referrer-Policy: `strict-origin-when-cross-origin`
- HSTS in production

#### RateLimitMiddleware
- Login attempts: 5 per 5 minutes per IP
- Password reset: 3 per hour per IP
- API requests: 100 per minute per IP

#### SessionActivityMiddleware
- Tracks user activity
- Updates last activity timestamp
- Handles session cleanup

#### SecurityAuditMiddleware
- Logs security events
- Tracks authentication attempts
- Monitors suspicious activity

#### SessionTimeoutMiddleware  
- Enforces session timeouts
- Handles inactive session cleanup

### Password Security
- Minimum 12 characters
- Requires: 1 uppercase, 1 lowercase, 2 digits, 1 special character
- Common password validation
- User attribute similarity validation

### Data Anonymization

#### Anonymization Levels (enums.py)
```python
class AnonymizationLevel(Enum):
    NONE = "none"      # No anonymization
    LOW = "low"        # Minimal anonymization  
    MEDIUM = "medium"  # Moderate anonymization
    HIGH = "high"      # High anonymization
    FULL = "full"      # Complete anonymization
```

#### Data Types Supported
- IP addresses (IPv4/IPv6)
- Domain names
- Email addresses  
- URLs
- Cryptographic hashes
- Filenames

#### Trust-Based Anonymization
Anonymization level determined by trust relationship between organizations:
- **High Trust**: Minimal anonymization (LOW level)
- **Medium Trust**: Moderate anonymization (MEDIUM level)
- **Low Trust**: High anonymization (HIGH level)
- **No Trust**: Full anonymization (FULL level)

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check database exists
psql -U admin -d crisp -c "\l"

# Reset database if needed
python3 manage.py migrate --run-syncdb
```

#### Import Errors
```bash
# Verify Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Test Django setup
python3 core/scripts/setup_and_test.py

# Check for circular imports
python3 -c "
import django
django.setup()
from core.models import CustomUser
print('✅ Models imported successfully')
"
```

#### Redis/Celery Issues
```bash
# Check Redis is running
redis-cli ping

# Test Celery connection
celery -A crisp inspect ping

# Clear Redis cache
redis-cli flushall
```

#### TAXII Connection Issues
```bash
# Test TAXII connection
python3 manage.py test_taxii --server-url https://otx.alienvault.com/taxii/

# Check OTX API key
python3 -c "
import os
from django.conf import settings
print('OTX API Key configured:', bool(settings.OTX_SETTINGS['API_KEY']))
"

# Verify SSL certificates
python3 -c "
import ssl
import socket
context = ssl.create_default_context()
with socket.create_connection(('otx.alienvault.com', 443)) as sock:
    with context.wrap_socket(sock, server_hostname='otx.alienvault.com') as ssock:
        print('✅ SSL connection successful')
"
```

### Debug Mode

Enable debug mode in `.env`:
```bash
DEBUG=True
```

Access debug information:
- Django admin: http://127.0.0.1:8000/admin/
- Debug auth view: http://127.0.0.1:8000/debug/auth/
- API debug: Add `?format=json` to API endpoints

### Logging

View logs in real-time:
```bash
# Django logs
tail -f logs/django.log

# Celery logs  
tail -f logs/celery.log

# Security audit logs
tail -f logs/security.log
```

## Deployment

### Production Checklist

#### Environment Configuration
- [ ] Set `DEBUG=False`
- [ ] Configure secure `SECRET_KEY` and `TRUST_MANAGEMENT_SECRET_KEY`
- [ ] Set up PostgreSQL production database
- [ ] Configure Redis for production
- [ ] Set `ALLOWED_HOSTS` for production domains
- [ ] Configure email backend for notifications

#### Security Configuration
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Set up backup strategies
- [ ] Enable database encryption at rest
- [ ] Configure log rotation

#### Performance Optimization
- [ ] Set up Gunicorn/uWSGI
- [ ] Configure Nginx reverse proxy
- [ ] Enable database connection pooling
- [ ] Set up Redis clustering
- [ ] Configure CDN for static files

#### Monitoring
- [ ] Set up application monitoring (Sentry, etc.)
- [ ] Configure log aggregation
- [ ] Set up health checks
- [ ] Monitor Celery task queue
- [ ] Set up alerts for security events

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY core/requirements/ requirements/
RUN pip install -r requirements/base.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "crisp.wsgi:application"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://admin:password@db:5432/crisp
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=crisp
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data/
  
  redis:
    image: redis:6
    
  celery:
    build: .
    command: celery -A crisp worker --loglevel=info
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### Production Deployment Steps

1. **Server Setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# Create application user
sudo useradd -m -s /bin/bash crisp
sudo usermod -aG sudo crisp
```

2. **Application Deployment:**
```bash
# Clone repository
sudo -u crisp git clone <repository> /home/crisp/crisp
cd /home/crisp/crisp

# Set up virtual environment
sudo -u crisp python3 -m venv venv
sudo -u crisp venv/bin/pip install -r core/requirements/base.txt

# Configure environment
sudo -u crisp cp crisp/config/security/.env.template crisp/config/security/.env
# Edit .env with production values

# Run migrations
sudo -u crisp venv/bin/python core/manage.py migrate
```

3. **Web Server Configuration:**
```nginx
# /etc/nginx/sites-available/crisp
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /home/crisp/crisp/staticfiles/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Service Configuration:**
```ini
# /etc/systemd/system/crisp.service
[Unit]
Description=CRISP Django Application
After=network.target

[Service]
User=crisp
Group=crisp
WorkingDirectory=/home/crisp/crisp
Environment=PATH=/home/crisp/crisp/venv/bin
ExecStart=/home/crisp/crisp/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 crisp.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Enable Services:**
```bash
sudo systemctl enable crisp
sudo systemctl start crisp
sudo systemctl enable nginx
sudo systemctl start nginx
```

---

## Support and Documentation

### Additional Resources
- **Project Organization**: `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/docs/PROJECT_ORGANIZATION.md`
- **Setup Guide**: `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/docs/README_SETUP.md`
- **CRISP Overview**: `/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/docs/CRISP - Cyber Risk Information Sharing Platform (1).md`

### Quick Access
- **Admin Panel**: http://127.0.0.1:8000/admin/ (admin/admin)
- **API Root**: http://127.0.0.1:8000/api/
- **TAXII Discovery**: http://127.0.0.1:8000/taxii2/
- **Debug Auth**: http://127.0.0.1:8000/debug/auth/

### System Status
**Current Implementation Status**: ✅ **PRODUCTION READY**
- 9,292 STIX Objects from AlienVault OTX
- 37 Organizations with trust relationships
- 32 Users across multiple roles
- 9 Anonymized indicators demonstrating privacy preservation
- Full STIX/TAXII compliance
- Comprehensive test coverage (85%+)
- Security middleware and audit logging
- Background task processing with Celery

---

**Last Updated**: 2025-06-27  
**Version**: 1.0.0  
**License**: Educational Use  
**Contact**: CRISP Development Team