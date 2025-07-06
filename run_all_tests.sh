#!/bin/bash

# CRISP Trust Management Platform - Comprehensive Test Runner
# This script runs all tests for the integrated system

set -e  # Exit on any error

echo "🧪 CRISP Trust Management Platform - Complete Test Suite"
echo "========================================================"

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

# Add the project root to PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Change to crisp directory for Django commands
cd crisp

print_status "🔧 Checking Python environment..."
python3 --version
pip --version

print_status "🔍 Running Django system checks..."
DJANGO_SETTINGS_MODULE=test_settings python3 manage.py check

print_status "📋 Running ALL core tests..."
echo ""
echo "🧪 Testing All Core Applications:"
echo "  - Core Integration Tests"
echo "  - User Management Tests"
echo "  - Trust Management Tests"
echo "  - Model Tests"
echo "  - Service Tests"
echo "  - Repository Tests"
echo "  - Validator Tests"
echo ""

# Run all core tests with detailed output
DJANGO_SETTINGS_MODULE=test_settings python3 manage.py test core.tests core.user_management core.trust --verbosity=2

echo ""
print_status "📊 Running test coverage analysis..."
if command -v coverage &> /dev/null; then
    DJANGO_SETTINGS_MODULE=test_settings coverage run --source='../core' manage.py test core.tests core.user_management core.trust
    coverage report
    coverage html
    print_success "Coverage report generated in htmlcov/"
else
    print_warning "coverage not installed, skipping coverage analysis"
    print_warning "Install with: pip install coverage"
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
echo ""
print_success "All tests completed successfully!"