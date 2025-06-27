#!/bin/bash
# CRISP Startup Script
echo "🚀 Starting CRISP - Cyber Risk Information Sharing Platform"
echo "=================================================="

# Navigate to core directory
cd "$(dirname "$0")/.."

# Check if Django is available
python3 -c "import django" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Django not found. Please install requirements:"
    echo "   pip install -r requirements/base.txt"
    exit 1
fi

echo "✅ Django found"
echo "🌐 Starting Django development server..."
echo "📱 Access at: http://127.0.0.1:8000/admin/"
echo "🔑 Login: admin / admin"
echo ""

# Start the Django server
python3 manage.py runserver
