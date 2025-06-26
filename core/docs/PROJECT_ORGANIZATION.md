# CRISP Project Organization

## 🎯 Ultra-Clean Project Structure

This project follows a clean, organized structure with all files properly contained within the `core/` or `crisp/` directories.

### 📁 Directory Structure

```
CRISP/
├── .git/              # Git version control
├── .venv/             # Python virtual environment  
├── .claude/           # Claude AI workspace files
├── backup/            # Archived components
├── core/              # 🎯 ALL APPLICATION CODE
│   ├── api/           # REST API endpoints
│   ├── docs/          # Documentation files
│   ├── factories/     # Test data factories
│   ├── models/        # Django models
│   ├── observers/     # Observer pattern implementations
│   ├── parsers/       # Data parsers (STIX, etc.)
│   ├── patterns/      # Design patterns
│   ├── repositories/  # Data access layer
│   ├── scripts/       # Utility scripts
│   ├── services/      # Business logic services
│   ├── strategies/    # Strategy pattern implementations
│   ├── taxii/         # TAXII protocol support
│   ├── templates/     # Django templates
│   ├── tests/         # All test files
│   ├── views/         # Django views
│   └── *.py          # Core Django modules
└── crisp/             # 🎯 DJANGO PROJECT CONFIG ONLY
    ├── settings.py    # Django settings
    ├── urls.py        # URL configuration
    ├── wsgi.py        # WSGI application
    └── *.py          # Other Django project files
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
