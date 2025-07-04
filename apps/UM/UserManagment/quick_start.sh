#!/bin/bash

# CRISP User Management Quick Start Script

echo "CRISP User Management Quick Start"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

print_status "Python 3 found"

# Check if PostgreSQL is available
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL command line tools not found. Please ensure PostgreSQL is installed."
    echo "Installation instructions:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "  macOS: brew install postgresql"
    echo "  Windows: Download from https://www.postgresql.org/download/windows/"
    echo ""
fi

# Create virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv
if [ $? -eq 0 ]; then
    print_status "Virtual environment created"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Install requirements
echo "📥 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    print_status "Requirements installed successfully"
else
    print_error "Failed to install requirements"
    exit 1
fi

# Check .env file
if [ ! -f .env ]; then
    print_warning ".env file not found. Using default environment variables."
    echo "You may need to create a .env file with your database credentials."
fi

# Test database connection
echo "🔌 Testing database connection..."
python3 -c "
import os
import sys
try:
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv()
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'crisp'),
        user=os.getenv('DB_USER', 'admin'),
        password=os.getenv('DB_PASSWORD', 'AdminPassword')
    )
    print('Database connection successful!')
    conn.close()
except ImportError:
    print('psycopg2 not installed correctly')
    sys.exit(1)
except Exception as e:
    print(f'Database connection failed: {e}')
    print('Please ensure PostgreSQL is running and database/user exists:')
    print('  sudo -u postgres psql')
    print('  CREATE DATABASE crisp;')
    print('  CREATE USER admin WITH ENCRYPTED PASSWORD \"AdminPassword\";')
    print('  GRANT ALL PRIVILEGES ON DATABASE crisp TO admin;')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_status "Database connection successful"
else
    print_error "Database connection failed"
    echo "Please check your database setup. See setup_guide.md for detailed instructions."
    exit 1
fi

# Run migrations
echo "🏗️  Running database migrations..."
python manage.py makemigrations UserManagement
python manage.py migrate
if [ $? -eq 0 ]; then
    print_status "Database migrations completed"
else
    print_error "Database migrations failed"
    exit 1
fi

# Create superuser
echo "👤 Creating superuser..."
echo "Default credentials: admin / AdminPassword123!"
python manage.py setup_auth --create-superuser --username=admin --email=admin@crisp.local --password=AdminPassword123! --non-interactive
if [ $? -eq 0 ]; then
    print_status "Superuser created successfully"
    echo "   Username: admin"
    echo "   Password: AdminPassword123!"
else
    print_warning "Superuser creation failed or user already exists"
fi

# Run basic tests
echo "🧪 Running basic tests..."
python manage.py test UserManagement.tests.test_authentication.AuthenticationStrategyTestCase.test_standard_authentication_success --verbosity=0
if [ $? -eq 0 ]; then
    print_status "Basic tests passing"
else
    print_warning "Some tests failed - check implementation"
fi

echo ""
echo "🎉 Setup Complete!"
echo "================="
echo ""
echo "Next steps:"
echo "1. Start the development server:"
echo "   python manage.py runserver"
echo ""
echo "2. Test the admin interface:"
echo "   http://127.0.0.1:8000/admin/"
echo "   Login: admin / AdminPassword123!"
echo ""
echo "3. Test API endpoints:"
echo "   curl -X POST http://127.0.0.1:8000/api/auth/login/ \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"username\": \"admin\", \"password\": \"AdminPassword123!\"}'"
echo ""
echo "4. Run the full test suite:"
echo "   python manage.py test UserManagement"
echo ""
echo "5. Audit users:"
echo "   python manage.py audit_users --security-focus"
echo ""
print_status "Ready to go!"