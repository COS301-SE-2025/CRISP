#!/bin/bash

# Check SSH Tunnels Status Script
# This script checks the status of SSH tunnels to the Raspberry Pi

PI_HOST="100.117.251.119"
LOCAL_DB_PORT="5433"
LOCAL_REDIS_PORT="6380"

echo "🔍 Checking SSH tunnel status..."
echo ""

# Check database tunnel
if pgrep -f "ssh.*$PI_HOST.*$LOCAL_DB_PORT:localhost:5432" > /dev/null; then
    echo "✅ Database tunnel: ACTIVE (localhost:$LOCAL_DB_PORT)"
else
    echo "❌ Database tunnel: INACTIVE"
fi

# Check Redis tunnel
if pgrep -f "ssh.*$PI_HOST.*$LOCAL_REDIS_PORT:localhost:6379" > /dev/null; then
    echo "✅ Redis tunnel: ACTIVE (localhost:$LOCAL_REDIS_PORT)"
else
    echo "❌ Redis tunnel: INACTIVE"
fi

echo ""
echo "🌐 Testing connections..."

# Test database connection
if command -v nc &> /dev/null; then
    if nc -z localhost $LOCAL_DB_PORT 2>/dev/null; then
        echo "✅ Database port $LOCAL_DB_PORT: REACHABLE"
    else
        echo "❌ Database port $LOCAL_DB_PORT: NOT REACHABLE"
    fi
    
    if nc -z localhost $LOCAL_REDIS_PORT 2>/dev/null; then
        echo "✅ Redis port $LOCAL_REDIS_PORT: REACHABLE"
    else
        echo "❌ Redis port $LOCAL_REDIS_PORT: NOT REACHABLE"
    fi
else
    echo "⚠️  Install 'nc' (netcat) to test port connectivity"
fi