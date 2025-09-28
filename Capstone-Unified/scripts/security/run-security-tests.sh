#!/bin/bash

# CRISP Automated Security Testing Script
# Runs comprehensive security tests against local Django + Vite application

set -e

# Configuration
DJANGO_URL="http://127.0.0.1:8000"
VITE_URL="http://127.0.0.1:5173"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_DIR="security-testing/reports/${TIMESTAMP}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Create report directory
mkdir -p "$REPORT_DIR"

print_status "Starting CRISP Security Assessment - ${TIMESTAMP}"
print_warning "Ensure your Django server is running on ${DJANGO_URL}"
print_warning "Ensure your Vite frontend is running on ${VITE_URL}"

# Function to check if service is running
check_service() {
    local url=$1
    local name=$2
    
    print_status "Checking if $name is running on $url..."
    if curl -s --connect-timeout 5 "$url" >/dev/null 2>&1; then
        print_success "$name is running"
        return 0
    else
        print_error "$name is not running on $url"
        return 1
    fi
}

# Function to run Bandit static analysis
run_bandit() {
    print_status "Running Bandit static code analysis..."
    
    # Create bandit config
    cat > security-testing/configs/bandit.yaml << 'EOF'
tests: [B101, B102, B103, B104, B105, B106, B107, B108, B110, B112, B201, B301, B302, B303, B304, B305, B306, B307, B308, B310, B311, B312, B313, B314, B315, B316, B317, B318, B319, B321, B323, B324, B401, B402, B403, B404, B405, B406, B407, B408, B409, B411, B412, B413, B501, B502, B503, B504, B505, B506, B507, B601, B602, B603, B604, B605, B606, B607, B608, B609, B610, B611, B701, B702, B703]
skips: []
EOF

    bandit -r ./core ./crisp_unified -f json -o "${REPORT_DIR}/bandit_report.json" -c security-testing/configs/bandit.yaml || true
    bandit -r ./core ./crisp_unified -f html -o "${REPORT_DIR}/bandit_report.html" -c security-testing/configs/bandit.yaml || true
    bandit -r ./core ./crisp_unified -f txt -o "${REPORT_DIR}/bandit_report.txt" -c security-testing/configs/bandit.yaml || true
    
    print_success "Bandit analysis completed. Reports saved to ${REPORT_DIR}/"
}

# Function to run Nikto web server scanner
run_nikto() {
    local url=$1
    local name=$2
    
    print_status "Running Nikto scan against $name ($url)..."
    
    nikto -h "$url" -output "${REPORT_DIR}/nikto_${name}_report.html" -Format html || true
    nikto -h "$url" -output "${REPORT_DIR}/nikto_${name}_report.txt" -Format txt || true
    
    print_success "Nikto scan against $name completed"
}

# Function to run OWASP ZAP scan
run_zap_scan() {
    local url=$1
    local name=$2
    
    print_status "Running OWASP ZAP scan against $name ($url)..."
    
    # Create ZAP automation config
    mkdir -p "${REPORT_DIR}"
    cat > "${REPORT_DIR}/zap_automation_${name}.yaml" << EOF
---
env:
  contexts:
    - name: "CRISP_${name}"
      urls:
        - "${url}"
      includePaths:
        - "${url}/.*"
      excludePaths: []
  parameters:
    failOnError: true
    failOnWarning: false
    progressToStdout: true

jobs:
  - type: spider
    parameters:
      context: "CRISP_${name}"
      url: "${url}"
      maxDuration: 2
      maxDepth: 5
      numberOfThreads: 5
      
  - type: activeScan
    parameters:
      context: "CRISP_${name}"
      policy: "Default Policy"
      maxRuleDurationInMins: 1
      maxScanDurationInMins: 10
      
  - type: report
    parameters:
      template: "traditional-html"
      reportDir: "${REPORT_DIR}"
      reportFile: "zap_${name}_report.html"
      
  - type: report
    parameters:
      template: "traditional-json"
      reportDir: "${REPORT_DIR}"
      reportFile: "zap_${name}_report.json"
EOF

    # Run ZAP in automation mode
    ~/.local/bin/zap.sh -cmd -autorun "${REPORT_DIR}/zap_automation_${name}.yaml" || true
    
    print_success "ZAP scan against $name completed"
}

# Function to run sqlmap tests
run_sqlmap() {
    print_status "Running sqlmap SQL injection tests..."
    
    # Test common endpoints
    local endpoints=(
        "${DJANGO_URL}/api/auth/login/"
        "${DJANGO_URL}/api/users/"
        "${DJANGO_URL}/api/organizations/"
        "${DJANGO_URL}/api/threat-feeds/"
        "${DJANGO_URL}/api/indicators/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        print_status "Testing endpoint: $endpoint"
        
        # Test GET parameters (gentler approach)
        sqlmap -u "$endpoint?id=1" \
            --batch \
            --level=1 \
            --risk=1 \
            --timeout=5 \
            --retries=1 \
            --delay=2 \
            --threads=1 \
            --technique=B \
            --output-dir="${REPORT_DIR}/sqlmap" \
            --flush-session \
            --fresh-queries || true
            
        # Test POST data (basic test)
        sqlmap -u "$endpoint" \
            --data="username=test&password=test" \
            --batch \
            --level=1 \
            --risk=1 \
            --timeout=5 \
            --retries=1 \
            --delay=2 \
            --threads=1 \
            --technique=B \
            --output-dir="${REPORT_DIR}/sqlmap" \
            --flush-session \
            --fresh-queries || true
    done
    
    print_success "sqlmap testing completed"
}

# Function to run Hydra brute force tests
run_hydra() {
    print_status "Running Hydra brute force tests..."
    
    # Test login endpoint
    print_status "Testing Django login endpoint..."
    hydra -L security-testing/wordlists/common_usernames.txt \
          -P security-testing/wordlists/common_passwords.txt \
          -s 8000 \
          -f \
          -t 4 \
          -w 3 \
          127.0.0.1 \
          http-post-form "/api/auth/login/:username=^USER^&password=^PASS^:Invalid credentials" \
          -o "${REPORT_DIR}/hydra_login_report.txt" || true
    
    # Test admin endpoint if exists
    print_status "Testing Django admin endpoint..."
    hydra -L security-testing/wordlists/common_usernames.txt \
          -P security-testing/wordlists/common_passwords.txt \
          -s 8000 \
          -f \
          -t 4 \
          -w 3 \
          127.0.0.1 \
          http-post-form "/admin/login/:username=^USER^&password=^PASS^:Please enter the correct" \
          -o "${REPORT_DIR}/hydra_admin_report.txt" || true
    
    print_success "Hydra brute force testing completed"
}

# Function to generate summary report
generate_summary() {
    print_status "Generating security assessment summary..."
    
    cat > "${REPORT_DIR}/security_assessment_summary.md" << EOF
# CRISP Security Assessment Summary

**Date:** $(date)
**Target Applications:**
- Django Backend: ${DJANGO_URL}
- Vite Frontend: ${VITE_URL}

## Tests Performed

### 1. Static Code Analysis (Bandit)
- **Purpose:** Identify insecure code patterns in Django codebase
- **Files Analyzed:** Core Django application files
- **Report:** bandit_report.html, bandit_report.json, bandit_report.txt

### 2. Web Server Vulnerability Scanning (Nikto)
- **Purpose:** Scan for misconfigurations and known vulnerabilities
- **Targets:** Both Django and Vite servers
- **Reports:** nikto_django_report.html, nikto_vite_report.html

### 3. Web Application Security Testing (OWASP ZAP)
- **Purpose:** Comprehensive web application security testing
- **Tests:** Spider crawling, Active security scanning
- **Vulnerabilities Tested:** XSS, SQL Injection, CSRF, Security Headers
- **Reports:** zap_django_report.html, zap_vite_report.html

### 4. SQL Injection Testing (sqlmap)
- **Purpose:** Automated SQL injection vulnerability detection
- **Endpoints Tested:** API authentication and data endpoints
- **Report Directory:** sqlmap/

### 5. Brute Force Testing (Hydra)
- **Purpose:** Test authentication mechanisms against brute force attacks
- **Targets:** Login endpoints and admin interfaces
- **Reports:** hydra_login_report.txt, hydra_admin_report.txt

## Vulnerability Categories Tested

- **Injection Attacks:** SQL injection, Command injection, LDAP injection
- **Authentication Issues:** Weak passwords, Brute force resistance
- **Session Management:** Session fixation, Session hijacking
- **Cross-Site Scripting (XSS):** Reflected, Stored, DOM-based
- **Cross-Site Request Forgery (CSRF)**
- **Security Misconfigurations:** Default credentials, Unnecessary services
- **Sensitive Data Exposure:** Unencrypted data, Information leakage
- **Broken Access Control:** Privilege escalation, Path traversal
- **Security Headers:** Missing security headers
- **Known Vulnerabilities:** CVE-based vulnerability checks

## Next Steps

1. Review all generated reports in detail
2. Prioritize vulnerabilities by severity (Critical → High → Medium → Low)
3. Create remediation plan for identified issues
4. Implement security fixes
5. Re-run tests to validate fixes
6. Consider implementing continuous security testing

## Important Notes

- All tests were performed against LOCAL development environment only
- Results should be validated manually before implementing fixes
- Some findings may be false positives - manual verification recommended
- Consider professional penetration testing for production systems

EOF

    print_success "Security assessment summary generated"
}

# Main execution
main() {
    # Check if services are running
    local django_running=false
    local vite_running=false
    
    if check_service "$DJANGO_URL" "Django Backend"; then
        django_running=true
    fi
    
    if check_service "$VITE_URL" "Vite Frontend"; then
        vite_running=true
    fi
    
    if [[ "$django_running" == false && "$vite_running" == false ]]; then
        print_error "Neither Django nor Vite is running. Please start your applications first."
        exit 1
    fi
    
    # Run static analysis (doesn't require running services)
    run_bandit
    
    # Run tests against running services
    if [[ "$django_running" == true ]]; then
        run_nikto "$DJANGO_URL" "django"
        run_zap_scan "$DJANGO_URL" "django"
        run_sqlmap
        run_hydra
    fi
    
    if [[ "$vite_running" == true ]]; then
        run_nikto "$VITE_URL" "vite"
        run_zap_scan "$VITE_URL" "vite"
    fi
    
    # Generate summary
    generate_summary
    
    print_success "Security assessment completed!"
    print_status "All reports saved to: ${REPORT_DIR}/"
    print_status "Review the security_assessment_summary.md for an overview"
    
    echo ""
    print_warning "IMPORTANT:"
    echo "1. Review all reports carefully"
    echo "2. Verify findings manually"
    echo "3. Prioritize fixes by severity"
    echo "4. Test fixes in development first"
}

# Run main function
main "$@"