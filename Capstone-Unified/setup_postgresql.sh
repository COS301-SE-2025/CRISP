#!/bin/bash

# PostgreSQL Setup Script for CRISP Unified Platform

echo "Setting up PostgreSQL for CRISP Unified Platform..."

# Start PostgreSQL service
echo "Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
echo "Creating database and user..."
sudo -u postgres psql << EOF
CREATE DATABASE crisp_unified;
CREATE USER crisp_user WITH PASSWORD 'crisp_password';
GRANT ALL PRIVILEGES ON DATABASE crisp_unified TO crisp_user;
ALTER USER crisp_user CREATEDB;
\q
EOF

# Grant schema permissions
echo "Granting schema permissions..."
sudo -u postgres psql -d crisp_unified << EOF
GRANT ALL PRIVILEGES ON SCHEMA public TO crisp_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crisp_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crisp_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO crisp_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO crisp_user;
\q
EOF

# Update environment file
echo "Updating .env file for PostgreSQL..."
cat > .env << EOF
# Database Configuration
# Set USE_SQLITE=false for PostgreSQL
USE_SQLITE=false

# PostgreSQL Configuration
DB_NAME=crisp_unified
DB_USER=crisp_user
DB_PASSWORD=crisp_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
DEBUG=true
SECRET_KEY=django-insecure-development-key-change-in-production

# CORS Configuration
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
EOF

# Install PostgreSQL Python adapter if not present
echo "Installing PostgreSQL Python adapter..."
pip3 install psycopg2-binary --break-system-packages

# Run Django migrations
echo "Running Django migrations..."
python3 manage.py migrate

# Create superuser
echo "Creating superuser..."
python3 manage.py shell << EOF
from core.models.models import CustomUser, Organization
from django.contrib.auth.hashers import make_password

# Create default organization
org, created = Organization.objects.get_or_create(
    name="Blue Vision Technologies",
    defaults={
        'domain': 'bluevision.tech',
        'organization_type': 'private',
        'description': 'Default administrative organization',
        'contact_email': 'admin@bluevision.tech',
        'is_active': True
    }
)

# Create superuser
user, created = CustomUser.objects.get_or_create(
    username='bluevision_admin',
    defaults={
        'email': 'admin@bluevision.tech',
        'first_name': 'Blue Vision',
        'last_name': 'Admin',
        'role': 'BlueVisionAdmin',
        'organization': org,
        'is_active': True,
        'is_staff': True,
        'is_superuser': True,
        'password': make_password('admin123')
    }
)

if created:
    print(f"Created superuser: {user.username}")
else:
    print(f"Superuser already exists: {user.username}")
EOF

echo "PostgreSQL setup complete!"
echo "Database: crisp_unified"
echo "User: crisp_user"
echo "Password: crisp_password"
echo "Admin user: bluevision_admin / admin123"
echo ""
echo "To start the server with PostgreSQL:"
echo "python3 manage.py runserver"