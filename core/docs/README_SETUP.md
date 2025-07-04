# CRISP Ultra-Clean Structure - Setup Guide

## 🎯 Overview
The CRISP project has been reorganized into an ultra-clean structure with only 3 root directories:

```
📁 backup/     - Original components preserved
📁 core/       - ALL application code (models, views, patterns, etc.)
📁 crisp/      - Django project configuration only
```

## 🚀 Quick Setup & Testing

### 1. Navigate to Project Directory
```bash
cd "/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone"
```

### 2. Run Setup Script
```bash
python3 core/scripts/setup_and_test.py
```

## 🧪 Individual Component Testing

### Test Core Models
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

### Test Trust Models
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

## 🏗️ Structure Details

### Core Directory Structure
```
core/
├── models.py                    # Main Django models registration
├── admin.py                     # Django admin configuration
├── serializers.py               # API serializers
├── models/                      # Model packages
│   ├── __init__.py             # Clean exports (no circular imports)
│   ├── auth.py                 # Authentication models (Organization, CustomUser, etc.)
│   ├── stix_object.py          # STIX-related models
│   ├── indicator.py            # Indicator models
│   ├── institution.py          # Institution models
│   ├── threat_feed.py          # Threat feed models
│   ├── ttp_data.py            # TTP data models
│   └── trust_models/
│       └── models.py           # Trust management models
├── patterns/                    # Design patterns
│   ├── decorator/              # Decorator pattern (STIX decorators)
│   ├── factory/                # Factory pattern (STIX creators)
│   └── observer/               # Observer pattern (threat feed observers)
├── strategies/                  # Strategy pattern implementations
│   ├── enums.py                # Anonymization levels and other enums
│   ├── anonymization.py        # Anonymization strategies
│   ├── authentication_strategies.py # Auth strategies
│   └── ...other strategies
├── api/                        # API endpoints
│   ├── trust_api/              # Trust management API
│   ├── serializers/            # API serializers
│   └── views/                  # API views
├── views/                      # Django views
│   ├── auth_views.py           # Authentication views
│   ├── admin_views.py          # Admin views
│   └── api/                    # API views
├── services/                   # Business logic services
├── repositories/               # Data access layer
├── tests/                      # Test files
├── scripts/                    # Utility scripts
└── ...other core components
```

## 🔧 Key Fixes Applied

1. **Circular Import Resolution**: 
   - Removed direct imports from `core.models` in submodules
   - Used string references for ForeignKey relationships
   - Cleaned up `models/__init__.py` to avoid circular dependencies

2. **Path Configuration**:
   - Updated `manage.py` to handle Python path correctly
   - Created setup scripts for easy testing

3. **Model References**:
   - Changed `ForeignKey(Organization, ...)` to `ForeignKey('Organization', ...)`
   - Applied this fix across STIX models and trust models

## ✅ Verification Commands

Run these commands to verify everything is working:

```bash
# 1. Check directory structure
ls -la

# 2. Test all components
python3 core/scripts/setup_and_test.py

# 3. Verify imports work (with Django setup)
python3 -c "
import os
import sys
import django
from django.conf import settings

# Setup Django properly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
sys.path.append('.')
django.setup()

# Test STIX
from core.models.stix_object import STIXObject
print('STIXObject loaded:', STIXObject.__name__)

# Test Trust
from core.models.trust_models.models import TrustLevel
print('TrustLevel loaded:', TrustLevel.__name__)

print('🎯 All components working!')
"
```

## 🎯 Success Criteria

When everything is working correctly, you should see:

✅ Ultra-clean directory structure (only 3 root folders)  
✅ All model imports working without circular import errors  
✅ Design patterns accessible  
✅ Core functionality intact  
✅ Ready for Django integration  

## 🚀 Next Steps

1. Run the verification commands above
2. If any issues occur, check Python path configuration
3. For Django integration, ensure `DJANGO_SETTINGS_MODULE` is set
4. All tests should pass without circular import errors

The ultra-clean structure is now complete and functional! 🎉
