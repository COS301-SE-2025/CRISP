#!/bin/bash
# Setup script for Trust Management development environment

set -e

echo "Setting up Trust Management development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing development dependencies..."
pip install --upgrade pip
pip install -r requirements/development.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if not exists
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    print('Creating superuser...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Set up trust configuration
echo "Setting up default trust configuration..."
python manage.py setup_trust --create-defaults

echo "Development environment setup complete!"
echo "To activate the environment, run: source venv/bin/activate"
echo "To start the development server, run: python manage.py runserver"
