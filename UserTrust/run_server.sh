#!/bin/bash

# CRISP Platform Server Startup Script
echo "🚀 Starting CRISP Platform Server..."
echo "📍 Location: /mnt/c/Users/Client/Documents/GitHub/CRISP/UserTrust"

# Default port
PORT=8000

# Check if port is in use and find alternative
while lsof -i :$PORT > /dev/null 2>&1; do
    echo "⚠️  Port $PORT is already in use"
    # Try to kill existing Django processes
    echo "🔧 Attempting to stop existing Django server..."
    pkill -f "manage.py runserver" 2>/dev/null
    sleep 2
    
    # If still in use, try next port
    if lsof -i :$PORT > /dev/null 2>&1; then
        PORT=$((PORT + 1))
        echo "🔄 Trying port $PORT instead..."
    fi
    
    # Safety check to avoid infinite loop
    if [ $PORT -gt 8010 ]; then
        echo "❌ No available ports found between 8000-8010"
        exit 1
    fi
done

echo "🌐 Server will be available at: http://localhost:$PORT"
echo "📊 Admin interface: http://localhost:$PORT/admin/"
echo "🔗 API endpoints: http://localhost:$PORT/api/v1/"
echo ""

# Navigate to project directory
cd /mnt/c/Users/Client/Documents/GitHub/CRISP/UserTrust/crisp

# Check if PostgreSQL is running
if ! pg_isready > /dev/null 2>&1; then
    echo "⚠️  PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

echo "✅ PostgreSQL is running"
echo "🔧 Running Django checks..."

# Run Django checks
python3 manage.py check

if [ $? -eq 0 ]; then
    echo "✅ Django configuration is valid"
    echo "🚀 Starting development server on port $PORT..."
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "=================================="
    
    # Start the Django development server
    python3 manage.py runserver 0.0.0.0:$PORT
else
    echo "❌ Django configuration check failed"
    exit 1
fi