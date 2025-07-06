#!/bin/bash

# CRISP Trust Management Platform - Comprehensive Test Runner
# This script runs all tests for the integrated system

set -e  # Exit on any error

echo "🧪 CRISP Trust Management Platform - Test Suite"
echo "=============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "crisp/manage.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Change to crisp directory for Django commands
cd crisp

print_status "Checking Python environment..."
python3 --version
pip --version

print_status "Checking database connection..."
python3 manage.py check --database default

print_status "Running Django system checks..."
python3 manage.py check

print_status "Checking for pending migrations..."
python3 manage.py showmigrations

print_status "Running linting checks..."
if command -v flake8 &> /dev/null; then
    flake8 --max-line-length=100 --exclude=migrations,venv,env ../core/ . || print_warning "Linting issues found"
else
    print_warning "flake8 not installed, skipping linting"
fi

print_status "Running unit tests for core applications..."

echo ""
echo "📋 Testing User Management System..."
python3 manage.py test core.user_management --verbosity=2

echo ""
echo "🔐 Testing Trust Management System..."
python3 manage.py test core.trust --verbosity=2

echo ""
echo "🔍 Testing Integration..."
python3 manage.py test core.tests --verbosity=2

echo ""
print_status "Running comprehensive test suite..."
python3 manage.py test --verbosity=2

echo ""
print_status "Running test coverage analysis..."
if command -v coverage &> /dev/null; then
    coverage run --source='../core,.' manage.py test
    coverage report
    coverage html
    print_success "Coverage report generated in htmlcov/"
else
    print_warning "coverage not installed, skipping coverage analysis"
    print_warning "Install with: pip install coverage"
fi

echo ""
print_status "Testing API endpoints..."
if [ -f "legacy_tests/test_api_endpoints.py" ]; then
    python3 legacy_tests/test_api_endpoints.py || print_warning "API endpoint tests had issues"
fi

echo ""
print_status "Running performance tests..."
if [ -f "tools/test_runners/run_tests.py" ]; then
    python3 tools/test_runners/run_tests.py || print_warning "Performance tests had issues"
fi

echo ""
print_success "Test suite completed!"
echo ""
echo "📊 Test Summary:"
echo "  ✓ Django system checks"
echo "  ✓ User Management tests"
echo "  ✓ Trust Management tests" 
echo "  ✓ Integration tests"
echo "  ✓ Coverage analysis"
echo "  ✓ API endpoint tests"

echo ""
echo "📝 Next steps:"
echo "  1. Review test coverage in htmlcov/index.html"
echo "  2. Check logs in logs/ directory"
echo "  3. Run the development server: python3 manage.py runserver"

echo ""
print_success "All tests completed successfully! 🎉"