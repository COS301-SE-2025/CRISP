# 🔐 CRISP Trust Management Platform

## 📋 Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Database Population](#database-population)
- [Testing](#testing)
- [Development](#development)
- [Security Testing](#security-testing)
- [Docker Deployment](#docker-deployment)
- [Troubleshooting](#troubleshooting)

## 📖 Overview

CRISP (Cyber Risk Intelligence Sharing Platform) is a comprehensive trust management system for threat intelligence sharing. Built with Django (backend) and React (frontend), it provides organizations with secure, trust-based information sharing capabilities.

### Key Features
- 🛡️ Trust-based access control
- 📊 Threat intelligence feeds
- 🔄 TAXII/STIX integration
- 👥 Multi-organization support
- 📈 Analytics and reporting
- 🔒 Advanced security controls
- 🎯 **Asset-Based Alert System (WOW Factor #1)**
  - Custom threat correlation with client infrastructure
  - Multi-channel alert delivery (email, SMS, Slack, webhooks)
  - Asset criticality-based prioritization
  - Real-time IoC correlation
- 🧠 **User Behavior Analytics (WOW Factor #2)**
  - Statistical anomaly detection for suspicious user activities
  - Behavioral baseline learning and pattern recognition
  - Real-time activity monitoring and session tracking
  - Comprehensive system logs export (CSV/JSON)
  - Advanced threat hunting capabilities
  - Optional ML-enhanced detection with scikit-learn

## 🗂️ Project Structure

```
Capstone-Unified/
├── core/                           # Django backend
│   ├── models/                     # Database models
│   ├── api/                        # REST API endpoints
│   ├── services/                   # Business logic
│   ├── management/commands/        # Custom Django commands
│   └── tests/                      # Backend tests
├── crisp-react/                    # React frontend
│   ├── src/components/             # React components
│   ├── src/test/                   # Frontend tests
│   └── node_modules/               # Node dependencies
├── scripts/                        # Utility scripts
├── security-testing/              # Security test configs
├── docs/                          # Documentation
├── requirements.txt               # Python dependencies
├── package.json                   # Node scripts
└── *.sh                          # Setup/testing scripts
```

## ✅ Prerequisites

### Required Software
- **Python 3.10+** with pip
- **PostgreSQL 12+**
- **Node.js 18+** with npm
- **Git**

### System Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2

## 🚀 Quick Start

### 🎯 One-Click Deployment with Asset-Based Alert System

**Want to see the complete Asset-Based Alert System in action?** Use our one-click deployment:

```bash
# Clone the repository
git clone <repository-url>
cd CRISP/Capstone-Unified

# One-click deployment with Asset-Based Alert System
chmod +x run-crisp-with-asset-alerts.sh
./run-crisp-with-asset-alerts.sh
```

This will:
- 🐳 Build and start all Docker containers
- 🗄️ Set up database with migrations
- 🎯 Deploy the Asset-Based Alert System (WOW Factor #1)
- 👤 Create demo user: `demo_security_admin` / `<A securely generated password will be displayed on startup>`
- 🏢 Set up "Demo University" with sample assets
- 🚨 Generate demo alerts showing threat correlation
- 🌐 Launch frontend at http://localhost:5173

**Access the Asset-Based Alert System:**
1. Go to http://localhost:5173
2. Login with the generated credentials displayed in the console
3. Navigate to **Management → Asset-Based Alerts**
4. Explore the asset inventory and custom alerts!

---

### 🛠️ Manual Setup (Alternative)

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd CRISP/Capstone-Unified
```

### 2. Database Setup
```bash
# Run the automated PostgreSQL setup
chmod +x setup_postgresql.sh
./setup_postgresql.sh
```

### 3. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Set up Asset-Based Alert System
python manage.py demo_asset_alerts --mode setup
python manage.py demo_asset_alerts --mode demo
```

### 4. Frontend Setup
```bash
# Navigate to React app and install dependencies
cd crisp-react
npm install
cd ..
```

### 5. Populate Database with Test Data
```bash
# Run the massive database population script
python manage.py populate_database

# Optional: Add additional threat intelligence data
python manage.py populate_otx_threats
python manage.py populate_ttp_data
```

### 6. Start the Application
```bash
# Terminal 1: Start Django backend
python manage.py runserver

# Terminal 2: Start React frontend
cd crisp-react
npm run dev
```

### 7. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1/
- **Django Admin**: http://localhost:8000/admin/

## 🔧 Detailed Setup

### Database Configuration

#### Manual PostgreSQL Setup
If the automated script fails:

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Set password for postgres user
sudo -u postgres psql -c "ALTER USER postgres PASSWORD '<your_secure_password>';"

# Create database
sudo -u postgres createdb crisp_unified

# Test connection
PGPASSWORD='<your_secure_password>' psql -h localhost -U postgres -d crisp_unified -c "SELECT version();"
```

#### Environment Configuration
Ensure your `.env` file contains:
```bash
# Database
DB_NAME=crisp_unified
DB_USER=postgres
DB_PASSWORD=<your_secure_password>
DB_HOST=localhost
DB_PORT=5432

# Django
DEBUG=True
SECRET_KEY=(your-secret-key)
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (for testing)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Backend Dependencies
```bash
# Install all Python packages
pip install -r requirements.txt

# If you encounter permission issues
pip install --user -r requirements.txt
```

### Frontend Dependencies
```bash
cd crisp-react

# Install Node packages
npm install

# Install Playwright for E2E tests
npx playwright install
```

## 🗄️ Database Population

### Core Population Script
The main database population command creates a comprehensive test environment:

```bash
# Run the massive database population script
# This creates: 50+ organizations, 500+ users, trust relationships, threat feeds
python manage.py populate_database
```

**What this creates:**
- 50+ Organizations with realistic hierarchies
- 500+ Users with varied roles and permissions
- Trust relationships between organizations
- Trust groups and memberships
- System activities and audit logs
- Sample threat intelligence data

### Additional Population Scripts
```bash
# Add Open Threat Exchange (OTX) threat data
python manage.py populate_otx_threats

# Add Tactics, Techniques, and Procedures (TTP) data
python manage.py populate_ttp_data

# Add demo reports and analytics data  
python manage.py populate_reports_demo

# Set up trust relationships (simplified version)
python manage.py populate_trust_relationships_simple

# Initialize trust levels
python manage.py init_trust_levels
```

### Complete Setup Command Sequence
```bash
# Full database setup and population
python manage.py migrate
python manage.py createsuperuser
python manage.py initialize_system
python manage.py populate_database
python manage.py populate_otx_threats
python manage.py populate_ttp_data
python manage.py init_trust_levels
```

## 🧪 Testing

### Quick Tests
```bash
# Run essential tests only (fast)
./run-quick-tests.sh
```

### Complete Test Suite
```bash
# Run all tests: backend, frontend, integration, E2E
./run-all-tests.sh

# With verbose output
./run-all-tests.sh --verbose

# Skip specific test types
./run-all-tests.sh --skip-frontend --skip-e2e
```

### Individual Test Categories

#### Backend Tests
```bash
# Django unit tests
python manage.py test

# Orchestrated test suite
python manage.py run_orchestrated_tests

# Specific test modules
python manage.py test core.tests.test_models
```

#### Frontend Tests
```bash
cd crisp-react

# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests with Playwright
npm run test:e2e

# All frontend tests
npm run test:all
```

#### Using NPM Scripts
```bash
# From project root, use package.json scripts
npm run test:all          # All tests
npm run test:quick        # Quick tests only
npm run test:backend      # Backend only
npm run test:frontend     # Frontend only
npm run test:e2e          # E2E only
```

### Test Data Management
```bash
# Reset database before tests
./reset_db.sh

# Clean up test data after tests
python manage.py cleanup_test_data
```

## 🛠️ Development

### Development Servers
```bash
# Backend development server (with auto-reload)
python manage.py runserver 0.0.0.0:8000

# Frontend development server (with hot reload)
cd crisp-react
npm run dev
```

### Database Management
```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database completely
./reset_db.sh

# Check database health
python manage.py system_health_check
```

### Useful Development Commands
```bash
# Django shell for database exploration
python manage.py shell

# Collect static files
python manage.py collectstatic

# Create new Django app
python manage.py startapp myapp

# Check for code issues
python manage.py check
```

## 🔒 Security Testing

### Quick Security Scan
```bash
# Run basic security diagnostics
./security-diagnostic.sh
```

### Comprehensive Security Testing
```bash
# Full security test suite (requires additional tools)
./run-security-tests.sh

# Setup security testing tools
./security-testing-setup.sh

# Individual security tests
./security-testing-individual.sh
```

### Security Tools Used
- **Bandit** - Python code security analysis
- **Safety** - Python dependency vulnerability scanning
- **OWASP ZAP** - Web application security testing
- **Nikto** - Web server scanner
- **Hydra** - Authentication brute force testing

## 🐳 Docker Deployment

### Quick Docker Start
```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d
```

### Docker Commands
```bash
# Build custom image
docker build -t crisp-platform .

# View logs
docker-compose logs -f

# Access container shell
docker-compose exec web bash

# Stop services
docker-compose down
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check port availability
netstat -an | grep 5432
```

#### Python/Django Issues
```bash
# Clear Python cache
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Reset migrations (CAUTION: data loss)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

#### Frontend Issues
```bash
cd crisp-react

# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear browser cache and restart
npm run dev -- --force
```

#### Permission Issues
```bash
# Fix script permissions
chmod +x *.sh

# Fix file permissions
sudo chown -R $USER:$USER .
```

### Performance Issues

#### Large Dataset Handling
```bash
# Monitor system resources during population
htop

# Run population in smaller batches
python manage.py populate_database --batch-size 10

# Clear test data if system becomes slow
python manage.py cleanup_test_data
```

### Debug Mode
```bash
# Enable Django debug mode
export DEBUG=True
python manage.py runserver

# Enable verbose logging
export LOG_LEVEL=DEBUG
```

## 📚 Additional Resources

### Documentation Files
- `SETUP.md` - Basic setup instructions
- `TESTING.md` - Detailed testing procedures
- `SECURITY_TESTING_GUIDE.md` - Security testing guide
- `LOAD_TESTING_GUIDE.md` - Performance testing guide
- `DOCKER_README.md` - Docker deployment guide
- `BEHAVIOR_ANALYTICS_SETUP.md` - User Behavior Analytics configuration guide

### API Documentation
- Django Admin: http://localhost:8000/admin/
- API Endpoints: http://localhost:8000/api/v1/
- API Documentation: http://localhost:8000/api/docs/ (if configured)

### Support
For issues and questions:
1. Check the troubleshooting section above
2. Review log files in `logs/` directory
3. Run system health check: `python manage.py system_health_check`
4. Check individual component status with respective test commands

---

## 🎯 Quick Commands Reference

```bash
# Complete setup from scratch
./setup_postgresql.sh && pip install -r requirements.txt && python manage.py migrate && python manage.py createsuperuser

# Populate massive test database
python manage.py populate_database

# Start development environment
python manage.py runserver & cd crisp-react && npm run dev

# Run all tests
./run-all-tests.sh

# Quick security check
./security-diagnostic.sh

# Reset everything
./reset_db.sh && python manage.py migrate && python manage.py populate_database
```

**Happy developing! 🚀**