# Trust Management Module

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com)

A comprehensive trust relationship and access control system for the CRISP (Cyber Risk Information Sharing Platform) threat intelligence sharing platform.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (for production)
- Git

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd trust_management

# Setup development environment (creates venv, installs deps, runs migrations)
./scripts/setup_dev_environment.sh

# Activate virtual environment
source venv/bin/activate

# Start development server
python manage.py runserver
```

### Running Tests
```bash
# Run all tests
./scripts/run_tests.sh

# Run with coverage
./scripts/run_tests.sh --coverage

# Run specific test types
./scripts/run_tests.sh --type unit        # Unit tests only
./scripts/run_tests.sh --type integration # Integration tests only
./scripts/run_tests.sh --type api         # API tests only
```

## 📁 Project Structure

```
trust_management/
├── 📄 docs/                    # Documentation
├── ⚙️  config/                 # Configuration files  
├── 📦 requirements/            # Python dependencies
├── 🔧 scripts/                 # Development scripts
├── 🧪 tests/                   # Organized test suite
├── 🏗️  trust_management_app/   # Main Django application
│   ├── 🎯 core/               # Business logic (models, services, validators)
│   ├── 🌐 api/                # REST API layer (views, serializers, permissions)
│   ├── 🔄 strategies/         # Strategy pattern implementations
│   ├── 👁️  observers/          # Observer pattern implementations
│   └── 🏭 factories/          # Factory pattern implementations
└── 🛠️  tools/                  # Development and debugging tools
```

For detailed structure documentation, see [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md).

## 🌟 Features

### Core Trust Management
- **Bilateral Trust Relationships**: Direct trust between organizations
- **Community Trust Groups**: Sector-based or purpose-driven sharing networks
- **Hierarchical Trust**: Parent-child organization relationships
- **Federation Trust**: Cross-federation trust relationships

### Access Control & Security
- **Trust-based Access Levels**: Granular access control (none → read → subscribe → contribute → full)
- **Dynamic Anonymization**: Trust-level based data anonymization
- **Temporal Trust**: Time-bounded relationships with expiration
- **Comprehensive Audit**: Complete audit trail of all operations

## 📚 Documentation

- **[Main Documentation](docs/README.md)**: Complete feature documentation
- **[Testing Guide](docs/TESTING_GUIDE.md)**: Testing strategies and guidelines
- **[Security Guide](docs/TRUST_MANAGEMENT_SECURITY_GUIDE.md)**: Security considerations
- **[Project Structure](docs/PROJECT_STRUCTURE.md)**: Detailed structure explanation

## 🔧 Development

### Code Quality
```bash
# Run code quality checks
./scripts/code_quality_check.sh

# Format code
black trust_management_app/ tests/
isort trust_management_app/ tests/

# Type checking
mypy trust_management_app/
```

### Dependencies
- **Base**: Core runtime dependencies ([requirements/base.txt](requirements/base.txt))
- **Development**: Testing and development tools ([requirements/development.txt](requirements/development.txt))
- **Production**: Production-specific dependencies ([requirements/production.txt](requirements/production.txt))

## 🚦 API Usage

### Quick API Examples
```python
from trust_management_app.core.services.trust_service import TrustService

# Create trust relationship
relationship = TrustService.create_trust_relationship(
    source_org="org-uuid-1",
    target_org="org-uuid-2",
    trust_level_name="Standard Trust"
)

# Check trust level
trust_info = TrustService.check_trust_level("org-uuid-1", "org-uuid-2")
```

For complete API documentation, see [docs/README.md](docs/README.md).

## 🧪 Testing Strategy

- **Unit Tests** (`tests/unit/`): Fast, isolated component testing
- **Integration Tests** (`tests/integration/`): Component interaction testing  
- **API Tests** (`tests/api/`): REST endpoint testing
- **Utilities** (`tests/utils/`): Test helpers and database verification

Target: **90%+ test coverage**

## 🤝 Contributing

1. **Setup**: Use `./scripts/setup_dev_environment.sh`
2. **Code Style**: Follow PEP 8, use type hints, write docstrings
3. **Testing**: Maintain 90%+ coverage, write tests for new features
4. **Quality**: Run `./scripts/code_quality_check.sh` before committing

## 📄 License

This module is part of the CRISP platform and follows the same licensing terms.

## 🆘 Support

- **Examples**: Review the test suite for usage examples
- **Commands**: Check management commands for operational procedures  
- **Integration**: Consult CRISP platform documentation for integration details

---

**Built with ❤️ for secure threat intelligence sharing**
