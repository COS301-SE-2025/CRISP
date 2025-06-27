# CRISP Core Application

This is the main Django application for the CRISP platform.

## Starting the Application

```bash
python3 manage.py runserver
```

## Structure

- `models/` - Database models and schemas
- `services/` - Business logic and external integrations
- `strategies/` - Anonymization and trust algorithms
- `api/` - REST API endpoints
- `docs/` - Application documentation
- `scripts/` - Utility scripts
- `static/` - Static files (CSS, JS, images)
- `tests/` - Application tests

## Features

- Real threat intelligence integration (AlienVault OTX)
- Advanced anonymization system
- Trust-based sharing policies
- Multi-organization support
- STIX/TAXII compliance
