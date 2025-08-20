# CRISP Capstone-Unified Setup Guide

## Prerequisites
- PostgreSQL installed and running
- Python 3.10+
- pip3

## Database Setup

1. **Set PostgreSQL password**
```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'AdminPass123!';"
```

2. **Create database**
```bash
sudo -u postgres psql -c "CREATE DATABASE crisp_trust_db;"
```

3. **Test connection**
```bash
PGPASSWORD='AdminPass123!' psql -h localhost -U postgres -d crisp_trust_db -c "SELECT version();"
```

## Django Setup

4. **Install dependencies**
```bash
pip3 install -r requirements.txt
```

5. **Run migrations**
```bash
python3 manage.py migrate
```

6. **Create superuser**
```bash
python3 manage.py createsuperuser
```

7. **Start server**
```bash
python3 manage.py runserver
```

## Access URLs
- Django Admin: http://127.0.0.1:8000/admin/
- Main App: http://127.0.0.1:8000/

## Environment Variables
Ensure `.env` file exists with:
```
DB_NAME=crisp_trust_db
DB_USER=postgres
DB_PASSWORD=AdminPass123!
DB_HOST=localhost
DB_PORT=5432
DEBUG=True
```