#!/bin/bash

# CRISP Trust Management Platform - Startup Script
# This script sets up and runs the CRISP platform

set -e  # Exit on any error

echo "🚀 CRISP Trust Management Platform - Startup"
echo "============================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "crisp/manage.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check for required environment variables
if [ -z "$DB_NAME" ]; then
    print_warning "DB_NAME not set, using default: crisp_trust_db"
    export DB_NAME=crisp_trust_db
fi

if [ -z "$DB_USER" ]; then
    print_warning "DB_USER not set, using default: crisp_user"
    export DB_USER=crisp_user
fi

if [ -z "$DB_PASSWORD" ]; then
    print_warning "DB_PASSWORD not set, using default: crisp_password"
    export DB_PASSWORD=crisp_password
fi

# Change to crisp directory
cd crisp

print_status "Checking system requirements..."

# Check Python version
python_version=$(python --version 2>&1)
print_status "Python version: $python_version"

# Check Django
django_version=$(python -c "import django; print(django.get_version())" 2>/dev/null || echo "Not installed")
print_status "Django version: $django_version"

# Check PostgreSQL connection
print_status "Checking database connection..."
if python manage.py check --database default &>/dev/null; then
    print_success "Database connection successful"
else
    print_error "Database connection failed!"
    print_error "Please ensure PostgreSQL is running and credentials are correct"
    print_error "Required environment variables:"
    print_error "  DB_NAME=$DB_NAME"
    print_error "  DB_USER=$DB_USER"
    print_error "  DB_PASSWORD=<set in environment>"
    exit 1
fi

print_status "Running system checks..."
python manage.py check

print_status "Checking migrations..."
migration_status=$(python manage.py showmigrations --plan 2>/dev/null | grep -c "\[ \]" || echo "0")

if [ "$migration_status" -gt "0" ]; then
    print_warning "Found $migration_status unapplied migrations"
    read -p "Apply migrations now? (y/N): " apply_migrations
    if [ "$apply_migrations" = "y" ] || [ "$apply_migrations" = "Y" ]; then
        print_status "Applying migrations..."
        python manage.py migrate
        print_success "Migrations applied successfully"
    else
        print_warning "Migrations not applied. System may not work correctly."
    fi
else
    print_success "All migrations are up to date"
fi

# Check if superuser exists
print_status "Checking for admin user..."
admin_exists=$(python manage.py shell -c "from core.user_management.models import CustomUser; print(CustomUser.objects.filter(role='BlueVisionAdmin').exists())" 2>/dev/null || echo "False")

if [ "$admin_exists" = "False" ]; then
    print_warning "No admin user found"
    read -p "Create admin user now? (y/N): " create_admin
    if [ "$create_admin" = "y" ] || [ "$create_admin" = "Y" ]; then
        print_status "Creating admin user..."
        python manage.py createsuperuser
    fi
fi

# Collect static files if in production
if [ "$DEBUG" = "False" ]; then
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Create logs directory
mkdir -p logs

print_status "Starting CRISP Trust Management Platform..."
print_success "System is ready!"

echo ""
echo "🌐 API Endpoints:"
echo "  Authentication: http://localhost:8000/api/v1/auth/"
echo "  Users:          http://localhost:8000/api/v1/users/"
echo "  Organizations:  http://localhost:8000/api/v1/organizations/"
echo "  Admin:          http://localhost:8000/api/v1/admin/"
echo "  Django Admin:   http://localhost:8000/admin/"

echo ""
echo "📚 Documentation:"
echo "  Project docs:   docs_project/"
echo "  API docs:       Available when browsing API endpoints"
echo "  Coverage:       htmlcov/index.html (after running tests)"

echo ""
print_status "Starting development server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the development server
python manage.py runserver