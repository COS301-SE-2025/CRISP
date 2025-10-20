# CRISP Capstone-Unified Setup Guide

## Prerequisites
- PostgreSQL installed and running
- Python 3.10+
- pip3

## Database Setup

1. **Set PostgreSQL password**
```bash
# Replace 'your_secure_password' with a strong password
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_secure_password';"
```

2. **Create database**
```bash
sudo -u postgres psql -c "CREATE DATABASE crisp_trust_db;"
```

3. **Test connection**
```bash
# Use the password you set in step 1
PGPASSWORD='your_secure_password' psql -h localhost -U postgres -d crisp_trust_db -c "SELECT version();"
```

## Django Setup

4. **Configure environment variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
# Update DB_PASSWORD to match the password from step 1
nano .env
```

5. **Install dependencies**
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
Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```bash
DB_NAME=crisp_trust_db
DB_USER=postgres
DB_PASSWORD=your_secure_password  # Use the password from step 1
DB_HOST=localhost
DB_PORT=5432
DEBUG=True
DJANGO_SECRET_KEY=your-generated-secret-key  # Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

⚠️ **Never commit `.env` to git - it's already in .gitignore**