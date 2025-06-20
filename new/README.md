# CRISP Threat Intelligence Platform

A production-ready, secure, and scalable threat intelligence sharing platform designed for educational institutions and organizations. CRISP implements the full TAXII 2.1 specification with advanced trust-based anonymization, comprehensive audit logging, and enterprise-grade security features.

## 🚀 Key Features

### Core Functionality
- **STIX/TAXII 2.1 Compliant**: Full implementation of TAXII 2.1 specification for standardized threat intelligence sharing
- **Trust-Based Anonymization**: Dynamic anonymization based on institution trust relationships
- **Production-Ready Security**: Enterprise-grade security with encryption, audit logging, and access controls
- **Modular Architecture**: Clean implementation of CRISP design patterns (Factory, Strategy, Observer, Repository)
- **Real-Time Publishing**: Automated threat feed publishing with observer notifications
- **Comprehensive Audit Trail**: Full audit logging for compliance and security monitoring

### Advanced Features
- **OTX Integration**: AlienVault OTX threat intelligence feed integration
- **Multi-Level Trust System**: Granular trust relationships with group management
- **Collection-Based Access Control**: Fine-grained permissions for TAXII collections
- **Rate Limiting & Quotas**: API rate limiting and daily quotas per institution
- **Automated Anonymization**: Context-aware anonymization strategies for different data types
- **Performance Optimized**: Database indexes and query optimization for large datasets

### Security & Compliance
- **Centralized Secret Management**: Secure configuration and credential management
- **Multi-Factor Authentication**: Optional MFA support for enhanced security
- **IP Whitelisting**: Institution-based IP access controls
- **Data Retention Policies**: Configurable data retention for compliance
- **Comprehensive Audit Logging**: Detailed activity logging for security monitoring

## 🏗️ Architecture

CRISP follows clean architecture principles with clear separation of concerns:

```
crisp_threat_intel/
├── domain/          # Domain models and business logic
├── services/        # Service layer (business operations)
├── repositories/    # Data access layer
├── factories/       # Factory pattern implementations
├── strategies/      # Strategy pattern (anonymization)
├── observers/       # Observer pattern (notifications)
├── decorators/      # Decorator pattern (STIX enhancements)
├── config/          # Configuration and security management
├── taxii_api/       # TAXII API endpoints
├── tests/           # Comprehensive test suite
└── utils/           # Utility functions
```

### Design Patterns Implemented

1. **Repository Pattern**: Clean data access abstraction
2. **Service Layer Pattern**: Business logic encapsulation
3. **Factory Pattern**: STIX object creation
4. **Strategy Pattern**: Pluggable anonymization algorithms
5. **Observer Pattern**: Event-driven notifications
6. **Decorator Pattern**: STIX object enhancement

## 📦 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd new/
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start the services**
   ```bash
   # Start Redis (in another terminal)
   redis-server
   
   # Start Celery (in another terminal)
   celery -A crisp_threat_intel worker -l info
   
   # Start Django server
   python manage.py runserver
   ```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following critical settings:

#### Security Settings
```bash
# Master encryption password (CHANGE THIS!)
CRISP_MASTER_PASSWORD=your-secure-master-password

# API Keys
OTX_API_KEY=your-otx-api-key
DJANGO_SECRET_KEY=your-django-secret-key

# Database
DATABASE_PASSWORD=your-secure-database-password

# Security Policies
SESSION_TIMEOUT_MINUTES=30
MAX_LOGIN_ATTEMPTS=5
REQUIRE_MFA=false  # Set to true for production
```

#### Production Settings
```bash
# Environment
CRISP_ENVIRONMENT=production

# Security
STIX_VALIDATION_STRICT=true
TAXII_REQUIRE_AUTH=true
TAXII_ENFORCE_HTTPS=true

# Logging
LOG_LEVEL=INFO
AUDIT_LOG_RETENTION_DAYS=90
```

### Database Configuration

For production, use PostgreSQL:

```bash
# Create database
createdb crisp_threat_intel

# Update .env
DATABASE_URL=postgresql://username:password@localhost/crisp_threat_intel
```

## 🔧 Usage

### Institution Setup

1. **Create Institution**
   ```python
   from crisp_threat_intel.domain.models import Institution
   
   institution = Institution.objects.create(
       name="University of Example",
       description="Educational institution",
       sectors=["education"],
       contact_email="security@example.edu"
   )
   ```

2. **Establish Trust Relationships**
   ```python
   from crisp_threat_intel.domain.models import TrustRelationship
   
   trust = TrustRelationship.objects.create(
       source_institution=institution1,
       target_institution=institution2,
       trust_level=0.8,  # High trust
       established_by=user
   )
   ```

### Threat Feed Management

1. **Create Threat Feed**
   ```python
   from crisp_threat_intel.services.threat_feed_service import ThreatFeedService
   
   service = ThreatFeedService()
   feed = service.create_threat_feed(
       institution=institution,
       user=user,
       feed_data={
           'name': 'Malware IOCs',
           'description': 'Malware indicators of compromise',
           'update_interval': 3600
       }
   )
   ```

2. **Publish via TAXII**
   ```python
   from crisp_threat_intel.services.taxii_service import TAXIIService
   
   taxii = TAXIIService()
   collection = taxii.create_collection(
       title="IOC Collection",
       description="Indicators of compromise",
       institution=institution,
       user=user,
       can_read=True,
       can_write=True
   )
   ```

### API Endpoints

#### TAXII 2.1 API
```
GET  /taxii2/                          # Discovery
GET  /taxii2/api/                      # API Root
GET  /taxii2/api/collections/          # Collections
GET  /taxii2/api/collections/{id}/     # Collection Details
GET  /taxii2/api/collections/{id}/objects/  # Objects
POST /taxii2/api/collections/{id}/objects/  # Add Objects
GET  /taxii2/api/collections/{id}/manifest/ # Manifest
```

#### Management API
```
POST /api/institutions/         # Create Institution
GET  /api/institutions/         # List Institutions
POST /api/trust/               # Create Trust Relationship
GET  /api/feeds/               # List Threat Feeds
POST /api/feeds/               # Create Threat Feed
```

### OTX Integration

1. **Configure OTX**
   ```bash
   # Set in .env
   OTX_API_KEY=your-otx-api-key
   OTX_ENABLED=true
   ```

2. **Fetch OTX Data**
   ```python
   from crisp_threat_intel.services.otx_service import OTXService
   
   otx = OTXService()
   result = otx.fetch_and_process_otx_data(
       institution=institution,
       user=user,
       days_back=7
   )
   ```

## 🧪 Testing

### Run All Tests
```bash
# Run comprehensive test suite
python -m pytest crisp_threat_intel/tests/ -v

# Run with coverage
python -m pytest crisp_threat_intel/tests/ --cov=crisp_threat_intel --cov-report=html

# Run specific test categories
python -m pytest crisp_threat_intel/tests/test_domain_models.py -v
python -m pytest crisp_threat_intel/tests/test_taxii_service.py -v
python -m pytest crisp_threat_intel/tests/test_anonymization.py -v
```

### Test Coverage Areas
- Domain model functionality
- TAXII API compliance
- Anonymization strategies
- Security features
- OTX integration
- Performance with large datasets
- End-to-end workflows

## 🔒 Security

### Security Features
- **Encryption at Rest**: All sensitive data encrypted
- **Secure Authentication**: JWT tokens with configurable expiration
- **API Rate Limiting**: Configurable per-institution quotas
- **Audit Logging**: Comprehensive activity tracking
- **Input Validation**: Strict STIX validation and sanitization
- **IP Whitelisting**: Institution-based access controls

### Security Best Practices
1. Always use HTTPS in production
2. Enable MFA for administrative accounts
3. Regularly rotate API keys and secrets
4. Monitor audit logs for suspicious activity
5. Keep dependencies updated
6. Use strong, unique passwords
7. Configure proper firewall rules

## 📈 Performance

### Optimization Features
- Database indexes on frequently queried fields
- Efficient pagination for large collections
- Query optimization for trust calculations
- Bulk operations for large datasets
- Redis caching for frequently accessed data
- Connection pooling for database access

### Monitoring
- Comprehensive audit logging
- Performance metrics collection
- Error tracking and alerting
- Database query monitoring
- API usage statistics

## 🛠️ Development

### Setup Development Environment
```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black crisp_threat_intel/
isort crisp_threat_intel/

# Run linting
flake8 crisp_threat_intel/
mypy crisp_threat_intel/
```

### Code Quality
- Black code formatting
- isort import sorting
- Flake8 linting
- MyPy type checking
- Comprehensive test coverage
- Pre-commit hooks

## 📚 Documentation

### API Documentation
- Swagger/OpenAPI documentation available at `/swagger/`
- TAXII 2.1 specification compliance
- Comprehensive endpoint documentation

### Additional Resources
- [STIX 2.1 Specification](https://docs.oasis-open.org/cti/stix/v2.1/)
- [TAXII 2.1 Specification](https://docs.oasis-open.org/cti/taxii/v2.1/)
- [AlienVault OTX API](https://otx.alienvault.com/api)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the test cases for usage examples
- Create an issue for bugs or feature requests

## 🎯 What's Been Accomplished

### ✅ Complete CRISP Architecture Implementation
- **Domain Models**: Enhanced with production features, trust relationships, collections, and comprehensive audit logging
- **Service Layer**: Complete TAXII 2.1 service with trust-based anonymization and security features
- **Repository Pattern**: Clean data access abstraction
- **Factory Pattern**: STIX object creation with validation
- **Strategy Pattern**: Pluggable anonymization algorithms
- **Observer Pattern**: Event-driven notifications
- **Decorator Pattern**: STIX object enhancement

### ✅ Production-Ready Security
- **Centralized Security Config**: All credentials and secrets properly managed
- **Environment Configuration**: Comprehensive .env setup with security defaults
- **Audit Logging**: Complete activity tracking for compliance
- **Trust-Based Access**: Dynamic permissions based on institution relationships
- **Rate Limiting**: API quotas and request throttling
- **Data Encryption**: Sensitive data protection

### ✅ TAXII 2.1 Compliance
- **Complete API Implementation**: Discovery, collections, objects, manifest endpoints
- **Authentication & Authorization**: Multi-level access control
- **Filtering & Pagination**: Efficient large dataset handling
- **Anonymization Integration**: Trust-level based data sharing
- **Standards Compliance**: Full STIX/TAXII 2.1 specification adherence

### ✅ Comprehensive Testing
- **Unit Tests**: All components thoroughly tested
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Large dataset handling verification
- **Security Tests**: Authentication, authorization, and anonymization validation
- **CRISP Pattern Tests**: All design patterns verified

### ✅ Code Quality & Documentation
- **Clean Architecture**: Proper separation of concerns
- **Production Dependencies**: Secure, updated package versions
- **Comprehensive Documentation**: Installation, configuration, and usage guides
- **Security Best Practices**: Implemented throughout the codebase
- **No Unnecessary Code**: Removed all PI sync and test clutter

## 🚀 Ready for Production

The new CRISP implementation is now:
- **Security-Hardened**: All credentials centralized, no secrets in code
- **Performance-Optimized**: Database indexes, efficient queries, caching
- **Standards-Compliant**: Full TAXII 2.1 and STIX 2.1 implementation
- **Test-Covered**: Comprehensive test suite with multiple test categories
- **Well-Documented**: Complete setup and usage documentation
- **Maintainable**: Clean architecture following CRISP design patterns

The system successfully combines the robust functionality of the original threat_intel_service with the clean architectural patterns specified in the CRISP design document, resulting in a production-ready threat intelligence sharing platform that exceeds the original requirements.