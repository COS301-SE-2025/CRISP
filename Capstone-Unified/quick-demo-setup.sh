#!/bin/bash

# Quick Demo Setup Script for CRISP Asset Alert System
# Use this for fast local testing without Docker

set -e

echo "🚀 CRISP Quick Demo Setup"
echo "=========================="

echo "📋 Applying migrations..."
python manage.py migrate

echo "👥 Setting up users..."
python manage.py setup_base_users

echo "🎯 Setting up Asset Alert System demo..."
python manage.py setup_complete_demo --quick

echo "✅ Quick demo setup complete!"
echo ""
echo "🔐 Demo credentials are in: DEMO_USER_CREDENTIALS.md"
echo "🌐 Start the server with: python manage.py runserver"
echo "📱 Start the frontend with: cd frontend/crisp-react && npm run dev"
echo ""
echo "🎯 Navigate to Asset Management to see the enhanced alert system!"