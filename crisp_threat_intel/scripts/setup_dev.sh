#!/bin/bash
# CRISP Threat Intelligence Platform - Development Setup Script

set -e

echo "🛡️ CRISP Threat Intelligence Platform - Development Setup"
echo "============================================================"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: This script must be run from the crisp_threat_intel directory"
    exit 1
fi

# Check Python version
echo "📋 Checking Python version..."
if ! python3 --version | grep -E "Python 3\.(8|9|10|11|12)" > /dev/null; then
    echo "❌ Error: Python 3.8+ is required"
    exit 1
fi

# Check PostgreSQL
echo "📋 Checking PostgreSQL..."
if ! command -v psql > /dev/null; then
    echo "❌ Error: PostgreSQL is not installed. Please install PostgreSQL first."
    echo "   Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "   macOS: brew install postgresql"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << 'EOF'
# CRISP Threat Intelligence Platform Configuration

# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here-change-in-production

# Database Configuration
DB_NAME=crisp
DB_USER=admin
DB_PASSWORD=AdminPassword
DB_HOST=localhost
DB_PORT=5432

# OTX Configuration
OTX_API_KEY=your-otx-api-key-here
OTX_ENABLED=True
OTX_FETCH_INTERVAL=3600
OTX_BATCH_SIZE=50
OTX_MAX_AGE_DAYS=30

# TAXII Settings
TAXII_SERVER_TITLE=CRISP Threat Intelligence Platform
TAXII_SERVER_DESCRIPTION=Educational threat intelligence sharing platform
TAXII_CONTACT_EMAIL=admin@example.com

# Security Settings
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Redis Configuration (optional, for Celery)
REDIS_URL=redis://localhost:6379/0
EOF
    echo "✅ Created .env file - please update with your actual values"
    echo "⚠️  IMPORTANT: Update OTX_API_KEY with your actual AlienVault OTX API key"
else
    echo "✅ .env file already exists"
fi

# Database setup
echo "🗄️ Setting up database..."

# Check if PostgreSQL is running
if ! pg_isready > /dev/null 2>&1; then
    echo "📋 Starting PostgreSQL..."
    if command -v systemctl > /dev/null; then
        sudo systemctl start postgresql
    elif command -v service > /dev/null; then
        sudo service postgresql start
    else
        echo "⚠️  Please start PostgreSQL manually"
    fi
fi

# Create database and user if they don't exist
echo "📋 Creating database and user..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'crisp'" | grep -q 1 || sudo -u postgres createdb crisp
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = 'admin'" | grep -q 1 || sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'AdminPassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE crisp TO admin;" || true
sudo -u postgres psql -c "ALTER USER admin CREATEDB;" || true

# Run migrations
echo "🔄 Running database migrations..."
python3 manage.py migrate

# Create superuser and setup platform
echo "👤 Setting up CRISP platform..."
python3 manage.py setup_crisp

# Test database setup
echo "🧪 Testing database setup..."
python3 tests/verify_postgresql.py

# Test OTX connection if API key is provided
if grep -q "your-otx-api-key-here" .env; then
    echo "⚠️  OTX API key not configured - skipping OTX setup"
    echo "   Please update OTX_API_KEY in .env and run: python3 manage.py setup_otx --fetch-data"
else
    echo "🌐 Testing OTX connection..."
    if python3 manage.py test_otx_connection; then
        echo "📡 Setting up OTX integration..."
        python3 manage.py setup_otx --fetch-data
    else
        echo "⚠️  OTX connection failed - please check your API key"
    fi
fi

# Collect static files
echo "📁 Collecting static files..."
python3 manage.py collectstatic --noinput

# Run tests
echo "🧪 Running basic tests..."
python3 run_tests.py --fast

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Quick Start:"
echo "   1. Start the server: python3 manage.py runserver"
echo "   2. Visit: http://localhost:8000"
echo "   3. Login: admin / admin123"
echo ""
echo "🧪 Run tests: python3 run_tests.py --all"
echo "📊 TAXII API: http://localhost:8000/taxii2/"
echo "📋 Admin panel: http://localhost:8000/admin/"
echo ""
echo "📚 Documentation: See README.md for detailed usage"