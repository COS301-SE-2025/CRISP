# 🛡️ CRISP Strategy Pattern Integration Guide

## 🎯 Overview

This guide shows how to run and use the integrated CRISP threat intelligence platform with strategy pattern anonymization.

## 🚀 Quick Start

### Option 1: Run Standalone Demo

```bash
cd /mnt/c/Users/Liamv/Documents/GitHub/CRISP
python3 run_integration_demo.py
```

This shows the integration concepts and anonymization examples.

### Option 2: Run Integration Tests

```bash
python3 test_integration.py
```

This validates that the core integration functionality works.

### Option 3: Run Original Anonymization Demo

```bash
python3 main.py demo
```

This runs the original CRISP anonymization system demo.

## 📋 Full Django Setup (For Production Use)

If you want to run the full Django application with database integration:

### 1. Install Dependencies

```bash
cd crisp_threat_intel
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# Run migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Setup initial data
python3 manage.py setup_crisp
```

### 3. Run Django Server

```bash
python3 manage.py runserver
```

### 4. Run Django Integration Tests

```bash
python3 manage.py test crisp_threat_intel.tests.test_integrated_anonymization
```

## 🔧 Integration Features

### ✅ What's Integrated:

1. **Unified Strategy Pattern** - Bridges both anonymization systems
2. **Trust-Based Processing** - Maps organization trust to anonymization levels
3. **STIX + Raw Data Support** - Handles both STIX objects and raw indicators
4. **TAXII API Integration** - Trust-aware endpoint anonymization
5. **Database Models** - TrustRelationship model for org trust management
6. **Comprehensive Testing** - Full test suite validating integration

### 🎯 Key Components:

- `IntegratedAnonymizationContext` - Main interface for unified anonymization
- `TrustRelationship` model - Manages trust between organizations
- Enhanced `Collection.generate_bundle()` - Trust-aware bundle generation
- Updated TAXII endpoints - Automatic anonymization based on requesting org
- `STIXObject.apply_anonymization()` - Direct STIX object anonymization

## 💡 Usage Examples

### Basic Integration Usage:

```python
from crisp_threat_intel.strategies.integrated_anonymization import IntegratedAnonymizationContext

# Initialize context
context = IntegratedAnonymizationContext()

# Anonymize STIX object based on trust
stix_indicator = {...}  # Your STIX indicator
anonymized = context.anonymize_stix_object(stix_indicator, trust_level=0.5)

# Anonymize raw data
anonymized_domain = context.anonymize_raw_data("evil.com", DataType.DOMAIN, AnonymizationLevel.MEDIUM)

# Mixed data anonymization
mixed_data = [stix_indicator, "192.168.1.1", "phishing@bad.com"]
results = context.anonymize_mixed(mixed_data, trust_level=0.3)
```

### Django Model Usage:

```python
from crisp_threat_intel.models import Organization, Collection, TrustRelationship

# Create trust relationship
trust = TrustRelationship.objects.create(
    source_organization=org1,
    target_organization=org2,
    trust_level=0.6  # Medium trust
)

# Generate anonymized bundle for organization
collection = Collection.objects.get(id=collection_id)
bundle = collection.generate_bundle(requesting_organization=org2)
# Automatically applies anonymization based on trust relationship
```

### TAXII API Usage:

```bash
# Access collection objects (automatically anonymized based on requesting org)
curl -X GET "http://localhost:8000/taxii2/collections/{collection_id}/objects/" \
     -H "Accept: application/stix+json;version=2.1" \
     -u "username:password"
```

## 🎯 Trust Level Mapping

| Trust Level | Scenario | Anonymization Level | Description |
|-------------|----------|-------------------|-------------|
| 0.8+ | Trusted Partner | None | No anonymization applied |
| 0.5-0.8 | Known Partner | Low | Minimal anonymization |
| 0.2-0.5 | Occasional Collaborator | Medium | Moderate anonymization |
| <0.2 | Unknown/Untrusted | Full | Complete anonymization |

## 📊 Anonymization Examples

### Domain Anonymization:
- **Original**: `malicious.example.com`
- **Low**: `*.example.com`
- **Medium**: `*.com`
- **High**: `*.commercial`
- **Full**: `anon-domain-a1b2c3d4.example`

### IP Anonymization:
- **Original**: `192.168.1.100`
- **Low**: `192.168.1.x`
- **Medium**: `192.168.x.x`
- **High**: `192.x.x.x`
- **Full**: `anon-ipv4-d984a05f`

### STIX Pattern Anonymization:
- **Original**: `[domain-name:value = 'malicious.example.com']`
- **Medium Trust**: `[domain-name:value = '[REDACTED].example.com']`
- **Low Trust**: `[domain-name:value = 'anon-domain-a1b2c3d4.example']`

## 🧪 Testing

### Run All Tests:

```bash
# Integration tests (standalone)
python3 test_integration.py

# Original anonymization tests
python3 core/tests/test_strategies.py

# Django integration tests (requires Django setup)
python3 manage.py test crisp_threat_intel.tests.test_integrated_anonymization

# Full system tests (if Django is set up)
python3 run_tests.py --all
```

### Test Coverage:

- ✅ Strategy pattern implementation
- ✅ Trust level mapping
- ✅ STIX object anonymization
- ✅ Raw data anonymization
- ✅ Mixed data processing
- ✅ Bundle anonymization
- ✅ Django model integration
- ✅ TAXII endpoint integration

## 🔍 Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure you're in the correct directory and paths are set up
2. **Django Not Found**: Install Django with `pip install django`
3. **Missing Dependencies**: Run `pip install -r requirements.txt`
4. **Database Errors**: Run migrations with `python3 manage.py migrate`

### Debug Mode:

Add this to enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance

The integrated system is optimized for:
- ✅ Bulk anonymization operations
- ✅ Real-time TAXII endpoint processing
- ✅ Large STIX bundle handling
- ✅ Minimal memory overhead
- ✅ Concurrent organization access

## 🚀 Production Deployment

For production use:

1. **Set up Django properly** with PostgreSQL database
2. **Configure trust relationships** between organizations
3. **Set up proper authentication** for TAXII endpoints
4. **Monitor performance** and adjust trust levels as needed
5. **Regular testing** of anonymization effectiveness

## 📚 Additional Resources

- **Original CRISP Anonymization**: See `core/patterns/strategy/` directory
- **STIX 2.1 Specification**: [OASIS STIX 2.1](https://oasis-open.github.io/cti-documentation/)
- **TAXII 2.1 Specification**: [OASIS TAXII 2.1](https://oasis-open.github.io/cti-documentation/)
- **Strategy Pattern**: [Design Patterns Documentation](https://refactoring.guru/design-patterns/strategy)

## ✅ Success Criteria

The integration is successful when:
- ✅ All demos run without errors
- ✅ Integration tests pass
- ✅ STIX objects are properly anonymized
- ✅ Trust relationships control anonymization levels
- ✅ TAXII endpoints serve anonymized content
- ✅ Raw data and STIX data work together seamlessly

**🎉 Integration Complete! The CRISP platform now provides unified, trust-based anonymization for comprehensive threat intelligence sharing.**