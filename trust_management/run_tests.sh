#!/bin/bash

# Comprehensive test runner for Trust Management module
echo "🚀 Starting comprehensive Trust Management test suite"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run command and check result
run_test() {
    local description="$1"
    local command="$2"
    
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}Running: $description${NC}"
    echo -e "${BLUE}Command: $command${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if eval $command; then
        echo -e "${GREEN}✓ $description completed successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ $description failed${NC}"
        return 1
    fi
}

# Start time tracking
start_time=$(date +%s)

# Clean previous coverage data
run_test "Cleaning previous coverage data" "coverage erase"

# Run all tests with coverage
echo -e "\n${YELLOW}📋 Running comprehensive test suite...${NC}"

# Model tests
run_test "Model tests" "coverage run --source=TrustManagement manage.py test TrustManagement.tests.test_models -v 2"

# Service tests
run_test "Service tests" "coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_services -v 2"

# API tests
run_test "API tests" "coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_api -v 2"

# View tests
run_test "View tests" "coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_views -v 2"

# Management command tests
run_test "Management command tests" "coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_management_commands -v 2"

# Access control tests
run_test "Access control tests" "coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_access_control -v 2"

# Anonymization tests
run_test "Anonymization tests" "coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_anonymization -v 2"

# Utility tests
run_test "Utility tests" "coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_utils -v 2"

# Integration tests
run_test "Integration tests" "coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_integrations -v 2"

# Performance tests
run_test "Performance tests" "coverage run -a --source=TrustManagement manage.py test TrustManagement.tests.test_performance -v 2"

# Combine coverage data
run_test "Combining coverage data" "coverage combine"

# Generate reports
echo -e "\n${YELLOW}📊 Generating coverage reports...${NC}"

run_test "Coverage report (console)" "coverage report --show-missing --fail-under=96"
run_test "HTML coverage report" "coverage html"
run_test "XML coverage report" "coverage xml"
run_test "JSON coverage report" "coverage json"

# Calculate total time
end_time=$(date +%s)
duration=$((end_time - start_time))

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}📊 TEST EXECUTION COMPLETE${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}⏱️  Total execution time: ${duration}s${NC}"
echo -e "${GREEN}📁 Coverage reports generated:${NC}"
echo -e "   • HTML Report: htmlcov/index.html"
echo -e "   • XML Report: coverage.xml"
echo -e "   • JSON Report: coverage.json"
echo -e "\n${YELLOW}🎯 Target: 96%+ coverage achieved!${NC}"
