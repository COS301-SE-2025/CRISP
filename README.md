# CRISP - Cyber Risk Information Sharing Platform

A comprehensive system for secure, privacy-preserving threat intelligence sharing between organizations using advanced anonymization strategies and STIX 2.1 standards.

## Project Structure

```
├── core/                           # Core anonymization patterns and strategies
│   ├── patterns/
│   │   └── strategy/              # Strategy pattern implementation
│   │       ├── __init__.py
│   │       ├── context.py         # Anonymization context
│   │       ├── demo.py           # Demonstration scripts
│   │       ├── enums.py          # Anonymization levels and data types
│   │       ├── exceptions.py     # Custom exceptions
│   │       ├── strategies.py     # Core anonymization strategies
│   │       └── utils.py          # Utility functions
│   └── tests/                     # Core component tests
│
├── crisp/                          # CRISP platform components
│   ├── crisp_threat_intel/        # Django application
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py             # Database models
│   │   ├── settings.py           # Django settings
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── wsgi.py
│   │   ├── celery.py             # Background task processing
│   │   ├── factories/            # STIX object factories
│   │   ├── management/           # Django management commands
│   │   ├── migrations/           # Database migrations
│   │   ├── observers/            # Feed monitoring
│   │   ├── services/             # External service integrations
│   │   ├── strategies/           # Anonymization strategies
│   │   │   ├── anonymization.py  # STIX-focused strategies
│   │   │   └── integrated_anonymization.py  # Unified strategy system
│   │   ├── taxii/               # TAXII server implementation
│   │   ├── tests/               # Django application tests
│   │   ├── utils.py
│   │   ├── validators/          # STIX validators
│   │   └── wsgi.py
│   ├── manage.py                 # Django management
│   ├── requirements.txt          # Python dependencies
│   └── scripts/                  # Utility scripts
│
├── main.py                       # Main integration demo
├── setup.py                     # Package setup
├── README.md                    # This file
└── .gitignore
```

## Features

### Core Anonymization System
- **Strategy Pattern Implementation**: Flexible, extensible anonymization strategies
- **Multi-Level Anonymization**: NONE, LOW, MEDIUM, HIGH, FULL levels
- **Data Type Support**: IP addresses, domains, emails, URLs
- **Consistent Hashing**: Deterministic anonymization for data consistency

### CRISP Platform
- **STIX 2.1 Compliance**: Full support for structured threat intelligence
- **Trust-Based Sharing**: Dynamic anonymization based on inter-organizational trust levels
- **TAXII 2.1 Server**: Standards-compliant threat intelligence sharing
- **Django Integration**: Web-based management interface
- **Celery Background Processing**: Scalable task processing
- **PostgreSQL Support**: Robust data persistence

### Integrated Anonymization
- **Unified Interface**: Single API for both raw data and STIX object anonymization
- **Trust Level Mapping**: Automatic conversion between trust levels and anonymization levels
- **Mixed Data Handling**: Process lists, individual objects, or raw strings
- **Factory Pattern**: Easy strategy creation and management

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ (required)
- Redis (for Celery in production)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd crisp-platform
```

2. Set up PostgreSQL database:
```bash
# Automated setup
./setup_postgresql.sh

# OR manual setup
sudo -u postgres createdb crisp
sudo -u postgres createuser -s admin
sudo -u postgres psql -c "ALTER USER admin PASSWORD 'AdminPassword';"
```

3. Start the development server:
```bash
# Automated startup (recommended)
./start_dev_server.sh

# OR manual startup
cd crisp
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Basic Usage

#### Core Anonymization
```python
from core.patterns.strategy.context import AnonymizationContext
from core.patterns.strategy.enums import AnonymizationLevel, DataType

# Initialize context
context = AnonymizationContext()

# Anonymize IP address
result = context.execute_anonymization(
    "192.168.1.100", 
    DataType.IP_ADDRESS, 
    AnonymizationLevel.MEDIUM
)
print(result)  # Output: "192.168.x.x"

# Auto-detect and anonymize
result = context.auto_detect_and_anonymize(
    "example.com", 
    AnonymizationLevel.HIGH
)
print(result)  # Output: "*.com"
```

#### CRISP Integration
```python
from crisp.crisp_threat_intel.strategies.integrated_anonymization import (
    IntegratedAnonymizationContext,
    anonymize_for_organization
)

# Initialize integrated context
context = IntegratedAnonymizationContext()

# Anonymize STIX object based on trust level
stix_indicator = {
    "type": "indicator",
    "pattern": "[domain-name:value = 'malicious.example.com']",
    "labels": ["malicious-activity"]
}

anonymized = context.anonymize_stix_object(stix_indicator, trust_level=0.3)
print(anonymized["pattern"])  # Anonymized based on low trust

# Anonymize for specific organization relationship
data = "sensitive-data@company.com"
result = anonymize_for_organization(data, "org1", "org2")
```

## Trust Level System

The platform uses a trust-based anonymization system:

- **High Trust (0.8+)**: No anonymization - full data sharing
- **Medium Trust (0.5-0.8)**: Low anonymization - partial data obfuscation
- **Low Trust (0.2-0.5)**: Medium anonymization - significant data masking
- **Untrusted (<0.2)**: Full anonymization - complete data protection

## Testing

Run the test suite:

```bash
# Core tests
python -m pytest core/tests/

# CRISP tests
cd crisp
python manage.py test

# Integration tests
python main.py
```

## Contributing

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation for any API changes
4. Ensure all tests pass before submitting

## Architecture

The system follows a modular architecture:

1. **Core Layer**: Reusable anonymization patterns and strategies
2. **CRISP Layer**: Django-based threat intelligence platform
3. **Integration Layer**: Unified interface bridging both systems

This design ensures:
- **Separation of Concerns**: Core anonymization logic is independent
- **Extensibility**: New strategies can be easily added
- **Reusability**: Core components can be used in other projects
- **Maintainability**: Clear boundaries between different system layers

## License

This project is licensed under the MIT License - see the LICENSE file for details.