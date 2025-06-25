# Trust Management Project Structure

This document describes the organized structure of the Trust Management module.

## Directory Structure

```
trust_management/
├── docs/                              # Documentation
│   ├── README.md                      # Main project documentation
│   ├── TESTING_GUIDE.md              # Testing guidelines
│   ├── TRUST_MANAGEMENT_SECURITY_GUIDE.md
│   └── PROJECT_STRUCTURE.md          # This file
│
├── config/                            # Configuration files
│   ├── pytest.ini                    # pytest configuration
│   └── setup.cfg                     # Tool configurations
│
├── requirements/                      # Python dependencies
│   ├── base.txt                      # Base requirements
│   ├── development.txt               # Development dependencies
│   └── production.txt                # Production dependencies
│
├── scripts/                          # Shell scripts and utilities
│   ├── setup_dev_environment.sh     # Development setup
│   ├── run_tests.sh                 # Test runner with options
│   └── code_quality_check.sh        # Code quality checks
│
├── tests/                            # Test suite
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   ├── api/                         # API endpoint tests
│   └── utils/                       # Test utilities
│
├── coverage/                         # Coverage reports and config
│   ├── .coveragerc                  # Coverage configuration
│   ├── htmlcov/                     # HTML coverage reports (generated)
│   └── coverage.xml                 # XML coverage reports (generated)
│
├── logs/                            # Application logs
│   └── trust_management.log        # Main application log
│
├── cache/                           # Cache files
│   ├── __pycache__/                # Python bytecode cache
│   └── .pytest_cache/              # Pytest cache
│
├── reports/                         # Generated reports
│   ├── bandit_report.json          # Security analysis reports
│   └── safety_report.json          # Dependency security reports
│
├── trust_management_app/             # Main Django application
│   ├── core/                        # Core business logic
│   │   ├── models/                  # Database models
│   │   ├── services/                # Business services
│   │   └── validators/              # Input validation
│   │
│   ├── api/                         # REST API layer
│   │   ├── views/                   # API views and viewsets
│   │   ├── serializers/             # DRF serializers
│   │   └── permissions/             # API permissions
│   │
│   ├── utils/                       # Utility functions
│   ├── management/                  # Django management commands
│   ├── migrations/                  # Database migrations
│   ├── strategies/                  # Strategy pattern implementations
│   ├── observers/                   # Observer pattern implementations
│   ├── factories/                   # Factory pattern implementations
│   │
│   ├── admin.py                     # Django admin configuration
│   ├── apps.py                      # Django app configuration
│   ├── settings.py                  # Django settings
│   ├── urls.py                      # URL routing
│   └── signals.py                   # Django signals
│
├── tools/                           # Development tools
│   ├── debug_*.py                   # Debugging scripts
│   ├── test_*.py                    # Test utilities
│   └── run_tests*.py               # Legacy test runners
│
├── manage.py                        # Django management script
├── Makefile                         # Build automation
├── pyproject.toml                   # Python project configuration
└── .env                            # Environment variables
```

## Quick Start

### Development Setup
```bash
# Setup development environment
./scripts/setup_dev_environment.sh

# Run all tests
./scripts/run_tests.sh

# Run specific test types
./scripts/run_tests.sh --type unit --coverage

# Check code quality
./scripts/code_quality_check.sh
```

### Running Tests
```bash
# All tests
./scripts/run_tests.sh

# Unit tests only
./scripts/run_tests.sh --type unit

# With coverage
./scripts/run_tests.sh --coverage

# Verbose output
./scripts/run_tests.sh --verbose
```

## File Organization Principles

### Core Business Logic (`trust_management_app/core/`)
- **models/**: All database models and model-related functionality
- **services/**: Business logic services following domain-driven design
- **validators/**: Input validation and business rule validation

### API Layer (`trust_management_app/api/`)
- **views/**: REST API views, viewsets, and endpoints
- **serializers/**: Django REST Framework serializers
- **permissions/**: Custom permissions and access control

### Design Patterns (`trust_management_app/`)
- **strategies/**: Strategy pattern implementations for flexible algorithms
- **observers/**: Observer pattern for event handling
- **factories/**: Factory pattern for object creation

### Testing (`tests/`)
- **unit/**: Fast, isolated unit tests
- **integration/**: Integration tests for component interaction
- **api/**: API endpoint and functionality tests
- **utils/**: Test utilities and database verification

### Dependencies (`requirements/`)
- **base.txt**: Core runtime dependencies
- **development.txt**: Development and testing tools
- **production.txt**: Production-specific dependencies

## Benefits of This Structure

1. **Clear Separation of Concerns**: Each directory has a specific purpose
2. **Scalability**: Easy to add new components without cluttering
3. **Maintainability**: Related files are grouped together
4. **Testing**: Organized test structure makes it easy to run specific test types
5. **Development Workflow**: Scripts automate common development tasks
6. **Documentation**: Clear documentation structure for different audiences
