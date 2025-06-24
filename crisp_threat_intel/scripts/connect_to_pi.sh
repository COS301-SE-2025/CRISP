#!/bin/bash

# SSH Tunnel Script for Raspberry Pi Database Connection
# This script creates SSH tunnels for PostgreSQL and Redis connections

PI_USER="datadefenders"
PI_HOST="100.117.251.119"
LOCAL_DB_PORT="5433"
REMOTE_DB_PORT="5432"
LOCAL_REDIS_PORT="6380"
REMOTE_REDIS_PORT="6379"

echo "🔗 Setting up SSH tunnels to Raspberry Pi..."
echo "Pi Host: $PI_HOST"
echo "Database: localhost:$LOCAL_DB_PORT -> $PI_HOST:$REMOTE_DB_PORT"
echo "Redis: localhost:$LOCAL_REDIS_PORT -> $PI_HOST:$REMOTE_REDIS_PORT"

# Check if tunnels are already running
if pgrep -f "ssh.*$PI_HOST.*$LOCAL_DB_PORT:localhost:$REMOTE_DB_PORT" > /dev/null; then
    echo "⚠️  Database tunnel already running"
else
    echo "🚀 Starting database tunnel..."
    ssh -f -N -L $LOCAL_DB_PORT:localhost:$REMOTE_DB_PORT $PI_USER@$PI_HOST
    if [ $? -eq 0 ]; then
        echo "✅ Database tunnel established"
    else
        echo "❌ Failed to establish database tunnel"
        exit 1
    fi
fi

if pgrep -f "ssh.*$PI_HOST.*$LOCAL_REDIS_PORT:localhost:$REMOTE_REDIS_PORT" > /dev/null; then
    echo "⚠️  Redis tunnel already running"
else
    echo "🚀 Starting Redis tunnel..."
    ssh -f -N -L $LOCAL_REDIS_PORT:localhost:$REMOTE_REDIS_PORT $PI_USER@$PI_HOST
    if [ $? -eq 0 ]; then
        echo "✅ Redis tunnel established"
    else
        echo "❌ Failed to establish Redis tunnel"
        exit 1
    fi
fi

echo ""
echo "🎉 SSH tunnels are ready!"
echo "💡 To use tunneled connections:"
echo "   cp .env.tunnel .env"
echo ""
echo "🔍 To check tunnel status:"
echo "   ./scripts/check_tunnels.sh"
echo ""
echo "🛑 To stop tunnels:"
echo "   ./scripts/stop_tunnels.sh"