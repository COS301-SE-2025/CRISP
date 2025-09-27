#!/bin/bash

# Quick Redis Start Script for CRISP Threat Feed Consumption
# This script starts Redis and Celery worker for async threat feed processing

echo "🔄 Starting Redis and Celery for async threat feed consumption..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "📦 Starting Redis container..."
    docker run -d --name crisp-redis -p 6379:6379 redis:latest

    echo "⏳ Waiting for Redis to start..."
    sleep 3

    echo "🔄 Starting Celery worker..."
    celery -A settings worker --loglevel=info --detach

    echo "✅ Redis and Celery started successfully!"
    echo ""
    echo "🎯 You can now use async threat feed consumption in the web UI."
    echo "📋 To stop Redis later: docker stop crisp-redis && docker rm crisp-redis"

elif command -v redis-server &> /dev/null; then
    echo "📦 Starting Redis server..."
    redis-server --daemonize yes

    echo "🔄 Starting Celery worker..."
    celery -A settings worker --loglevel=info --detach

    echo "✅ Redis and Celery started successfully!"
    echo ""
    echo "🎯 You can now use async threat feed consumption in the web UI."
    echo "📋 To stop Redis later: pkill redis-server"

else
    echo "❌ Neither Docker nor Redis is installed."
    echo "💡 SOLUTION: Use the direct consumption command instead:"
    echo ""
    echo "   # Consume specific feed"
    echo "   python3 manage.py consume_threat_feeds --feed-name 'AlienVault OTX' --limit 10"
    echo ""
    echo "   # Consume all feeds"
    echo "   python3 manage.py consume_threat_feeds --all --limit 5"
    echo ""
    echo "   # Test connections"
    echo "   python3 manage.py consume_threat_feeds --feed-name 'OTX' --dry-run"
fi