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
python3 setup_and_test.py
```

## 🧪 Individual Component Testing

### Test Core Models
```bash
python3 -c "
import sys
sys.path.append('core')
import models
print('✅ Organization:', models.Organization.__name__)
print('✅ CustomUser:', models.CustomUser.__name__)
print('✅ UserSession:', models.UserSession.__name__)
print('🎯 Core models working!')
"
```

### Test STIX Models
```bash
python3 -c "
import sys
sys.path.append('.')
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
import sys
sys.path.append('.')
from core.models.trust_models.models import TrustLevel, TrustRelationship
print('✅ TrustLevel:', TrustLevel.__name__)
print('✅ TrustRelationship:', TrustRelationship.__name__)
print('🎯 Trust models working!')
"
```

### Test Design Patterns
```bash
python3 -c "
import sys
sys.path.append('.')
from core.patterns.strategy.enums import AnonymizationLevel
from core.patterns.observer.threat_feed import ThreatFeed
print('✅ AnonymizationLevel:', AnonymizationLevel.__name__)
print('✅ ThreatFeed:', ThreatFeed.__name__)
print('🎯 Patterns working!')
"
```

### Test Other Models
```bash
python3 -c "
import sys
sys.path.append('.')
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
├── models.py                    # Main models (Organization, CustomUser, etc.)
├── admin.py                     # Django admin configuration
├── views.py                     # Main views
├── serializers.py               # API serializers
├── models/                      # Model packages
│   ├── __init__.py             # Clean exports (no circular imports)
│   ├── stix_object.py          # STIX-related models
│   ├── indicator.py            # Indicator models
│   ├── institution.py          # Institution models
│   ├── ttp_data.py            # TTP data models
│   └── trust_models/
│       └── models.py           # Trust management models
├── patterns/                    # Design patterns
│   ├── strategy/
│   ├── observer/
│   ├── factory/
│   └── decorator/
├── api/                        # API endpoints
├── tests/                      # Test files
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
python3 setup_and_test.py

# 3. Verify imports work
python3 -c "
import sys
sys.path.append('core')
sys.path.append('.')

# Test main models
import models
print('Main models:', [attr for attr in dir(models) if not attr.startswith('_')])

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
