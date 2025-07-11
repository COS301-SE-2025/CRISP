#!/bin/bash

# CRISP Platform Server Stop Script
echo "🛑 Stopping CRISP Platform Server..."

# Kill Django processes
DJANGO_PIDS=$(pgrep -f "manage.py runserver")

if [ -z "$DJANGO_PIDS" ]; then
    echo "✅ No Django server processes found running"
else
    echo "🔧 Found Django server processes: $DJANGO_PIDS"
    echo "🛑 Stopping Django servers..."
    pkill -f "manage.py runserver"
    sleep 2
    
    # Check if processes are still running
    REMAINING_PIDS=$(pgrep -f "manage.py runserver")
    if [ -z "$REMAINING_PIDS" ]; then
        echo "✅ All Django servers stopped successfully"
    else
        echo "⚠️  Some processes may still be running: $REMAINING_PIDS"
        echo "🔧 Force killing remaining processes..."
        pkill -9 -f "manage.py runserver"
        echo "✅ All processes forcefully stopped"
    fi
fi

# Check ports 8000-8010 for any remaining Django processes
echo "🔍 Checking ports 8000-8010..."
for port in {8000..8010}; do
    if lsof -i :$port > /dev/null 2>&1; then
        PID=$(lsof -ti :$port)
        echo "⚠️  Port $port still in use by PID $PID"
    fi
done

echo "🏁 Server stop script completed"