#!/bin/bash

# CRISP Trust Management Platform - Development Setup Script
# This script sets up the development environment from scratch

set -e  # Exit on any error

echo "🛠️  CRISP Trust Management Platform - Development Setup"
echo "====================================================="

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

print_status "Setting up CRISP development environment..."

# Check Python version
python_version=$(python --version 2>&1 | cut -d' ' -f2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python $required_version or higher required. Found: $python_version"
    exit 1
fi

print_success "Python version check passed: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || {
    print_error "Failed to activate virtual environment"
    exit 1
}

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r crisp/requirements/development.txt

print_success "Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f "crisp/.env" ]; then
    print_status "Creating .env file..."
    cat > crisp/.env << EOL
# CRISP Development Environment Configuration

# Database
DB_NAME=crisp_trust_db
DB_USER=crisp_user
DB_PASSWORD=crisp_password
DB_HOST=localhost
DB_PORT=5432

# Security
SECRET_KEY=dev-secret-key-change-in-production-$(openssl rand -hex 16)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Trust System Settings
TRUST_RELATIONSHIP_EXPIRY_DAYS=365
ACCOUNT_LOCKOUT_THRESHOLD=5
ACCOUNT_LOCKOUT_DURATION_MINUTES=30

# Email (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Logging
LOG_LEVEL=INFO

# Optional: Redis for caching
# REDIS_URL=redis://localhost:6379/1
EOL
    print_success ".env file created"
else
    print_status ".env file already exists"
fi

# Database setup instructions
echo ""
print_status "Database Setup Instructions:"
echo "=============================================="
echo ""
echo "1. Install PostgreSQL if not already installed:"
echo "   Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
echo "   MacOS: brew install postgresql"
echo "   Windows: Download from https://www.postgresql.org/download/"
echo ""
echo "2. Create database and user:"
echo "   sudo -u postgres psql"
echo "   CREATE DATABASE crisp_trust_db;"
echo "   CREATE USER crisp_user WITH PASSWORD 'crisp_password';"
echo "   GRANT ALL PRIVILEGES ON DATABASE crisp_trust_db TO crisp_user;"
echo "   ALTER USER crisp_user CREATEDB;  -- For testing"
echo "   \\q"
echo ""

# Check if PostgreSQL is running
if command -v pg_isready &> /dev/null; then
    if pg_isready -h localhost -p 5432 &>/dev/null; then
        print_success "PostgreSQL is running"
        
        # Try to connect to the database
        cd crisp
        if python manage.py check --database default &>/dev/null; then
            print_success "Database connection successful"
            
            # Run migrations
            print_status "Running database migrations..."
            python manage.py migrate
            print_success "Migrations completed"
            
            # Create superuser prompt
            print_status "Creating admin user..."
            echo "You'll be prompted to create an admin user for the system:"
            python manage.py createsuperuser || print_warning "Admin user creation skipped"
            
        else
            print_warning "Database connection failed. Please check your PostgreSQL setup."
            print_warning "Make sure the database 'crisp_trust_db' exists and user 'crisp_user' has access."
        fi
        cd ..
    else
        print_warning "PostgreSQL is not running. Please start PostgreSQL service."
    fi
else
    print_warning "PostgreSQL not found. Please install PostgreSQL first."
fi

# Create necessary directories
print_status "Creating project directories..."
mkdir -p crisp/logs
mkdir -p crisp/staticfiles
mkdir -p crisp/media

print_success "Project directories created"

echo ""
print_success "Development environment setup completed! 🎉"
echo ""
echo "📋 Next Steps:"
echo "1. Ensure PostgreSQL is running and database is set up"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run tests: ./run_tests.sh"
echo "4. Start development server: ./start_crisp.sh"
echo ""
echo "🔗 Useful Commands:"
echo "   Run tests:        ./run_tests.sh"
echo "   Start server:     ./start_crisp.sh"
echo "   Django shell:     cd crisp && python manage.py shell"
echo "   Create migration: cd crisp && python manage.py makemigrations"
echo "   Apply migration:  cd crisp && python manage.py migrate"
echo ""
echo "📚 Documentation:"
echo "   Main README:      README.md"
echo "   API Docs:         crisp/docs_project/"
echo "   Test Coverage:    htmlcov/index.html (after running tests)"