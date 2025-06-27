# CRISP Project Organization

## 🎯 Ultra-Clean Project Structure

This project follows a clean, organized structure with all files properly contained within the `core/` or `crisp/` directories.

### 📁 Directory Structure

```
CRISP/
├── .git/              # Git version control
├── .venv/             # Python virtual environment  
├── backup/            # Archived components
├── README.md          # Main project documentation
├── core/              # 🎯 ALL APPLICATION CODE
│   ├── manage.py      # Django management script
│   ├── models.py      # Main models registration
│   ├── admin.py       # Django admin configuration
│   ├── serializers.py # API serializers
│   ├── api/           # REST API endpoints
│   │   ├── trust_api/ # Trust management API
│   │   ├── serializers/ # API serializers
│   │   └── views/     # API views
│   ├── docs/          # Documentation files
│   ├── factories/     # Test data factories
│   ├── management/    # Django management commands
│   ├── models/        # Organized Django models
│   │   ├── auth.py    # Authentication models
│   │   ├── stix_object.py # STIX models
│   │   ├── trust_models/ # Trust management models
│   │   ├── indicator.py # Indicator models
│   │   ├── institution.py # Institution models
│   │   ├── threat_feed.py # Threat feed models
│   │   └── ttp_data.py # TTP data models
│   ├── observers/     # Observer pattern implementations
│   ├── parsers/       # Data parsers (STIX, etc.)
│   ├── patterns/      # Design patterns
│   │   ├── decorator/ # Decorator pattern (STIX decorators)
│   │   ├── factory/   # Factory pattern (STIX creators)
│   │   └── observer/  # Observer pattern (threat feed)
│   ├── repositories/  # Data access layer
│   ├── requirements/  # Python dependencies
│   ├── scripts/       # Utility scripts
│   ├── serializers/   # Additional serializers
│   ├── services/      # Business logic services
│   ├── strategies/    # Strategy pattern implementations
│   │   ├── enums.py   # Strategy enums
│   │   ├── anonymization.py # Anonymization strategies
│   │   └── authentication_strategies.py # Auth strategies
│   ├── taxii/         # TAXII protocol support
│   ├── templates/     # Django templates
│   ├── tests/         # All test files
│   ├── urls/          # URL configurations  
│   ├── user_management/ # User management components
│   └── views/         # Django views
│       ├── auth_views.py # Authentication views
│       ├── admin_views.py # Admin views
│       └── api/       # API views
└── crisp/             # 🎯 DJANGO PROJECT CONFIG ONLY
    ├── settings.py    # Django settings
    ├── test_settings.py # Test environment settings
    ├── urls.py        # URL configuration
    ├── wsgi.py        # WSGI application
    ├── asgi.py        # ASGI application
    └── celery.py      # Celery configuration
```

## ✅ Organization Principles

1. **No loose files in root** - All code files are organized in subdirectories
2. **Logical separation** - Application code in `core/`, project config in `crisp/`
3. **Proper Python packages** - All directories have `__init__.py` files
4. **Clean structure** - Easy to navigate and maintain

## 🔍 Verification

To verify the organization is maintained:

```bash
# Run structure verification
python3 core/scripts/final_verification.py

# Run detailed structure check
python3 core/scripts/verify_structure.py
```

## 🚀 Benefits

- **Easy navigation** - Developers can quickly find relevant code
- **Maintainable** - Clear separation of concerns
- **Scalable** - Structure supports project growth
- **Professional** - Follows Django and Python best practices

This organization ensures the project remains clean, professional, and easy to work with as it grows.
