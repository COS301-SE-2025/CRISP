#!/bin/bash
# Docker Initialization Script for CRISP with Asset-Based Alert System
# Handles database migrations, demo data setup, and asset alert system initialization.

set -e  # Exit on any error

echo "🎯 CRISP Docker Initialization Starting..."
echo "============================================="

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python manage.py wait_for_db

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Setup base users
echo "👥 Setting up base users..."
python manage.py setup_base_users

# Conditional test data population
if [ "$POPULATE_TEST_DATA" = "true" ]; then
    echo "📊 Populating test data..."
    python manage.py populate_database --no-input
fi

# Clean up invalid feeds
echo "🧹 Cleaning up invalid feeds..."
python manage.py cleanup_feeds --force

# Setup VirusTotal feed
echo "🦠 Setting up VirusTotal feed..."
python manage.py setup_virustotal_feed --with-samples

# Setup Asset-Based Alert System (WOW Factor #1)
echo "🎯 Setting up Asset-Based Alert System (WOW Factor #1)..."
python manage.py demo_asset_alerts --mode setup --organization "Demo University"

# Generate demo alerts to showcase functionality
echo "🚨 Generating demo alerts..."
python manage.py demo_asset_alerts --mode demo

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ CRISP Initialization Complete!"
echo "🌟 Asset-Based Alert System Ready!"
echo "==============================================="
echo "📋 What's Available:"
echo "   • Demo University organization with sample assets"
echo "   • Asset inventory (IP ranges, domains, software)"
echo "   • Custom alerts generated from threat correlation"
echo "   • Multi-channel notification system"
echo "   • Frontend management interface at /assets"
echo ""
echo "🚀 Access Points:"
echo "   • Main Application: http://localhost:5173"
echo "   • Asset Management: http://localhost:5173/assets"
echo "   • API Documentation: http://localhost:8000/api/"
echo ""
echo "📖 Demo Credentials:"
echo "   • Username: demo_security_admin"
echo "   • Password: demo123"
echo "   • Role: Publisher (can access Asset Management)"
echo ""

# Start the Django development server
echo "🔴 Starting Django server on 0.0.0.0:8000..."
exec python manage.py runserver 0.0.0.0:8000