# CRISP Trust Management Module

A comprehensive trust relationship and access control system for the CRISP (Cyber Risk Information Sharing Platform) threat intelligence sharing platform.

## Overview

The Trust Management module provides secure, configurable trust relationships between organizations in the CRISP ecosystem. It enables fine-grained access control, trust-based anonymization, and community-based intelligence sharing while maintaining comprehensive audit trails.

## Features

### Core Trust Management
- **Bilateral Trust Relationships**: Direct trust between two organizations
- **Community Trust Groups**: Trust networks for sector-based or purpose-driven sharing
- **Hierarchical Trust**: Parent-child organization relationships
- **Federation Trust**: Cross-federation trust relationships

### Access Control
- **Trust-based Access Levels**: none, read, subscribe, contribute, full
- **Dynamic Anonymization**: Trust-level based data anonymization strategies
- **Granular Permissions**: Role-based access control with organization context
- **Temporal Trust**: Time-bounded trust relationships with expiration

### Intelligence Sharing
- **Selective Sharing**: Share intelligence based on trust relationships
- **Anonymization Strategies**: Multiple levels of data anonymization
- **Sharing Policies**: Configurable policies for different trust levels
- **Access Logging**: Comprehensive audit trail of all access events

### Management & Monitoring
- **Trust Metrics**: Calculate and track trust scores over time
- **Activity Monitoring**: Monitor sharing patterns and relationship health
- **Security Alerts**: Detect suspicious trust-related activities
- **Audit Logs**: Complete audit trail of all trust operations

## Architecture

### Models
- **TrustLevel**: Configurable trust level definitions
- **TrustRelationship**: Trust relationships between organizations
- **TrustGroup**: Community-based trust groups
- **TrustGroupMembership**: Organization membership in trust groups
- **TrustLog**: Comprehensive audit logging
- **SharingPolicy**: Configurable sharing policies

### Services
- **TrustService**: Core trust relationship management
- **TrustGroupService**: Trust group and membership management
- **AccessControlStrategies**: Strategy pattern for access control
- **AnonymizationStrategies**: Strategy pattern for data anonymization

### Design Patterns
- **Strategy Pattern**: Flexible access control and anonymization
- **Observer Pattern**: Event notifications for trust changes
- **Factory Pattern**: Creation of trust objects and policies
- **Repository Pattern**: Data access abstraction

## Installation

### Prerequisites
- Python 3.9+
- Django 4.2+
- PostgreSQL 12+ (for production)

### Setup
```bash
# Clone or copy the trust-management module
cd trust-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Set up default trust configuration
python manage.py setup_trust --create-defaults
```

## Configuration

### Default Trust Levels
The module includes predefined trust levels:
- **No Trust** (0): No intelligence sharing
- **Basic Trust** (25): Limited sharing with full anonymization
- **Standard Trust** (50): Standard sharing with partial anonymization
- **High Trust** (75): Enhanced sharing with minimal anonymization
- **Complete Trust** (100): Full sharing with no anonymization

### Trust Groups
Create community groups for sector-based sharing:
```bash
# Create educational sector group
python manage.py manage_trust create-group \
    --name "Educational Institutions Network" \
    --description "Threat intelligence sharing for universities" \
    --creator-org <org-uuid> \
    --type sector \
    --public \
    --trust-level "Standard Trust"
```

## API Usage

### REST API Endpoints

#### Trust Relationships
```http
# Create trust relationship
POST /api/relationships/create_relationship/
{
    "target_organization": "uuid",
    "trust_level_name": "Standard Trust",
    "relationship_type": "bilateral",
    "notes": "Partnership agreement"
}

# Approve relationship
POST /api/relationships/approve_relationship/
{
    "relationship_id": "uuid"
}

# Check trust level
POST /api/relationships/check_trust/
{
    "target_organization": "uuid"
}

# Test intelligence access
POST /api/relationships/test_intelligence_access/
{
    "intelligence_owner": "uuid",
    "required_access_level": "read",
    "resource_type": "indicator"
}
```

#### Trust Groups
```http
# Create trust group
POST /api/groups/create_group/
{
    "name": "Cybersecurity Consortium",
    "description": "Regional cybersecurity sharing group",
    "group_type": "geography",
    "is_public": true,
    "default_trust_level_name": "Standard Trust"
}

# Join group
POST /api/groups/join_group/
{
    "group_id": "uuid",
    "membership_type": "member"
}

# Get group members
GET /api/groups/{group_id}/members/

# Get group statistics
GET /api/groups/{group_id}/statistics/
```

### Python API

```python
from TrustManagement.services.trust_service import TrustService
from TrustManagement.services.trust_group_service import TrustGroupService

# Create trust relationship
relationship = TrustService.create_trust_relationship(
    source_org="org-uuid-1",
    target_org="org-uuid-2",
    trust_level_name="Standard Trust",
    relationship_type="bilateral",
    created_by="user-id"
)

# Check trust level
trust_info = TrustService.check_trust_level("org-uuid-1", "org-uuid-2")
if trust_info:
    trust_level, relationship = trust_info
    print(f"Trust level: {trust_level.name}")

# Test intelligence access
can_access, reason, rel = TrustService.can_access_intelligence(
    requesting_org="org-uuid-1",
    intelligence_owner="org-uuid-2",
    required_access_level="read"
)

# Create trust group
group = TrustGroupService.create_trust_group(
    name="Research Collaboration",
    description="Academic research sharing",
    creator_org="org-uuid-1",
    is_public=True
)
```

## Management Commands

### Setup Commands
```bash
# Initialize trust configuration
python manage.py setup_trust --create-defaults --create-sample-groups

# Reset trust configuration (WARNING: destructive)
python manage.py setup_trust --reset
```

### Trust Management Commands
```bash
# Create trust relationship
python manage.py manage_trust create-relationship \
    --source-org <uuid> \
    --target-org <uuid> \
    --trust-level "Standard Trust" \
    --notes "Partnership agreement"

# Approve relationship
python manage.py manage_trust approve-relationship \
    --relationship-id <uuid> \
    --approving-org <uuid>

# Create trust group
python manage.py manage_trust create-group \
    --name "Security Consortium" \
    --description "Regional security sharing" \
    --creator-org <uuid> \
    --public

# List relationships
python manage.py manage_trust list-relationships --organization <uuid>

# Check trust between organizations
python manage.py manage_trust check-trust \
    --source-org <uuid> \
    --target-org <uuid>
```

### Audit Commands
```bash
# Generate audit report
python manage.py audit_trust --report-type summary

# Security analysis
python manage.py audit_trust --report-type security --days 30

# Activity analysis
python manage.py audit_trust --report-type activity --days 7

# Save report to file
python manage.py audit_trust --report-type all --save-to-file audit_report.json
```

## Security Considerations

### Access Control
- All trust operations require proper authentication and authorization
- Organization-scoped permissions ensure users can only manage their own relationships
- Role-based access control with multiple permission levels
- Comprehensive audit logging of all trust operations

### Data Protection
- Trust-based anonymization protects sensitive intelligence data
- Configurable anonymization strategies based on trust levels
- Temporal access controls with relationship expiration
- Secure handling of organization identifiers

### Monitoring
- Real-time monitoring of trust relationship changes
- Automated detection of suspicious access patterns
- Comprehensive audit trails for compliance
- Configurable alerting for security events

## Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test modules
python manage.py test TrustManagement.tests.test_trust_models
python manage.py test TrustManagement.tests.test_trust_services
python manage.py test TrustManagement.tests.test_access_control

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Categories
- **Model Tests**: Validation, constraints, and business logic
- **Service Tests**: Core business logic and operations
- **Access Control Tests**: Permission and strategy testing
- **Integration Tests**: End-to-end workflow testing
- **API Tests**: REST API endpoint testing

## Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Set up pre-commit hooks
pip install pre-commit
pre-commit install

# Run code quality checks
flake8 TrustManagement/
black TrustManagement/
isort TrustManagement/
mypy TrustManagement/
```

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 90%
- Follow Django best practices

## Documentation

### API Documentation
- REST API documentation available via Django REST Framework browsable API
- Comprehensive docstrings for all classes and methods
- Type hints for improved IDE support

### Architecture Documentation
- Domain model documentation in CRISP platform docs
- Design pattern implementation notes
- Security architecture documentation

## License

This module is part of the CRISP platform and follows the same licensing terms.

## Support

For support and questions:
- Review the test suite for usage examples
- Check the management commands for operational procedures
- Consult the CRISP platform documentation for integration details