#!/bin/bash

# CRISP Trust Management Platform - Complete Test Suite Runner
# This script runs all tests across the entire system: backend, frontend, integration, and E2E

set -e

# Colors for output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Parse command line arguments
SKIP_BACKEND=false
SKIP_FRONTEND=false
SKIP_E2E=false
VERBOSE=false
PARALLEL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --skip-e2e)
            SKIP_E2E=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-backend    Skip Django backend tests"
            echo "  --skip-frontend   Skip React frontend tests"
            echo "  --skip-e2e        Skip end-to-end tests"
            echo "  --verbose         Show detailed output"
            echo "  --parallel        Run tests in parallel where possible"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "    CRISP PLATFORM TEST SUITE"
echo "========================================"
echo "Running comprehensive test suite for:"
echo "• Django Backend API"
echo "• React Frontend Components"
echo "• Integration Tests"
echo "• End-to-End User Flows"
echo "========================================"

# Store test results
BACKEND_RESULT=0
FRONTEND_RESULT=0
INTEGRATION_RESULT=0
E2E_RESULT=0

# Start time
START_TIME=$(date +%s)

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists python3; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is required but not installed"
    exit 1
fi

print_success "Prerequisites check passed"

# 1. BACKEND TESTS
if [ "$SKIP_BACKEND" = false ]; then
    print_status "======== RUNNING BACKEND TESTS ========"
    
    # Check if virtual environment exists
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_status "Activated virtual environment"
    elif [ -f "env/bin/activate" ]; then
        source env/bin/activate  
        print_status "Activated virtual environment"
    else
        print_warning "No virtual environment found, using system Python"
    fi
    
    # Install backend dependencies if needed
    if [ ! -f "requirements.txt" ] || [ "requirements.txt" -nt "installed.flag" ]; then
        print_status "Installing/updating backend dependencies..."
        pip install -r requirements.txt
        touch installed.flag
    fi
    
    # Run Django backend tests
    print_status "Running Django backend test orchestrator..."
    
    if [ "$VERBOSE" = true ]; then
        cd ../.. && python3 manage.py run_orchestrated_tests --verbosity=2
    else
        cd ../.. && python3 manage.py run_orchestrated_tests
    fi
    
    BACKEND_RESULT=$?
    
    if [ $BACKEND_RESULT -eq 0 ]; then
        print_success "Backend tests passed"
    else
        print_error "Backend tests failed"
    fi
fi

# 2. FRONTEND TESTS  
if [ "$SKIP_FRONTEND" = false ]; then
    print_status "======== RUNNING FRONTEND TESTS ========"
    
    cd ../../frontend/crisp-react
    
    # Install frontend dependencies
    if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Run unit tests
    print_status "Running React component unit tests..."
    if [ "$VERBOSE" = true ]; then
        npm run test -- --reporter=verbose
    else
        npm run test
    fi
    UNIT_RESULT=$?
    
    # Run integration tests
    print_status "Running frontend integration tests..."
    npm run test:integration
    INTEGRATION_RESULT=$?
    
    FRONTEND_RESULT=$((UNIT_RESULT + INTEGRATION_RESULT))
    
    if [ $FRONTEND_RESULT -eq 0 ]; then
        print_success "Frontend tests passed"
    else
        print_error "Frontend tests failed"
    fi
    
    cd ..
fi

# 3. END-TO-END TESTS
if [ "$SKIP_E2E" = false ]; then
    print_status "======== RUNNING END-TO-END TESTS ========"
    
    cd ../../frontend/crisp-react
    
    # Install Playwright browsers if needed
    if [ ! -d "~/.cache/ms-playwright" ]; then
        print_status "Installing Playwright browsers..."
        npm run playwright:install
    fi
    
    # Start the development server in background
    print_status "Starting development server for E2E tests..."
    npm run dev > /dev/null 2>&1 &
    DEV_SERVER_PID=$!
    
    # Wait for server to start
    print_status "Waiting for development server to start..."
    sleep 10
    
    # Check if server is running
    if curl -f http://localhost:5173 > /dev/null 2>&1; then
        print_success "Development server is running"
        
        # Run E2E tests
        print_status "Running end-to-end tests..."
        if [ "$VERBOSE" = true ]; then
            npm run test:e2e -- --reporter=line
        else
            npm run test:e2e
        fi
        E2E_RESULT=$?
        
        if [ $E2E_RESULT -eq 0 ]; then
            print_success "End-to-end tests passed"
        else
            print_error "End-to-end tests failed"
        fi
    else
        print_error "Failed to start development server"
        E2E_RESULT=1
    fi
    
    # Kill development server
    kill $DEV_SERVER_PID > /dev/null 2>&1 || true
    
    cd ..
fi

# Calculate total time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "========================================"
echo "         TEST SUITE SUMMARY"
echo "========================================"

if [ "$SKIP_BACKEND" = false ]; then
    if [ $BACKEND_RESULT -eq 0 ]; then
        print_success "✓ Backend Tests: PASSED"
    else
        print_error "✗ Backend Tests: FAILED"
    fi
fi

if [ "$SKIP_FRONTEND" = false ]; then
    if [ $FRONTEND_RESULT -eq 0 ]; then
        print_success "✓ Frontend Tests: PASSED"
    else
        print_error "✗ Frontend Tests: FAILED"
    fi
fi

if [ "$SKIP_E2E" = false ]; then
    if [ $E2E_RESULT -eq 0 ]; then
        print_success "✓ End-to-End Tests: PASSED"
    else
        print_error "✗ End-to-End Tests: FAILED"
    fi
fi

echo "========================================"
echo "Total Duration: ${DURATION}s"

# Calculate final result
TOTAL_RESULT=$((BACKEND_RESULT + FRONTEND_RESULT + E2E_RESULT))

if [ $TOTAL_RESULT -eq 0 ]; then
    print_success "🎉 ALL TESTS PASSED! System is ready for deployment."
    echo ""
    echo "✓ Backend API functionality verified"
    echo "✓ Frontend components tested"
    echo "✓ Integration between systems validated"
    echo "✓ End-to-end user workflows confirmed"
    echo ""
    echo "The CRISP Trust Management Platform is ready for production!"
else
    print_error "❌ SOME TESTS FAILED! Review the output above."
    echo ""
    echo "Please fix the failing tests before deployment."
fi

exit $TOTAL_RESULT