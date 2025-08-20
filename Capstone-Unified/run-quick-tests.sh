#!/bin/bash

# CRISP Trust Management Platform - Quick Test Runner
# Runs essential tests quickly for development workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "========================================"
echo "    CRISP QUICK TEST SUITE"
echo "========================================"

START_TIME=$(date +%s)

# 1. Backend Critical Tests
print_status "Running critical backend tests..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "env/bin/activate" ]; then
    source env/bin/activate
fi

python3 manage.py test core.tests.test_repository core.tests.test_utils core.user_management.tests --verbosity=1 --keepdb
BACKEND_RESULT=$?

# 2. Frontend Unit Tests
print_status "Running frontend unit tests..."
cd crisp-react
npm run test -- --run --reporter=basic
FRONTEND_RESULT=$?
cd ..

# Calculate total time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "========================================"
echo "       QUICK TEST SUMMARY"
echo "========================================"

TOTAL_RESULT=$((BACKEND_RESULT + FRONTEND_RESULT))

if [ $BACKEND_RESULT -eq 0 ]; then
    print_success "✓ Backend Critical Tests: PASSED"
else
    print_error "✗ Backend Critical Tests: FAILED"
fi

if [ $FRONTEND_RESULT -eq 0 ]; then
    print_success "✓ Frontend Unit Tests: PASSED"
else
    print_error "✗ Frontend Unit Tests: FAILED"
fi

echo "Duration: ${DURATION}s"

if [ $TOTAL_RESULT -eq 0 ]; then
    print_success "🚀 Quick tests passed! Safe to continue development."
else
    print_error "❌ Quick tests failed! Fix issues before continuing."
fi

exit $TOTAL_RESULT