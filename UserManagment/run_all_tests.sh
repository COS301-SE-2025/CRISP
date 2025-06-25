#!/bin/bash
# 🧪 CRISP User Management - Complete Test Runner
# This script runs all essential tests to validate the system

echo "🛡️ CRISP User Management System - Complete Test Suite"
echo "============================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        return 0
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

# Function to run test and update counters
run_test() {
    local test_name="$1"
    local command="$2"
    
    echo -e "\n${YELLOW}$test_name${NC}"
    
    if eval "$command" > /dev/null 2>&1; then
        print_status 0 "${test_name#*️⃣ }"
        ((TESTS_PASSED++))
    else
        print_status 1 "${test_name#*️⃣ }"
        ((TESTS_FAILED++))
    fi
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Run all tests
run_test "1️⃣ Django Configuration Validation" "python3 manage.py check --verbosity=0"
run_test "2️⃣ Database Migration Status" "python3 manage.py showmigrations UserManagement --verbosity=0"
run_test "3️⃣ Model Validation" "python3 manage.py shell -c 'from UserManagement.models import CustomUser, Organization, UserSession, AuthenticationLog; print(\"Models loaded successfully\")'"
run_test "4️⃣ Authentication Unit Tests" "python3 manage.py test UserManagement.tests.test_authentication --verbosity=0"
run_test "5️⃣ User Management Tests" "python3 manage.py test UserManagement.tests.test_user_management --verbosity=0"
run_test "6️⃣ Security Tests" "python3 manage.py test UserManagement.tests.test_security --verbosity=0"
run_test "7️⃣ Integration Tests" "python3 manage.py test UserManagement.tests.test_integration --verbosity=0"
run_test "8️⃣ System Configuration Tests" "python3 test_system_offline.py"
run_test "9️⃣ API Endpoint Configuration" "python3 manage.py shell -c 'from crisp_project.urls import urlpatterns; from UserManagement.urls import urlpatterns as user_urls; print(\"API endpoints configured:\", len(urlpatterns) + len(user_urls))'"
run_test "🔟 Security Middleware Check" "python3 manage.py shell -c 'from django.conf import settings; middleware = settings.MIDDLEWARE; security_middleware = [m for m in middleware if \"security\" in m.lower() or \"csrf\" in m.lower()]; print(\"Security middleware:\", len(security_middleware)); exit(0 if len(security_middleware) >= 2 else 1)'"

# Final Summary
echo -e "\n${YELLOW}============================================================${NC}"
echo -e "${YELLOW}📊 Test Summary${NC}"
echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
    echo -e "${YELLOW}📈 Success Rate: $SUCCESS_RATE%${NC}"
fi

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! System is fully operational.${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed. Check the output above for details.${NC}"
    exit 1
fi