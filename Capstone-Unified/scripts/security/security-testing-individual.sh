#!/bin/bash

# CRISP Individual Security Testing Script
# Run specific security tools individually with detailed configuration

set -e

DJANGO_URL="http://127.0.0.1:8000"
VITE_URL="http://127.0.0.1:5173"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

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

show_usage() {
    echo "Usage: $0 [TOOL] [OPTIONS]"
    echo ""
    echo "Available tools:"
    echo "  bandit    - Static code analysis for Python/Django"
    echo "  nikto     - Web server vulnerability scanner"
    echo "  zap       - OWASP ZAP web application security tester"
    echo "  sqlmap    - SQL injection vulnerability scanner"
    echo "  hydra     - Brute force authentication tester"
    echo "  all       - Run all tools (equivalent to run-security-tests.sh)"
    echo ""
    echo "Examples:"
    echo "  $0 bandit                    # Run Bandit static analysis"
    echo "  $0 nikto django             # Run Nikto against Django server"
    echo "  $0 zap gui                  # Launch ZAP in GUI mode"
    echo "  $0 sqlmap /api/users/       # Test specific endpoint"
    echo "  $0 hydra /admin/login/      # Brute force specific endpoint"
}

# Individual tool functions
run_bandit_detailed() {
    print_status "Running detailed Bandit static code analysis..."
    
    mkdir -p "security-testing/reports/bandit_${TIMESTAMP}"
    
    # Create detailed bandit config
    cat > security-testing/configs/bandit_detailed.yaml << 'EOF'
# Bandit detailed configuration
tests: 
  # Injection attacks
  - B101  # assert_used
  - B102  # exec_used
  - B103  # set_bad_file_permissions
  - B104  # hardcoded_bind_all_interfaces
  - B105  # hardcoded_password_string
  - B106  # hardcoded_password_funcarg
  - B107  # hardcoded_password_default
  - B108  # hardcoded_tmp_directory
  - B110  # try_except_pass
  - B112  # try_except_continue
  
  # SQL injection
  - B201  # flask_debug_true
  - B601  # paramiko_calls
  - B602  # subprocess_popen_with_shell_equals_true
  - B603  # subprocess_without_shell_equals_true
  - B604  # any_other_function_with_shell_equals_true
  - B605  # start_process_with_a_shell
  - B606  # start_process_with_no_shell
  - B607  # start_process_with_partial_path
  
  # Crypto issues
  - B301  # pickle
  - B302  # pickle_load
  - B303  # pickle_loads
  - B304  # pickle_dump
  - B305  # pickle_dumps
  - B306  # pickle_load_deprecated
  - B307  # eval
  - B308  # mark_safe
  - B309  # httplib_https_default_context
  - B310  # urllib_opener_https_handler
  - B311  # random
  - B312  # telnetlib
  - B313  # xmlrpc_method
  - B314  # xmlrpc_server
  - B315  # xmlrpc_simple_server
  - B316  # xmlrpc_simple_server_no_method
  - B317  # xmlrpc_simple_server_method
  - B318  # xml_bad_cElementTree
  - B319  # xml_bad_ElementTree
  - B320  # xml_bad_expatreader
  - B321  # xml_bad_expatbuilder
  - B322  # input
  - B323  # unverified_context
  - B324  # hashlib_insecure_functions
  - B325  # tempfile_mktemp

skips: []
EOF

    # Run comprehensive bandit scan
    bandit -r ./core ./crisp_unified \
           -f json \
           -o "security-testing/reports/bandit_${TIMESTAMP}/detailed_report.json" \
           -c security-testing/configs/bandit_detailed.yaml \
           -v || true
           
    bandit -r ./core ./crisp_unified \
           -f html \
           -o "security-testing/reports/bandit_${TIMESTAMP}/detailed_report.html" \
           -c security-testing/configs/bandit_detailed.yaml \
           -v || true
           
    # Generate CSV for spreadsheet analysis
    bandit -r ./core ./crisp_unified \
           -f csv \
           -o "security-testing/reports/bandit_${TIMESTAMP}/detailed_report.csv" \
           -c security-testing/configs/bandit_detailed.yaml || true
    
    # Scan individual critical files
    critical_files=(
        "crisp_unified/settings.py"
        "core/models/models.py"
        "core/api/auth_api.py"
        "core/services/auth_service.py"
        "core/views.py"
    )
    
    for file in "${critical_files[@]}"; do
        if [[ -f "$file" ]]; then
            print_status "Scanning critical file: $file"
            bandit "$file" \
                   -f txt \
                   -o "security-testing/reports/bandit_${TIMESTAMP}/$(basename "$file")_report.txt" || true
        fi
    done
    
    print_success "Detailed Bandit analysis completed. Reports in security-testing/reports/bandit_${TIMESTAMP}/"
}

run_nikto_detailed() {
    local target=${2:-"django"}
    local url
    
    if [[ "$target" == "django" ]]; then
        url="$DJANGO_URL"
    elif [[ "$target" == "vite" ]]; then
        url="$VITE_URL"
    else
        url="$target"  # Allow custom URL
    fi
    
    print_status "Running detailed Nikto scan against $url..."
    
    mkdir -p "security-testing/reports/nikto_${TIMESTAMP}"
    
    # Full nikto scan with all plugins
    nikto -h "$url" \
          -Plugins "@@ALL" \
          -output "security-testing/reports/nikto_${TIMESTAMP}/full_scan_$(basename "$url").html" \
          -Format html \
          -Tuning "123456789abc" || true
          
    # Specific dangerous file check
    nikto -h "$url" \
          -Plugins "paths" \
          -output "security-testing/reports/nikto_${TIMESTAMP}/paths_$(basename "$url").txt" \
          -Format txt || true
          
    # SSL/TLS specific tests (if HTTPS)
    if [[ "$url" == https* ]]; then
        nikto -h "$url" \
              -Plugins "ssl" \
              -output "security-testing/reports/nikto_${TIMESTAMP}/ssl_$(basename "$url").txt" \
              -Format txt || true
    fi
    
    print_success "Detailed Nikto scan completed. Reports in security-testing/reports/nikto_${TIMESTAMP}/"
}

run_zap_gui() {
    print_status "Launching OWASP ZAP in GUI mode..."
    print_warning "Manual steps to perform in ZAP GUI:"
    echo "1. Set target URL to $DJANGO_URL or $VITE_URL"
    echo "2. Spider the application (Sites > Right-click > Spider)"
    echo "3. Run Active Scan (Sites > Right-click > Active Scan)"
    echo "4. Generate reports (Report > Generate Report)"
    echo "5. Save session for later analysis"
    
    # Launch ZAP GUI
    zap.sh &
    
    print_status "ZAP GUI launched. Complete your testing and close when done."
}

run_zap_automated() {
    local target=${2:-"django"}
    local url
    
    if [[ "$target" == "django" ]]; then
        url="$DJANGO_URL"
    elif [[ "$target" == "vite" ]]; then
        url="$VITE_URL"
    else
        url="$target"
    fi
    
    print_status "Running automated ZAP scan against $url..."
    
    mkdir -p "security-testing/reports/zap_${TIMESTAMP}"
    
    # Create comprehensive automation config
    cat > "security-testing/reports/zap_${TIMESTAMP}/automation_config.yaml" << EOF
---
env:
  contexts:
    - name: "CRISP_Detailed"
      urls:
        - "$url"
      includePaths:
        - "$url/.*"
      excludePaths:
        - "$url/static/.*"
        - "$url/media/.*"
        - ".*logout.*"
  parameters:
    failOnError: false
    failOnWarning: false
    progressToStdout: true

jobs:
  - type: spider
    parameters:
      context: "CRISP_Detailed"
      url: "$url"
      maxDuration: 10
      maxDepth: 10
      numberOfThreads: 10
      acceptCookies: true
      parseComments: true
      parseRobotsTxt: true
      parseSVNEntries: true
      parseSitemapXml: true
      
  - type: activeScan
    parameters:
      context: "CRISP_Detailed"
      policy: "Default Policy"
      maxRuleDurationInMins: 5
      maxScanDurationInMins: 30
      threadPerHost: 2
      delayInMs: 0
      
  - type: report
    parameters:
      template: "traditional-html"
      reportDir: "security-testing/reports/zap_${TIMESTAMP}"
      reportFile: "comprehensive_report_$(basename "$url").html"
      
  - type: report
    parameters:
      template: "traditional-json"
      reportDir: "security-testing/reports/zap_${TIMESTAMP}"
      reportFile: "comprehensive_report_$(basename "$url").json"
      
  - type: report
    parameters:
      template: "traditional-xml"
      reportDir: "security-testing/reports/zap_${TIMESTAMP}"
      reportFile: "comprehensive_report_$(basename "$url").xml"
EOF

    # Run ZAP automation
    zap.sh -cmd -autorun "security-testing/reports/zap_${TIMESTAMP}/automation_config.yaml" || true
    
    print_success "Automated ZAP scan completed. Reports in security-testing/reports/zap_${TIMESTAMP}/"
}

run_sqlmap_detailed() {
    local endpoint=${2:-"/api/users/"}
    local full_url="$DJANGO_URL$endpoint"
    
    print_status "Running detailed sqlmap testing against $full_url..."
    
    mkdir -p "security-testing/reports/sqlmap_${TIMESTAMP}"
    
    # Test GET parameters
    if [[ "$endpoint" != *"?"* ]]; then
        full_url="${full_url}?id=1&search=test"
    fi
    
    print_status "Testing GET parameters..."
    sqlmap -u "$full_url" \
           --batch \
           --level=3 \
           --risk=2 \
           --timeout=15 \
           --retries=2 \
           --threads=5 \
           --technique=BEUSTQ \
           --dbms=postgresql \
           --output-dir="security-testing/reports/sqlmap_${TIMESTAMP}" \
           --flush-session \
           --fresh-queries \
           --dump-all \
           --exclude-sysdbs || true
    
    # Test POST data
    print_status "Testing POST data..."
    sqlmap -u "$DJANGO_URL$endpoint" \
           --data="username=test&password=test&email=test@test.com" \
           --batch \
           --level=3 \
           --risk=2 \
           --timeout=15 \
           --retries=2 \
           --threads=5 \
           --technique=BEUSTQ \
           --dbms=postgresql \
           --output-dir="security-testing/reports/sqlmap_${TIMESTAMP}" \
           --flush-session \
           --fresh-queries || true
    
    # Test JSON data
    print_status "Testing JSON POST data..."
    sqlmap -u "$DJANGO_URL$endpoint" \
           --data='{"username":"test*","password":"test"}' \
           --headers="Content-Type: application/json" \
           --batch \
           --level=3 \
           --risk=2 \
           --timeout=15 \
           --retries=2 \
           --threads=5 \
           --technique=BEUSTQ \
           --dbms=postgresql \
           --output-dir="security-testing/reports/sqlmap_${TIMESTAMP}" \
           --flush-session \
           --fresh-queries || true
    
    # Test with authentication
    if [[ -f "security-testing/auth_token.txt" ]]; then
        local token=$(cat security-testing/auth_token.txt)
        print_status "Testing with authentication token..."
        sqlmap -u "$full_url" \
               --headers="Authorization: Bearer $token" \
               --batch \
               --level=2 \
               --risk=1 \
               --timeout=15 \
               --retries=1 \
               --threads=3 \
               --technique=BEUSTQ \
               --dbms=postgresql \
               --output-dir="security-testing/reports/sqlmap_${TIMESTAMP}" || true
    fi
    
    print_success "Detailed sqlmap testing completed. Reports in security-testing/reports/sqlmap_${TIMESTAMP}/"
}

run_hydra_detailed() {
    local endpoint=${2:-"/api/auth/login/"}
    
    print_status "Running detailed Hydra brute force testing against $endpoint..."
    
    mkdir -p "security-testing/reports/hydra_${TIMESTAMP}"
    
    # Extended username list
    cat > "security-testing/reports/hydra_${TIMESTAMP}/usernames_extended.txt" << 'EOF'
admin
administrator
root
user
test
guest
demo
service
default
crisp
system
api
support
help
info
contact
webmaster
postmaster
mail
www
ftp
staff
manager
supervisor
operator
EOF

    # Extended password list
    cat > "security-testing/reports/hydra_${TIMESTAMP}/passwords_extended.txt" << 'EOF'
password
123456
admin
password123
crisp
default
test
guest
demo
12345
qwerty
letmein
changeme
welcome
login
pass
secret
access
temp
temporary
user
system
service
Password1
Admin123
Test123
EOF

    # Test different authentication methods
    case "$endpoint" in
        */admin/*)
            print_status "Testing Django admin authentication..."
            hydra -L "security-testing/reports/hydra_${TIMESTAMP}/usernames_extended.txt" \
                  -P "security-testing/reports/hydra_${TIMESTAMP}/passwords_extended.txt" \
                  -s 8000 \
                  -f \
                  -t 4 \
                  -w 10 \
                  -v \
                  127.0.0.1 \
                  http-post-form "$endpoint:username=^USER^&password=^PASS^:Please enter the correct" \
                  -o "security-testing/reports/hydra_${TIMESTAMP}/admin_detailed.txt" || true
            ;;
        */api/*)
            print_status "Testing API authentication..."
            # JSON format
            hydra -L "security-testing/reports/hydra_${TIMESTAMP}/usernames_extended.txt" \
                  -P "security-testing/reports/hydra_${TIMESTAMP}/passwords_extended.txt" \
                  -s 8000 \
                  -f \
                  -t 4 \
                  -w 10 \
                  -v \
                  127.0.0.1 \
                  http-post-form "$endpoint:username=^USER^&password=^PASS^:H=Content-Type: application/json:Invalid" \
                  -o "security-testing/reports/hydra_${TIMESTAMP}/api_detailed.txt" || true
                  
            # Form data format
            hydra -L "security-testing/reports/hydra_${TIMESTAMP}/usernames_extended.txt" \
                  -P "security-testing/reports/hydra_${TIMESTAMP}/passwords_extended.txt" \
                  -s 8000 \
                  -f \
                  -t 4 \
                  -w 10 \
                  -v \
                  127.0.0.1 \
                  http-post-form "$endpoint:username=^USER^&password=^PASS^:Invalid" \
                  -o "security-testing/reports/hydra_${TIMESTAMP}/api_form_detailed.txt" || true
            ;;
        *)
            print_status "Testing generic authentication..."
            hydra -L "security-testing/reports/hydra_${TIMESTAMP}/usernames_extended.txt" \
                  -P "security-testing/reports/hydra_${TIMESTAMP}/passwords_extended.txt" \
                  -s 8000 \
                  -f \
                  -t 4 \
                  -w 10 \
                  -v \
                  127.0.0.1 \
                  http-post-form "$endpoint:username=^USER^&password=^PASS^:Invalid" \
                  -o "security-testing/reports/hydra_${TIMESTAMP}/generic_detailed.txt" || true
            ;;
    esac
    
    # Test with single user, multiple passwords (user enumeration)
    print_status "Testing user enumeration resistance..."
    hydra -l admin \
          -P "security-testing/reports/hydra_${TIMESTAMP}/passwords_extended.txt" \
          -s 8000 \
          -f \
          -t 2 \
          -w 15 \
          -v \
          127.0.0.1 \
          http-post-form "$endpoint:username=^USER^&password=^PASS^:Invalid" \
          -o "security-testing/reports/hydra_${TIMESTAMP}/user_enum.txt" || true
    
    print_success "Detailed Hydra testing completed. Reports in security-testing/reports/hydra_${TIMESTAMP}/"
}

# Main execution
case "$1" in
    bandit)
        run_bandit_detailed
        ;;
    nikto)
        run_nikto_detailed "$@"
        ;;
    zap)
        if [[ "$2" == "gui" ]]; then
            run_zap_gui
        else
            run_zap_automated "$@"
        fi
        ;;
    sqlmap)
        run_sqlmap_detailed "$@"
        ;;
    hydra)
        run_hydra_detailed "$@"
        ;;
    all)
        print_status "Running all security tests..."
        exec ./run-security-tests.sh
        ;;
    *)
        show_usage
        exit 1
        ;;
esac