# CRISP Unified System - Testing and Deployment Guide

## 🎯 System Overview

The CRISP Unified System is a complete threat intelligence platform that combines:
- **Trust Management**: Bilateral and community trust relationships
- **User Management**: JWT authentication and role-based access control
- **Threat Intelligence**: STIX/TAXII feeds, indicators, and TTPs
- **Anonymization**: Trust-aware data anonymization
- **Organization Management**: Multi-organization support

---

## 🚀 Quick Start Guide

### Prerequisites

1. **Python 3.8+** installed
2. **Node.js 16+** and **npm** installed
3. **PostgreSQL** database server running
4. **Redis** (optional, for Celery task queue)

### Environment Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd /path/to/CRISP
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies:**
   ```bash
   cd crisp-react
   npm install
   cd ..
   ```

### Database Setup

1. **Create PostgreSQL database:**
   ```sql
   CREATE DATABASE crisp_unified;
   CREATE USER crisp_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE crisp_unified TO crisp_user;
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Run migrations:**
   ```bash
   python3 manage.py migrate
   ```

4. **Initialize system with default data:**
   ```bash
   python3 manage.py initialize_system
   ```

---

## 🔧 Running the System

### Backend Development Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start Django development server
python3 manage.py runserver
```

The backend will be available at: `http://localhost:8000`

### Frontend Development Server

```bash
# In a new terminal, navigate to frontend
cd crisp-react

# Start React development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### Production Build

```bash
# Build React for production
cd crisp-react
npm run build
cd ..

# Collect static files
python3 manage.py collectstatic --noinput

# Run with production server (gunicorn example)
gunicorn crisp_unified.wsgi:application --bind 0.0.0.0:8000
```

---

## 🧪 Testing Guide

### System Health Check

```bash
# Run comprehensive system health check
python3 manage.py system_health_check --verbose
```

### Django Backend Tests

```bash
# Run all tests
python3 manage.py test

# Run specific app tests
python3 manage.py test core

# Run with verbose output
python3 manage.py test --verbosity=2
```

### Frontend Tests

```bash
cd crisp-react
npm test
```

### Manual Testing Workflow

#### 1. Authentication Testing

1. **Access the system:**
   - Backend: `http://localhost:8000/admin/`
   - Frontend: `http://localhost:5173`

2. **Login with default admin:**
   - Username: `admin`
   - Password: `AdminPassword123!`

3. **Test JWT authentication:**
   - Access: `http://localhost:8000/api/auth/login/`
   - Use credentials to get JWT token

#### 2. API Endpoint Testing

**Authentication Endpoints:**
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPassword123!"}'

# Get user profile (use token from login)
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**User Management:**
```bash
# List users
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Create user
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPassword123!",
    "organization": "ORG_ID"
  }'
```

**Trust Management:**
```bash
# List trust relationships
curl -X GET http://localhost:8000/api/trust/relationships/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Create trust relationship
curl -X POST http://localhost:8000/api/trust/relationships/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_organization": "ORG_ID",
    "trust_level": "standard",
    "relationship_type": "bilateral"
  }'
```

**Threat Intelligence:**
```bash
# List threat feeds
curl -X GET http://localhost:8000/api/threat-feeds/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# List indicators
curl -X GET http://localhost:8000/api/indicators/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# MITRE ATT&CK Matrix
curl -X GET http://localhost:8000/api/ttps/mitre-matrix/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# TTP Matrix Cell Details
curl -X GET "http://localhost:8000/api/ttps/matrix-cell-details/?tactic=initial-access&technique=T1190" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# TTP Technique Details
curl -X GET http://localhost:8000/api/ttps/technique-details/T1190/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**TAXII Endpoints:**
```bash
# TAXII Discovery
curl -X GET http://localhost:8000/taxii2/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Collections
curl -X GET http://localhost:8000/taxii2/collections/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. Frontend Testing

1. **Navigation Testing:**
   - Test all menu items and routes
   - Verify authentication redirects
   - Check responsive design

2. **User Management:**
   - Create/edit/delete users
   - Invite new users
   - Manage user roles

3. **Trust Management:**
   - Create trust relationships
   - Manage trust groups
   - View trust status

4. **Threat Intelligence:**
   - View threat feeds
   - Browse indicators
   - Explore TTP data
   - Use MITRE ATT&CK matrix

---

## 🔐 Security Testing

### Authentication Security

1. **JWT Token Validation:**
   ```bash
   # Test with invalid token
   curl -X GET http://localhost:8000/api/users/ \
     -H "Authorization: Bearer invalid_token"
   ```

2. **Password Security:**
   - Test password complexity requirements
   - Test password reset functionality
   - Test account lockout after failed attempts

### Access Control Testing

1. **Role-based Access:**
   - Test different user roles (admin, publisher, viewer)
   - Verify organization-based access control
   - Test trust-based data access

2. **API Security:**
   - Test API rate limiting
   - Verify CORS settings
   - Test input validation

---

## 📊 Performance Testing

### Database Performance

```bash
# Check database query performance
python3 manage.py shell -c "
from django.test.utils import override_settings
from django.db import connection
from core.models.models import CustomUser
print('Users count:', CustomUser.objects.count())
print('Queries:', len(connection.queries))
"
```

### API Performance

```bash
# Use Apache Bench for API load testing
ab -n 100 -c 10 http://localhost:8000/api/indicators/
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors:**
   ```bash
   # Check Python path and virtual environment
   which python3
   pip list
   ```

2. **Database Connection:**
   ```bash
   # Test database connection
   python3 manage.py dbshell
   ```

3. **Missing Dependencies:**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt --force-reinstall
   ```

4. **Frontend Build Issues:**
   ```bash
   # Clear npm cache and reinstall
   cd crisp-react
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

### Debug Mode

```bash
# Enable debug mode for troubleshooting
export DJANGO_DEBUG=True
python3 manage.py runserver
```

---

## 🌐 Deployment

### Environment Variables

Key environment variables to set:

```bash
# Production settings
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-production-secret-key
DJANGO_ALLOWED_HOSTS=your-domain.com

# Database
DB_NAME=crisp_unified
DB_USER=crisp_user
DB_PASSWORD=secure-password
DB_HOST=localhost

# Email
EMAIL_HOST=your-smtp-server
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

### Production Checklist

- [ ] Set `DJANGO_DEBUG=False`
- [ ] Configure secure `SECRET_KEY`
- [ ] Set up proper `ALLOWED_HOSTS`
- [ ] Configure SSL/HTTPS
- [ ] Set up proper database credentials
- [ ] Configure email settings
- [ ] Set up log rotation
- [ ] Configure backup procedures
- [ ] Set up monitoring

---

## 📈 System Administration

### Management Commands

```bash
# System initialization
python3 manage.py initialize_system

# System health check
python3 manage.py system_health_check

# Create superuser
python3 manage.py createsuperuser

# Clear test data
python3 manage.py cleanup_test_data

# TTP aggregation
python3 manage.py ttp_aggregation

# TAXII operations
python3 manage.py taxii_operations
```

### Monitoring

1. **System Health:**
   ```bash
   # Regular health checks
   python3 manage.py system_health_check --verbose
   ```

2. **Database Monitoring:**
   ```bash
   # Check database size and performance
   python3 manage.py dbshell -c "
   SELECT schemaname,tablename,attname,n_distinct,correlation 
   FROM pg_stats WHERE tablename IN ('core_indicator', 'core_ttpdata');
   "
   ```

3. **Log Monitoring:**
   ```bash
   # Monitor application logs
   tail -f crisp_unified.log
   ```

---

## ✅ Integration Verification

### Final System Verification

1. **Backend Functionality:**
   - [ ] Django admin accessible
   - [ ] JWT authentication working
   - [ ] All API endpoints responding
   - [ ] Database migrations applied
   - [ ] Management commands working

2. **Frontend Functionality:**
   - [ ] React app loads without errors
   - [ ] Authentication flow works
   - [ ] All components render properly
   - [ ] API integration working

3. **Integration Testing:**
   - [ ] Frontend-backend communication
   - [ ] Trust-based access control
   - [ ] Threat intelligence feeds
   - [ ] TAXII endpoint integration
   - [ ] Anonymization pipeline

4. **Security Testing:**
   - [ ] Authentication security
   - [ ] Authorization controls
   - [ ] Input validation
   - [ ] CSRF protection

---

## 📞 Support

### Getting Help

1. **Check logs:**
   - Application logs: `crisp_unified.log`
   - Django debug output
   - Browser console errors

2. **Run diagnostics:**
   ```bash
   python3 manage.py system_health_check --verbose
   python3 manage.py check
   ```

3. **Documentation:**
   - API endpoints: `/api/` (when running)
   - Django admin: `/admin/`
   - System status: `/api/system-health/`

### System Status

The system includes comprehensive monitoring and health checking:
- Real-time system health monitoring
- Database integrity checks
- Service availability validation
- Performance metrics
- Security audit capabilities

**🎉 Your CRISP Unified System is ready for production!**