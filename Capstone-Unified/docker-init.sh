#!/bin/bash
set -e

echo "🎯 CRISP Docker Initialization Starting..."
echo "============================================="

echo "⏳ Waiting for database connection..."
python manage.py wait_for_db

echo "🔄 Running database migrations..."
python manage.py migrate

echo "👥 Setting up base users..."
python manage.py setup_base_users

if [ "$POPULATE_TEST_DATA" = "true" ]; then
    echo "📊 Populating test data..."
    python manage.py populate_database --no-input
fi

echo "🧹 Cleaning up invalid feeds..."
python manage.py cleanup_feeds --force

echo "🦠 Setting up VirusTotal feed..."
python manage.py setup_virustotal_feed --with-samples

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ CRISP Initialization Complete!"
echo "🌟 Asset-Based Alert System Ready!"

echo "🔴 Starting Django server on 0.0.0.0:8000..."
exec python manage.py runserver 0.0.0.0:8000
