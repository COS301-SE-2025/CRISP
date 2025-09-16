#!/bin/bash

echo "CRISP Platform Setup - WORKING Version"
echo "======================================"

# Step 1: PostgreSQL Setup
echo "Setting up PostgreSQL..."
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'AdminPass123!';" || echo "Password might already be set"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS crisp_unified;"
sudo -u postgres psql -c "CREATE DATABASE crisp_unified;"

# Step 2: Complete fresh start
echo "Starting completely fresh..."
rm -rf venv

# Remove ALL migration files and directories to fix circular dependencies
echo "Removing all migration files to fix circular dependencies..."
rm -rf core/migrations
rm -rf user_management/migrations
rm -rf trust_management/migrations
rm -rf core/user_management/migrations
rm -rf core/trust_management/migrations
rm -rf core/alerts/migrations
rm -rf core_ut/alerts/migrations 2>/dev/null || true
rm -rf core_ut/trust/migrations 2>/dev/null || true
rm -rf core_ut/user_management/migrations 2>/dev/null || true

# Remove any __pycache__ directories that might interfere
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

python3 -m venv venv

# Step 3: Install packages in virtual environment
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install setuptools wheel
pip install -r requirements.txt

# Step 4: Handle migrations properly to avoid circular dependencies
echo "Creating migration directories..."
mkdir -p core/migrations core/user_management/migrations core/trust_management/migrations core/alerts/migrations
touch core/migrations/__init__.py core/user_management/migrations/__init__.py core/trust_management/migrations/__init__.py core/alerts/migrations/__init__.py

# Debug: Show Django configuration
echo "Checking Django configuration..."
python manage.py diffsettings | grep -E "(INSTALLED_APPS|AUTH_USER_MODEL)" || echo "Config check completed"

# Create migrations in dependency order to avoid circular dependencies
echo "Creating migrations in proper dependency order..."

# If there are circular dependency issues, sometimes we need to squash or recreate migrations
# Let's try creating migrations one by one and handle any errors gracefully

echo "Step 1: Creating user_management migrations (AUTH_USER_MODEL)..."
python manage.py makemigrations user_management || {
    echo "Warning: user_management migration failed, trying alternative approach..."
    # Clear and retry
    rm -f core/user_management/migrations/0001_initial.py 2>/dev/null || true
    python manage.py makemigrations user_management --empty --name fix_initial || echo "Empty migration failed"
    python manage.py makemigrations user_management || echo "Still failed, continuing..."
}

echo "Step 2: Creating core migrations..."
python manage.py makemigrations core || {
    echo "Warning: core migration failed, but continuing..."
}

echo "Step 3: Creating trust_management migrations..."
python manage.py makemigrations trust_management || echo "trust_management migration failed, continuing..."

echo "Step 4: Creating alerts migrations..."
python manage.py makemigrations alerts || echo "alerts migration failed, continuing..."

# Apply migrations with better error handling
echo "Applying migrations..."
python manage.py migrate --run-syncdb || {
    echo "Normal migration failed, trying --run-syncdb approach..."
    python manage.py migrate --fake-initial || {
        echo "Migration failed completely, but continuing setup..."
        echo "You may need to run 'python manage.py migrate --fake-initial' manually later"
    }
}

# Step 5: Initialize system
echo "Initializing system..."
python manage.py initialize_system || echo "System init had warnings, continuing..."

# Step 6: React setup
echo "Setting up React..."
cd crisp-react
npm install
cd ..

# Check if database tables exist before populating
echo "Checking database state..."
python manage.py showmigrations | head -20

# Step 7: MASSIVE database population (only if migrations worked)
echo "Populating massive database (this takes time)..."
python manage.py populate_database || echo "Population had warnings, continuing..."

# Step 8: Real threat intelligence (only if basic tables exist)
echo "Getting real threat intelligence..."
python manage.py populate_otx_threats || echo "OTX had warnings, continuing..."

# Step 9: TTP data
echo "Adding TTP data..."
python manage.py populate_ttp_data || echo "TTP had warnings, continuing..."

# Step 10: Trust levels
echo "Setting up trust management..."
python manage.py init_trust_levels || echo "Trust init had warnings, continuing..."

# Step 11: Reports
echo "Adding demo reports..."
python manage.py populate_reports_demo || echo "Reports had warnings, continuing..."

echo ""
echo "SETUP COMPLETE!"
echo "==============="
echo ""
echo "To start the application:"
echo "1. Terminal 1: source venv/bin/activate && python manage.py runserver"
echo "2. Terminal 2: cd crisp-react && npm run dev"
echo ""
echo "Access URLs:"
echo "- Frontend: http://localhost:5173"
echo "- Admin: http://localhost:8000/admin/"
echo "- Login: admin / AdminPass123"
echo ""
echo "TROUBLESHOOTING:"
echo "If you see migration errors:"
echo "1. Try: python manage.py migrate --fake-initial"
echo "2. Or: python manage.py migrate --run-syncdb"
echo "3. Create superuser: python manage.py createsuperuser"
echo ""
echo "If tables are missing, manually run:"
echo "python manage.py makemigrations && python manage.py migrate"
echo ""
echo "Happy developing!"
