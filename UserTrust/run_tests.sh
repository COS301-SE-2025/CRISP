#!/bin/bash

# CRISP Platform Test Runner Script
echo "🧪 CRISP Platform Test Suite"
echo "============================="
echo ""

# Navigate to project directory
cd /mnt/c/Users/Client/Documents/GitHub/CRISP/UserTrust/crisp

# Check if PostgreSQL is running
if ! pg_isready > /dev/null 2>&1; then
    echo "⚠️  PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

echo "✅ PostgreSQL is running"
echo ""

# Display test options
echo "Available test options:"
echo "1. Run all tests (675+ tests - comprehensive)"
echo "2. Run model tests only (quick - 28 tests)"
echo "3. Run trust management tests"
echo "4. Run user management tests"
echo "5. Run integration tests"
echo ""

# Check command line argument
case "$1" in
    "all")
        echo "🚀 Running ALL tests (this may take several minutes)..."
        python3 manage.py test core.tests --keepdb
        ;;
    "models")
        echo "🚀 Running model tests..."
        python3 manage.py test core.tests.test_models --keepdb
        ;;
    "trust")
        echo "🚀 Running trust management tests..."
        python3 manage.py test core.trust.tests --keepdb
        ;;
    "user")
        echo "🚀 Running user management tests..."
        python3 manage.py test core.user_management.tests --keepdb
        ;;
    "integration")
        echo "🚀 Running integration tests..."
        python3 manage.py test core.tests.test_integration --keepdb
        ;;
    *)
        echo "Usage: $0 [all|models|trust|user|integration]"
        echo ""
        echo "Examples:"
        echo "  $0 all       # Run all 675+ tests"
        echo "  $0 models    # Run quick model tests (28 tests)"
        echo "  $0 trust     # Run trust management tests"
        echo "  $0 user      # Run user management tests"
        echo "  $0 integration # Run integration tests"
        echo ""
        echo "To run manually:"
        echo "  cd crisp && python3 manage.py test core.tests --keepdb"
        ;;
esac