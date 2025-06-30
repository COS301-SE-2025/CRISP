#!/bin/bash
# 🧪 CRISP User Management - Enhanced Test Runner with Coverage
# This script runs all tests with detailed output and coverage analysis

echo "🛡️ CRISP User Management System - Enhanced Test Suite"
echo "============================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS_RUN=0
TOTAL_TESTS_PASSED=0
TOTAL_TESTS_FAILED=0
TOTAL_TESTS_SKIPPED=0
TOTAL_TESTS_ERRORS=0
SUITES_PASSED=0
SUITES_FAILED=0

# Function to print section header
print_section() {
    echo -e "\n${BOLD}${CYAN}$1${NC}"
    echo -e "${CYAN}$(printf '=%.0s' {1..60})${NC}"
}

# Function to print test file header
print_test_header() {
    echo -e "\n${BOLD}${YELLOW}📋 Running: $1${NC}"
    echo -e "${YELLOW}$(printf '-%.0s' {1..50})${NC}"
}

# Function to parse Django test output and extract statistics
parse_test_output() {
    local output="$1"
    local suite_name="$2"
    
    # Extract test counts from Django output
    local ran_line=$(echo "$output" | grep -E "^Ran [0-9]+ test")
    local tests_run=$(echo "$ran_line" | grep -oE '[0-9]+' | head -1)
    
    # Extract result line (OK, FAILED, etc.)
    local result_line=$(echo "$output" | tail -n 5 | grep -E "(OK|FAILED)")
    
    # Parse failures, errors, skipped
    local failures=$(echo "$result_line" | grep -oE 'failures=[0-9]+' | grep -oE '[0-9]+' || echo "0")
    local errors=$(echo "$result_line" | grep -oE 'errors=[0-9]+' | grep -oE '[0-9]+' || echo "0")
    local skipped=$(echo "$result_line" | grep -oE 'skipped=[0-9]+' | grep -oE '[0-9]+' || echo "0")
    
    # Default values if not found
    tests_run=${tests_run:-0}
    failures=${failures:-0}
    errors=${errors:-0}
    skipped=${skipped:-0}
    
    # Calculate passed tests
    local passed=$((tests_run - failures - errors - skipped))
    
    # Update totals
    TOTAL_TESTS_RUN=$((TOTAL_TESTS_RUN + tests_run))
    TOTAL_TESTS_PASSED=$((TOTAL_TESTS_PASSED + passed))
    TOTAL_TESTS_FAILED=$((TOTAL_TESTS_FAILED + failures))
    TOTAL_TESTS_ERRORS=$((TOTAL_TESTS_ERRORS + errors))
    TOTAL_TESTS_SKIPPED=$((TOTAL_TESTS_SKIPPED + skipped))
    
    # Print suite results
    echo -e "${BOLD}📊 Results for ${suite_name}:${NC}"
    echo -e "   Tests Run: ${BLUE}${tests_run}${NC}"
    echo -e "   Passed: ${GREEN}${passed}${NC}"
    echo -e "   Failed: ${RED}${failures}${NC}"
    echo -e "   Errors: ${RED}${errors}${NC}"
    echo -e "   Skipped: ${YELLOW}${skipped}${NC}"
    
    # Determine if suite passed
    if [ $failures -eq 0 ] && [ $errors -eq 0 ] && [ $tests_run -gt 0 ]; then
        echo -e "   Status: ${GREEN}✅ PASSED${NC}"
        ((SUITES_PASSED++))
        return 0
    elif [ $tests_run -eq 0 ]; then
        echo -e "   Status: ${YELLOW}⚠️  NO TESTS FOUND${NC}"
        return 2
    else
        echo -e "   Status: ${RED}❌ FAILED${NC}"
        ((SUITES_FAILED++))
        return 1
    fi
}

# Function to run Django test suite
run_django_test_suite() {
    local test_path="$1"
    local suite_name="$2"
    local show_output="${3:-false}"
    
    print_test_header "$suite_name"
    
    # Create temporary file for output
    local temp_output=$(mktemp)
    
    # Run the test with verbosity 2 for detailed output
    if python3 manage.py test "$test_path" --verbosity=2 > "$temp_output" 2>&1; then
        local exit_code=0
    else
        local exit_code=$?
    fi
    
    # Read the output
    local output=$(cat "$temp_output")
    
    # Show output if requested or if there were failures
    if [ "$show_output" = "true" ] || [ $exit_code -ne 0 ]; then
        echo -e "${CYAN}Output:${NC}"
        echo "$output"
    fi
    
    # Parse and display results
    parse_test_output "$output" "$suite_name"
    local parse_result=$?
    
    # Clean up
    rm -f "$temp_output"
    
    return $parse_result
}

# Function to run system validation
run_system_validation() {
    print_section "🔧 SYSTEM VALIDATION"
    
    echo -e "${YELLOW}Checking Django configuration...${NC}"
    if python3 manage.py check --verbosity=1; then
        echo -e "${GREEN}✅ Django configuration valid${NC}"
    else
        echo -e "${RED}❌ Django configuration issues found${NC}"
        return 1
    fi
    
    echo -e "\n${YELLOW}Checking database migrations...${NC}"
    python3 manage.py showmigrations UserManagement
    
    echo -e "\n${YELLOW}Validating models...${NC}"
    if python3 manage.py shell -c "
from UserManagement.models import CustomUser, Organization, UserSession, AuthenticationLog
print('✅ All models imported successfully')
print('CustomUser model:', CustomUser._meta.verbose_name)
print('Organization model:', Organization._meta.verbose_name)
print('UserSession model:', UserSession._meta.verbose_name)
print('AuthenticationLog model:', AuthenticationLog._meta.verbose_name)
"; then
        echo -e "${GREEN}✅ Models validation passed${NC}"
    else
        echo -e "${RED}❌ Models validation failed${NC}"
        return 1
    fi
}

# Function to run coverage analysis
run_coverage_analysis() {
    print_section "📈 COVERAGE ANALYSIS"
    
    echo -e "${YELLOW}Installing coverage if not present...${NC}"
    pip3 install coverage > /dev/null 2>&1
    
    echo -e "${YELLOW}Running tests with coverage...${NC}"
    coverage run --source='UserManagement' --omit='*/migrations/*,*/tests/*,*/venv/*' manage.py test UserManagement --verbosity=0
    
    echo -e "\n${BOLD}📊 Coverage Report:${NC}"
    coverage report --show-missing
    
    echo -e "\n${YELLOW}Generating HTML coverage report...${NC}"
    coverage html
    echo -e "${GREEN}✅ HTML coverage report generated in htmlcov/ directory${NC}"
    
    # Get overall coverage percentage
    local coverage_percent=$(coverage report | tail -1 | grep -oE '[0-9]+%' | tail -1)
    echo -e "${BOLD}Overall Coverage: ${coverage_percent}${NC}"
}

# Main execution starts here
print_section "🚀 STARTING ENHANCED TEST SUITE"

# System validation first
if ! run_system_validation; then
    echo -e "${RED}❌ System validation failed. Aborting test suite.${NC}"
    exit 1
fi

print_section "🧪 RUNNING TEST SUITES"

# Define test suites to run
declare -a test_suites=(
    "UserManagement.tests.test_authentication|Authentication Tests"
    "UserManagement.tests.test_user_management|User Management Tests"
    "UserManagement.tests.test_admin_views|Admin Views Tests"
    "UserManagement.tests.test_security|Security Tests"
    "UserManagement.tests.test_integration|Integration Tests"
    "UserManagement.tests.test_coverage_completion|Coverage Completion Tests"
    "UserManagement.tests.test_simple_coverage|Simple Coverage Tests"
)

# Run each test suite
for suite in "${test_suites[@]}"; do
    IFS='|' read -r test_path suite_name <<< "$suite"
    run_django_test_suite "$test_path" "$suite_name" "false"
done

# Run coverage analysis
run_coverage_analysis

# Additional system tests if they exist
print_section "🔍 ADDITIONAL SYSTEM TESTS"

if [ -f "test_api.py" ]; then
    echo -e "${YELLOW}Running API tests...${NC}"
    python3 test_api.py
fi

if [ -f "basic_system_test.py" ]; then
    echo -e "${YELLOW}Running basic system tests...${NC}"
    python3 basic_system_test.py
fi

if [ -f "test_admin_functionality.py" ]; then
    echo -e "${YELLOW}Running admin functionality tests...${NC}"
    python3 test_admin_functionality.py
fi

# Final comprehensive summary
print_section "📊 COMPREHENSIVE TEST SUMMARY"

echo -e "${BOLD}Test Suite Results:${NC}"
echo -e "   Total Suites Run: ${BLUE}$((SUITES_PASSED + SUITES_FAILED))${NC}"
echo -e "   Suites Passed: ${GREEN}${SUITES_PASSED}${NC}"
echo -e "   Suites Failed: ${RED}${SUITES_FAILED}${NC}"

echo -e "\n${BOLD}Individual Test Results:${NC}"
echo -e "   Total Tests Run: ${BLUE}${TOTAL_TESTS_RUN}${NC}"
echo -e "   Tests Passed: ${GREEN}${TOTAL_TESTS_PASSED}${NC}"
echo -e "   Tests Failed: ${RED}${TOTAL_TESTS_FAILED}${NC}"
echo -e "   Tests with Errors: ${RED}${TOTAL_TESTS_ERRORS}${NC}"
echo -e "   Tests Skipped: ${YELLOW}${TOTAL_TESTS_SKIPPED}${NC}"

# Calculate success rates
if [ $TOTAL_TESTS_RUN -gt 0 ]; then
    test_success_rate=$((TOTAL_TESTS_PASSED * 100 / TOTAL_TESTS_RUN))
    echo -e "   Test Success Rate: ${CYAN}${test_success_rate}%${NC}"
fi

if [ $((SUITES_PASSED + SUITES_FAILED)) -gt 0 ]; then
    suite_success_rate=$((SUITES_PASSED * 100 / (SUITES_PASSED + SUITES_FAILED)))
    echo -e "   Suite Success Rate: ${CYAN}${suite_success_rate}%${NC}"
fi

# Final status
echo -e "\n${BOLD}============================================================${NC}"
if [ $SUITES_FAILED -eq 0 ] && [ $TOTAL_TESTS_FAILED -eq 0 ] && [ $TOTAL_TESTS_ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! System is fully operational.${NC}"
    echo -e "${GREEN}✅ Ready for production deployment.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed or had errors.${NC}"
    echo -e "${YELLOW}📋 Review the detailed output above for specific issues.${NC}"
    echo -e "${YELLOW}🔍 Check the HTML coverage report in htmlcov/ for coverage details.${NC}"
    exit 1
fi