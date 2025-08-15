#!/bin/bash

# CRISP Unified System Test Runner
# Comprehensive testing script for the unified CRISP platform

set -e

echo "🧪 CRISP Unified System Test Suite"
echo "=================================="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate || source venv/Scripts/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run deploy.sh first."
    exit 1
fi

# Set test environment
export DJANGO_SETTINGS_MODULE=crisp_unified.test_settings

# Run system health check
echo "🏥 Running system health check..."
python manage.py system_health_check --verbose || echo "⚠️ Health check warnings found"

# Run Django tests
echo ""
echo "🐍 Running Django backend tests..."
python manage.py test --verbosity=2 --keepdb

# Run specific test suites
echo ""
echo "🔐 Testing Authentication System..."
python manage.py test core.tests.test_auth_integration --verbosity=2

echo ""
echo "🤝 Testing Trust Management..."
python manage.py test core.tests.test_trust_management --verbosity=2

echo ""
echo "👥 Testing User Management..."
python manage.py test core.tests.test_user_management --verbosity=2

echo ""
echo "🏢 Testing Organization Management..."
python manage.py test core.tests.test_organization_management --verbosity=2

echo ""
echo "🛡️ Testing Threat Intelligence..."
python manage.py test core.tests.test_threat_intel --verbosity=2

echo ""
echo "🔒 Testing Anonymization..."
python manage.py test core.tests.test_anonymization --verbosity=2

echo ""
echo "📡 Testing TAXII Integration..."
python manage.py test core.tests.test_taxii_integration --verbosity=2

# Test management commands
echo ""
echo "⚙️ Testing Management Commands..."
python manage.py test core.tests.test_management_commands --verbosity=2

# Run frontend tests if available
if [ -d "crisp-react" ]; then
    echo ""
    echo "⚛️ Running React frontend tests..."
    cd crisp-react
    if [ -f "package.json" ] && grep -q '"test"' package.json; then
        npm test -- --watchAll=false
    else
        echo "ℹ️ No frontend tests configured"
    fi
    cd ..
fi

# Performance tests
echo ""
echo "⚡ Running performance tests..."
python manage.py test core.tests.test_performance --verbosity=2

# Security tests
echo ""
echo "🔒 Running security tests..."
python manage.py test core.tests.test_security --verbosity=2

echo ""
echo "✅ All tests completed successfully!"
echo ""
echo "📊 Test Summary:"
echo "- Backend tests: Django test suite"
echo "- Authentication: JWT and user management"
echo "- Trust Management: Trust relationships and groups"
echo "- Threat Intelligence: Feeds, indicators, and TTPs"
echo "- Anonymization: Trust-aware anonymization"
echo "- TAXII: STIX/TAXII integration"
echo "- Performance: System performance validation"
echo "- Security: Security feature validation"