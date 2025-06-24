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
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${YELLOW}1️⃣ Django Configuration Validation${NC}"
python3 manage.py check --verbosity=0
print_status $? "Django Configuration Check"
[ $? -eq 0 ] && ((TESTS_PASSED++)) || ((TESTS_FAILED++))

echo -e "\n${YELLOW}2️⃣ Database Migration Status${NC}"
python3 manage.py showmigrations UserManagement --verbosity=0
print_status $? "Database Migration Status"
[ $? -eq 0 ] && ((TESTS_PASSED++)) || ((TESTS_FAILED++))

echo -e "\n${YELLOW}3️⃣ Model Validation${NC}"
python3 manage.py shell -c "
from UserManagement.models import CustomUser, Organization, UserSession, AuthenticationLog
print(f'✅ Models loaded successfully')
print(f'   Users: {CustomUser.objects.count()}')
print(f'   Organizations: {Organization.objects.count()}')
print(f'   Sessions: {UserSession.objects.count()}')
print(f'   Auth Logs: {AuthenticationLog.objects.count()}')
" 2>/dev/null
print_status $? "Model Validation"
[ $? -eq 0 ] && ((TESTS_PASSED++)) || ((TESTS_FAILED++))

echo -e "\n${YELLOW}4️⃣ Authentication Unit Tests${NC}"
python3 manage.py test UserManagement.tests.test_authentication --verbosity=0
print_status $? "Authentication Unit Tests"
[ $? -eq 0 ] && ((TESTS_PASSED++)) || ((TESTS_FAILED++))

echo -e "\n${YELLOW}5️⃣ User Management Tests${NC}"
python3 manage.py test UserManagement.tests.test_user_management --verbosity=0
print_status $? "User Management Tests"
[ $? -eq 0 ] && ((TESTS_PASSED++)) || ((TESTS_FAILED++))

echo -e "\n${YELLOW}6️⃣ Security Tests${NC}"
python3 manage.py test UserManagement.tests.test_security --verbosity=0
print_status $? "Security Tests"
[ $? -eq 0 ] && ((TESTS_PASSED++)) || ((TESTS_FAILED++))

echo -e "\n${YELLOW}7️⃣ Integration Tests${NC}"
python3 manage.py test UserManagement.tests.test_integration --verbosity=0
print_status $? "Integration Tests"
[ $? -eq 0 ] && ((TESTS_PASSED++)) || ((TESTS_FAILED++))

echo -e "\n${YELLOW}8️⃣ API Authentication Flow${NC}"
python3 test_system.py > /dev/null 2>&1
print_status $? "API Authentication Flow"
[ $? -eq 0 ] && ((TESTS_PASSED++)) || ((TESTS_FAILED++))

echo -e "\n${YELLOW}9️⃣ Admin Interface Accessibility${NC}"
curl -I http://127.0.0.1:8000/admin/ > /dev/null 2>&1
print_status $? "Admin Interface Accessibility"
[ $? -eq 0 ] && ((TESTS_PASSED++)) || ((TESTS_FAILED++))

echo -e "\n${YELLOW}🔟 Security Headers Validation${NC}"
HEADERS=$(curl -I http://127.0.0.1:8000/api/auth/login/ 2>/dev/null | grep -E "(X-XSS-Protection|X-Content-Type-Options|X-Frame-Options)" | wc -l)
if [ $HEADERS -ge 3 ]; then
    print_status 0 "Security Headers Validation"
    ((TESTS_PASSED++))
else
    print_status 1 "Security Headers Validation"
    ((TESTS_FAILED++))
fi

# Final Summary
echo -e "\n${YELLOW}============================================================${NC}"
echo -e "${YELLOW}📊 Test Summary${NC}"
echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))

echo -e "${YELLOW}📈 Success Rate: $SUCCESS_RATE%${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! System is fully operational.${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed. Check the output above for details.${NC}"
    exit 1
fi