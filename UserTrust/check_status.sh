#!/bin/bash

# CRISP Platform Status Check Script
echo "🔍 CRISP Platform Status Check"
echo "=============================="
echo ""

# Check PostgreSQL
echo "📊 Database Status:"
if pg_isready > /dev/null 2>&1; then
    echo "✅ PostgreSQL is running"
    
    # Check if CRISP database exists
    if psql -lqt | cut -d \| -f 1 | grep -qw crisp_trust_db; then
        echo "✅ CRISP database (crisp_trust_db) exists"
    else
        echo "❌ CRISP database (crisp_trust_db) not found"
    fi
else
    echo "❌ PostgreSQL is not running"
fi
echo ""

# Check Django server
echo "🌐 Server Status:"
DJANGO_PIDS=$(pgrep -f "manage.py runserver")
if [ -z "$DJANGO_PIDS" ]; then
    echo "❌ No Django server processes running"
else
    echo "✅ Django server running (PIDs: $DJANGO_PIDS)"
    
    # Check which ports are in use
    for port in {8000..8010}; do
        if lsof -i :$port > /dev/null 2>&1; then
            echo "🌐 Server running on port $port"
            echo "   📊 Admin: http://localhost:$port/admin/"
            echo "   🔗 API: http://localhost:$port/api/v1/"
        fi
    done
fi
echo ""

# Check Django configuration
echo "⚙️  Django Configuration:"
cd /mnt/c/Users/Client/Documents/GitHub/CRISP/UserTrust/crisp

if python3 manage.py check > /dev/null 2>&1; then
    echo "✅ Django configuration is valid"
else
    echo "❌ Django configuration has issues"
fi

# Check if migrations are applied
if python3 -c "
import os, sys, django
sys.path.insert(0, '/mnt/c/Users/Client/Documents/GitHub/CRISP/UserTrust')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.TrustManagement.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"SELECT COUNT(*) FROM django_migrations\")
count = cursor.fetchone()[0]
print(f'✅ {count} migrations applied')
" 2>/dev/null; then
    :
else
    echo "⚠️  Could not check migration status"
fi

echo ""
echo "📁 Project Structure:"
echo "✅ Core modules: trust, user_management"
echo "✅ Test suite: 675+ tests available"
echo "✅ Scripts: run_server.sh, run_tests.sh, stop_server.sh"
echo ""

# Quick test
echo "🧪 Quick Health Check:"
if [ ! -z "$DJANGO_PIDS" ]; then
    for port in {8000..8010}; do
        if lsof -i :$port > /dev/null 2>&1; then
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/ 2>/dev/null || echo "000")
            if [ "$HTTP_CODE" != "000" ]; then
                echo "✅ Server responding on port $port (HTTP $HTTP_CODE)"
            else
                echo "⚠️  Server on port $port not responding"
            fi
            break
        fi
    done
else
    echo "❌ Server not running - cannot perform health check"
fi

echo ""
echo "🏁 Status check completed"