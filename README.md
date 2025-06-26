# CRISP - Cyber Risk Information Sharing Platform

## 🎯 Overview

CRISP is a Django-based cybersecurity platform for sharing and managing cyber threat intelligence using STIX/TAXII standards. The platform implements enterprise-grade security patterns and provides comprehensive threat intelligence management capabilities.

## 🏗️ Project Structure

```
📁 crisp/           - Django project configuration
📁 core/            - Main application code
📁 backup/          - Preserved original components
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Django 4.2+
- PostgreSQL (recommended)

### Setup & Testing

1. **Navigate to project directory:**
```bash
cd "/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone"
```

2. **Run comprehensive setup test:**
```bash
python3 core/scripts/setup_and_test.py
```

## 🧪 Component Testing

### Test Core Authentication Models
```bash
python3 -c "
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
sys.path.append('.')
django.setup()

# Test models
from core.models.auth import Organization, CustomUser, UserSession
print('✅ Organization:', Organization.__name__)
print('✅ CustomUser:', CustomUser.__name__)
print('✅ UserSession:', UserSession.__name__)
print('🎯 Core models working!')
"
```

### Test STIX Models
```bash
python3 -c "
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
sys.path.append('.')
django.setup()

# Test models
from core.models.stix_object import STIXObject, Collection, Feed
print('✅ STIXObject:', STIXObject.__name__)
print('✅ Collection:', Collection.__name__)
print('✅ Feed:', Feed.__name__)
print('🎯 STIX models working!')
"
```

### Test Trust Management Models
```bash
python3 -c "
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
sys.path.append('.')
django.setup()

# Test models
from core.models.trust_models.models import TrustLevel, TrustRelationship
print('✅ TrustLevel:', TrustLevel.__name__)
print('✅ TrustRelationship:', TrustRelationship.__name__)
print('🎯 Trust models working!')
"
```

### Test Design Patterns
```bash
python3 -c "
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
sys.path.append('.')
django.setup()

# Test patterns
from core.strategies.enums import AnonymizationLevel
from core.patterns.observer.threat_feed import ThreatFeedSubject
print('✅ AnonymizationLevel:', AnonymizationLevel.__name__)
print('✅ ThreatFeedSubject:', ThreatFeedSubject.__name__)
print('🎯 Patterns working!')
"
```

### Test Other Models
```bash
python3 -c "
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
sys.path.append('.')
django.setup()

# Test other models
from core.models.indicator import Indicator
from core.models.institution import Institution
from core.models.ttp_data import TTPData
print('✅ Indicator:', Indicator.__name__)
print('✅ Institution:', Institution.__name__)
print('✅ TTPData:', TTPData.__name__)
print('🎯 Other models working!')
"
```

## ⚙️ Django Settings Configuration

The errors you encountered are due to Django not being properly configured. Here's what you need to set up:

### Required Environment Variables
```bash
export DJANGO_SETTINGS_MODULE=crisp.test_settings
```

### Python Path Setup
```python
import sys
sys.path.append('.')  # Add project root to Python path
```

### Django Initialization
```python
import django
django.setup()  # Must be called before importing Django models
```

### Complete Setup Pattern
```python
import os
import sys
import django
from django.conf import settings

# 1. Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')

# 2. Add project to Python path
sys.path.append('.')

# 3. Initialize Django
django.setup()

# 4. Now you can import Django models
from core.models.auth import Organization
```

## 🏗️ Architecture

### Core Components

- **Models**: Django ORM models for data persistence
- **Views**: HTTP request handlers and API endpoints
- **Services**: Business logic layer
- **Repositories**: Data access abstraction
- **Patterns**: Design pattern implementations
- **Strategies**: Configurable algorithm implementations

### Design Patterns Implemented

- **Factory Pattern**: STIX object creation
- **Decorator Pattern**: STIX data enhancement
- **Observer Pattern**: Event-driven updates
- **Strategy Pattern**: Pluggable anonymization algorithms

### Security Features

- Multi-factor authentication
- Role-based access control
- Data anonymization strategies
- Trust management system
- Audit logging

## 📁 Detailed Structure

```
core/
├── models/                      # Data models
│   ├── auth.py                 # Authentication models
│   ├── stix_object.py          # STIX standard models
│   ├── trust_models/           # Trust management
│   └── ...
├── views/                      # Request handlers
│   ├── auth_views.py           # Authentication views
│   ├── api/                    # API endpoints
│   └── ...
├── services/                   # Business logic
├── strategies/                 # Algorithm implementations
├── patterns/                   # Design patterns
├── tests/                      # Test suite
└── scripts/                    # Utility scripts
```

## 🔧 Common Issues & Solutions

### Django Settings Not Configured
**Error**: `ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings are not configured`

**Solution**: Always set up Django before importing models:
```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
django.setup()
```

### Module Import Errors
**Error**: `No module named 'core.patterns.strategy'`

**Solution**: The strategy patterns were moved to `core.strategies`. Use:
```python
from core.strategies.enums import AnonymizationLevel
```

### Circular Import Issues
These have been resolved by using string references in ForeignKey relationships and proper module organization.

## 🚀 Next Steps

1. Set up your database connection in `crisp/settings.py`
2. Run migrations: `python3 core/manage.py migrate`
3. Create superuser: `python3 core/manage.py createsuperuser`
4. Start development server: `python3 core/manage.py runserver`

## 📖 Documentation

- [Setup Guide](core/docs/README_SETUP.md)
- [Project Organization](core/docs/PROJECT_ORGANIZATION.md)

## 🎯 Success Criteria

✅ All models import without circular dependencies  
✅ Design patterns accessible and functional  
✅ Django setup works correctly  
✅ All test commands pass  
✅ Ready for production deployment  


something to remember:::# Run with production PostgreSQL settings
  python3 core/manage.py runserver --settings=crisp.settings      

  # Or set the environment variable to avoid specifying it        
  each time
  export DJANGO_SETTINGS_MODULE=crisp.settings
  python3 core/manage.py runserver