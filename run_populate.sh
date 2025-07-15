#!/bin/bash

echo "🚀 CRISP Database Population Setup"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Install faker if not present
echo "📦 Installing required dependencies..."
pip install faker

# Check if database is accessible
echo "🔍 Checking database connection..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.TrustManagement.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('Please ensure PostgreSQL is running and your .env file is configured correctly')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎯 Starting database population..."
    python populate_database.py
else
    echo "❌ Database check failed. Please fix database connection before running population script."
fi