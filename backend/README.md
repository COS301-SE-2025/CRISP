# Backend

This directory contains the Django backend code for CRISP.

## Structure
```
backend/
├── manage.py
├── requirements.txt
├── your_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── your_apps/
```

The CI/CD will automatically:
- Install dependencies from requirements.txt
- Run Django tests
- Perform security scans
- Lint your Python code