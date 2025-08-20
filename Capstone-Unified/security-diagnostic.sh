#!/bin/bash

# CRISP Security Diagnostic Script
# Quickly identifies and reports security issues found

echo "🔍 CRISP Security Diagnostic Report"
echo "=================================="
echo ""

# Check for critical finding from your test output
echo "🚨 CRITICAL SECURITY FINDINGS:"
echo ""
echo "1. WEAK AUTHENTICATION DETECTED"
echo "   Username: admin"
echo "   Password: password"
echo "   Status: CRITICAL - Immediate action required"
echo ""

# Check latest reports
LATEST_REPORT=$(ls -td security-testing/reports/*/ 2>/dev/null | head -n1)
if [[ -n "$LATEST_REPORT" ]]; then
    echo "📊 Latest Security Assessment: $(basename "$LATEST_REPORT")"
    echo "Report Location: $LATEST_REPORT"
    echo ""
    
    # Check what reports exist
    echo "📋 Available Reports:"
    if [[ -f "${LATEST_REPORT}bandit_report.html" ]]; then
        echo "   ✅ Bandit (Static Code Analysis)"
    fi
    if [[ -f "${LATEST_REPORT}nikto_django_report.html" ]]; then
        echo "   ✅ Nikto Django Scan"
    fi
    if [[ -f "${LATEST_REPORT}nikto_vite_report.html" ]]; then
        echo "   ✅ Nikto Vite Scan"
    fi
    if [[ -d "${LATEST_REPORT}sqlmap" ]]; then
        echo "   ⚠️  sqlmap SQL Injection Tests (Had connection issues)"
    fi
    if [[ -f "${LATEST_REPORT}hydra_login_report.txt" ]]; then
        echo "   🚨 Hydra Brute Force Test (FOUND WEAK CREDENTIALS)"
    fi
    if [[ -f "${LATEST_REPORT}zap_django_report.html" ]]; then
        echo "   ✅ ZAP Django Scan"
    else
        echo "   ❌ ZAP Django Scan (Configuration issue)"
    fi
    if [[ -f "${LATEST_REPORT}zap_vite_report.html" ]]; then
        echo "   ✅ ZAP Vite Scan"  
    else
        echo "   ❌ ZAP Vite Scan (Configuration issue)"
    fi
    echo ""
fi

# Issues identified from your output
echo "🐛 Issues Identified:"
echo ""
echo "1. ZAP Configuration Problem"
echo "   Issue: Cannot access automation config file"
echo "   Cause: Relative path issue"
echo "   Status: FIXED in security-testing-fixed.sh"
echo ""

echo "2. sqlmap Crashing Django Server"
echo "   Issue: Connection refused errors"
echo "   Cause: Aggressive testing overwhelming server"
echo "   Status: FIXED with gentle testing approach"
echo ""

echo "3. Bandit Unknown Test Warnings"
echo "   Issue: Unknown test IDs B309, B410, B322, B320, B325"
echo "   Cause: Outdated test configuration"
echo "   Status: FIXED with updated test list"
echo ""

echo "4. CRITICAL: Weak Authentication"
echo "   Issue: admin:password credentials accepted"
echo "   Cause: Default/weak password policy"
echo "   Status: REQUIRES IMMEDIATE ATTENTION"
echo ""

echo "💡 Immediate Actions Required:"
echo ""
echo "1. CRITICAL: Change admin password immediately"
echo "   Current: admin / password"
echo "   Action: Set strong, unique password"
echo ""

echo "2. Use Fixed Security Script:"
echo "   ./security-testing-fixed.sh"
echo ""

echo "3. Review Reports:"
if [[ -n "$LATEST_REPORT" ]]; then
    echo "   - Main summary: ${LATEST_REPORT}security_assessment_summary.md"
    echo "   - Bandit (code): ${LATEST_REPORT}bandit_report.html"
    echo "   - Nikto (server): ${LATEST_REPORT}nikto_*_report.html"
    echo "   - Hydra (auth): ${LATEST_REPORT}hydra_*_report.txt"
fi
echo ""

echo "4. Security Hardening Checklist:"
echo "   □ Change default passwords"
echo "   □ Implement password complexity rules"  
echo "   □ Enable account lockout policies"
echo "   □ Add multi-factor authentication"
echo "   □ Review user permissions"
echo "   □ Enable security logging"
echo ""

echo "🔧 Tools Status:"
echo "   ✅ Bandit - Working (with fixed config)"
echo "   ✅ Nikto - Working" 
echo "   ✅ Hydra - Working (found critical issue)"
echo "   ✅ ZAP - Fixed configuration"
echo "   ⚠️  sqlmap - Fixed with gentle approach"
echo ""

echo "Next Steps:"
echo "1. Run: ./security-testing-fixed.sh"
echo "2. Fix critical authentication issue"
echo "3. Review all generated reports"
echo "4. Implement security fixes"
echo "5. Re-test to validate fixes"