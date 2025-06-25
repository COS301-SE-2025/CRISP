# Backend

This directory contains the Django backend code for CRISP.

## Getting Started

1. Place your Django project files here
2. Include `manage.py` in this directory
3. Add your `requirements.txt` for dependencies
4. The CI/CD pipeline will automatically detect and test your code

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