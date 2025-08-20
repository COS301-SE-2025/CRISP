# CRISP Security Testing Guide

## Overview

This guide provides comprehensive security testing for your Django + Vite application using industry-standard tools. All testing is configured for **LOCAL DEVELOPMENT ONLY** - never run these tools against production systems without proper authorization.

## ⚠️ IMPORTANT WARNINGS

- **LOCAL TESTING ONLY**: These tools can cause damage if used improperly
- **AUTHORIZATION REQUIRED**: Only test systems you own or have explicit permission to test
- **BACKUP YOUR DATA**: Some tests may affect database state
- **DEVELOPMENT ENVIRONMENT**: Never run against production systems

## Quick Start

### 1. Setup (One-time)
```bash
# Make scripts executable
chmod +x security-testing-setup.sh run-security-tests.sh

# Run setup (installs all tools)
./security-testing-setup.sh

# Reload your shell environment
source ~/.bashrc
```

### 2. Start Your Applications
```bash
# Terminal 1: Start Django backend
cd /path/to/your/django/project
python manage.py runserver 127.0.0.1:8000

# Terminal 2: Start Vite frontend
cd crisp-react
npm run dev
```

### 3. Run Security Tests
```bash
# Run all security tests
./run-security-tests.sh

# Results will be saved to: security-testing/reports/[timestamp]/
```

## Individual Tool Usage

### 1. Bandit (Static Code Analysis)

**Purpose**: Identifies insecure code patterns in Python/Django code.

**What it finds**:
- Hardcoded passwords/secrets
- SQL injection vulnerabilities
- Use of insecure functions
- Weak cryptographic practices
- Path traversal vulnerabilities

**Manual Usage**:
```bash
# Scan entire Django project
bandit -r ./core ./crisp_unified -f html -o bandit_report.html

# Scan specific file
bandit core/models/models.py -f json -o bandit_single.json

# Scan with custom config
bandit -r ./core -c security-testing/configs/bandit.yaml -f txt

# Show all available tests
bandit --help
```

**Configuration File**: `security-testing/configs/bandit.yaml`

### 2. Nikto (Web Server Scanner)

**Purpose**: Scans web servers for misconfigurations and known vulnerabilities.

**What it finds**:
- Outdated server versions
- Dangerous files/programs
- Server misconfigurations
- Default files and programs
- Insecure HTTP methods

**Manual Usage**:
```bash
# Scan Django backend
nikto -h http://127.0.0.1:8000 -output nikto_django.html -Format html

# Scan Vite frontend
nikto -h http://127.0.0.1:5173 -output nikto_vite.html -Format html

# Scan with specific checks
nikto -h http://127.0.0.1:8000 -Plugins "@@ALL" -output detailed_scan.txt

# Scan specific path
nikto -h http://127.0.0.1:8000/admin/ -output admin_scan.html -Format html
```

### 3. OWASP ZAP (Web Application Security)

**Purpose**: Comprehensive web application security testing.

**What it finds**:
- Cross-Site Scripting (XSS)
- SQL injection
- Cross-Site Request Forgery (CSRF)
- Security header issues
- Authentication bypasses
- Session management flaws

**Manual Usage**:

**GUI Mode** (Recommended for detailed analysis):
```bash
# Launch ZAP GUI
zap.sh

# Manual steps in GUI:
# 1. Set target URL (http://127.0.0.1:8000)
# 2. Use Spider to crawl the application
# 3. Run Active Scan
# 4. Generate reports from Report menu
```

**Command Line Mode**:
```bash
# Quick scan
zap.sh -cmd -quickurl http://127.0.0.1:8000 -quickout zap_quick_report.html

# Automated scan with custom config
zap.sh -cmd -autorun security-testing/configs/zap_automation.yaml
```

**Automation Config Example**:
```yaml
# Create custom automation config
cat > security-testing/configs/zap_automation.yaml << 'EOF'
---
env:
  contexts:
    - name: "CRISP_Full"
      urls:
        - "http://127.0.0.1:8000"
        - "http://127.0.0.1:5173"

jobs:
  - type: spider
    parameters:
      maxDuration: 5
      maxDepth: 10
      
  - type: activeScan
    parameters:
      maxScanDurationInMins: 15
      
  - type: report
    parameters:
      template: "traditional-html"
      reportFile: "comprehensive_zap_report.html"
EOF
```

### 4. sqlmap (SQL Injection Testing)

**Purpose**: Automated SQL injection vulnerability detection and exploitation.

**What it finds**:
- Boolean-based blind SQL injection
- Time-based blind SQL injection
- Error-based SQL injection
- Union query SQL injection
- Stacked queries SQL injection

**Manual Usage**:

**Basic Testing**:
```bash
# Test GET parameter
sqlmap -u "http://127.0.0.1:8000/api/users/?id=1" --batch

# Test POST data
sqlmap -u "http://127.0.0.1:8000/api/auth/login/" --data="username=test&password=test" --batch

# Test with cookies/headers
sqlmap -u "http://127.0.0.1:8000/api/users/" --cookie="sessionid=abc123" --batch
```

**Advanced Testing**:
```bash
# Test all parameters in request file
sqlmap -r request.txt --batch

# Specific database tests
sqlmap -u "http://127.0.0.1:8000/api/users/?id=1" --dbms=postgresql --batch

# Risk and level settings
sqlmap -u "http://127.0.0.1:8000/api/users/?id=1" --level=3 --risk=2 --batch
```

**Request File Example** (`request.txt`):
```
POST /api/auth/login/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 45

{"username": "test*", "password": "test"}
```

### 5. Hydra (Brute Force Testing)

**Purpose**: Tests authentication mechanisms against brute force attacks.

**What it finds**:
- Weak passwords
- Default credentials
- Account enumeration vulnerabilities
- Rate limiting bypasses

**Manual Usage**:

**HTTP Form Brute Force**:
```bash
# Login form brute force
hydra -L security-testing/wordlists/common_usernames.txt \
      -P security-testing/wordlists/common_passwords.txt \
      127.0.0.1 -s 8000 \
      http-post-form "/api/auth/login/:username=^USER^&password=^PASS^:Invalid"

# Admin panel brute force
hydra -L security-testing/wordlists/common_usernames.txt \
      -P security-testing/wordlists/common_passwords.txt \
      127.0.0.1 -s 8000 \
      http-post-form "/admin/login/:username=^USER^&password=^PASS^:Please enter"
```

**API Brute Force**:
```bash
# JSON API brute force
hydra -L users.txt -P passwords.txt 127.0.0.1 -s 8000 \
      http-post-form "/api/auth/login/:username=^USER^&password=^PASS^:H=Content-Type: application/json:Invalid"
```

## Custom Testing Scenarios

### Testing CRISP-Specific Endpoints

**1. Authentication Testing**:
```bash
# Test registration endpoint
sqlmap -u "http://127.0.0.1:8000/api/auth/register/" \
       --data='{"username":"test","password":"test","email":"test@test.com"}' \
       --headers="Content-Type: application/json" --batch

# Test JWT token endpoints
sqlmap -u "http://127.0.0.1:8000/api/auth/token/refresh/" \
       --data='{"refresh":"token_here"}' \
       --headers="Content-Type: application/json" --batch
```

**2. TAXII Endpoint Testing**:
```bash
# Test TAXII collection endpoints
nikto -h http://127.0.0.1:8000/taxii/ -output taxii_scan.html -Format html

# SQL injection testing on TAXII
sqlmap -u "http://127.0.0.1:8000/taxii/collections/?id=1" --batch
```

**3. Trust Management Testing**:
```bash
# Test trust relationship endpoints
sqlmap -u "http://127.0.0.1:8000/api/trust/?user_id=1" --batch

# Brute force trust admin functions
hydra -L security-testing/wordlists/common_usernames.txt \
      -P security-testing/wordlists/common_passwords.txt \
      127.0.0.1 -s 8000 \
      http-post-form "/api/trust/admin/:username=^USER^&password=^PASS^:Unauthorized"
```

## Understanding Results

### Severity Levels

**Critical** 🔴
- SQL injection vulnerabilities
- Remote code execution
- Authentication bypasses
- Sensitive data exposure

**High** 🟠
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Privilege escalation
- Weak authentication

**Medium** 🟡
- Information disclosure
- Missing security headers
- Weak session management
- Input validation issues

**Low** 🟢
- Version disclosure
- Cache control issues
- Minor configuration issues

### Report Locations

After running tests, reports are saved to:
```
security-testing/reports/[timestamp]/
├── bandit_report.html          # Static code analysis
├── bandit_report.json          # Machine-readable format
├── nikto_django_report.html    # Django server scan
├── nikto_vite_report.html      # Vite server scan
├── zap_django_report.html      # ZAP web app scan
├── zap_vite_report.html        # ZAP frontend scan
├── sqlmap/                     # SQL injection results
├── hydra_login_report.txt      # Brute force results
└── security_assessment_summary.md  # Overview
```

## Remediation Guidelines

### Common Vulnerabilities and Fixes

**1. SQL Injection**
```python
# ❌ Vulnerable
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ Secure
from django.db import models
User.objects.filter(id=user_id)
```

**2. XSS Prevention**
```python
# ❌ Vulnerable
return HttpResponse(f"<h1>Hello {user_input}</h1>")

# ✅ Secure
from django.utils.html import escape
return HttpResponse(f"<h1>Hello {escape(user_input)}</h1>")
```

**3. CSRF Protection**
```python
# In Django views
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token

@csrf_protect
def my_view(request):
    csrf_token = get_token(request)
    # ... view logic
```

**4. Security Headers**
```python
# In Django settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
X_FRAME_OPTIONS = 'DENY'
```

## Continuous Security Testing

### Integrate with CI/CD

**GitHub Actions Example**:
```yaml
# .github/workflows/security.yml
name: Security Testing
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r ./core -f json -o bandit_results.json
      - name: Upload Security Results
        uses: actions/upload-artifact@v2
        with:
          name: security-results
          path: bandit_results.json
```

### Regular Testing Schedule

**Weekly**:
- Run full security test suite
- Review and triage new findings
- Update security testing tools

**Monthly**:
- Update wordlists and payloads
- Review security testing configurations
- Assess new threat vectors

**Before Releases**:
- Complete security assessment
- Verify all critical/high issues resolved
- Generate security sign-off report

## Troubleshooting

### Common Issues

**1. Tools Not Found**
```bash
# Check if tools are in PATH
which bandit nikto sqlmap hydra
# If not found, re-run setup script
./security-testing-setup.sh
```

**2. Permission Denied**
```bash
# Make scripts executable
chmod +x *.sh
```

**3. ZAP Won't Start**
```bash
# Check Java installation
java -version
# Install Java if needed (Ubuntu/Debian)
sudo apt install openjdk-11-jdk
```

**4. False Positives**
- Review findings manually
- Check context and exploitability
- Document false positives for future reference

### Getting Help

- **Bandit**: https://bandit.readthedocs.io/
- **Nikto**: https://github.com/sullo/nikto
- **OWASP ZAP**: https://owasp.org/www-project-zap/
- **sqlmap**: http://sqlmap.org/
- **Hydra**: https://github.com/vanhauser-thc/thc-hydra

## Legal and Ethical Considerations

- Only test systems you own or have explicit permission to test
- Respect rate limits and don't overload systems
- Document all testing activities
- Follow responsible disclosure for any findings
- Comply with your organization's security policies

---

**Remember**: Security testing is an ongoing process, not a one-time activity. Regular testing and continuous improvement are essential for maintaining a secure application.