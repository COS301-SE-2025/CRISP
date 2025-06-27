#!/bin/bash

# CRISP Coverage Analysis Script
# Runs comprehensive test coverage for the CRISP platform by explicitly targeting all test files.

echo "🧪 CRISP Test Coverage Analysis - Running ALL tests"
echo "==================================================="

# Change to project root
cd "/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone"

# Set Python path
export PYTHONPATH="/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone"

echo "📊 Running coverage analysis on all known test files..."

# Run pytest on every single test file to ensure maximum coverage.
# This command is intentionally explicit to avoid discovery issues.
DJANGO_SETTINGS_MODULE=crisp.test_settings python3 -m pytest \
    core/tests/test_admin_views.py \
    core/tests/test_anonymization_service_integration.py \
    core/tests/test_anonymization_strategies.py \
    core/tests/test_api_comprehensive.py \
    core/tests/test_api_permissions_serializers.py \
    core/tests/test_api_repository_comprehensive.py \
    core/tests/test_auth_debug.py \
    core/tests/test_auth_views.py \
    core/tests/test_authentication.py \
    core/tests/test_comprehensive_coverage.py \
    core/tests/test_coverage_completion.py \
    core/tests/test_decorator.py \
    core/tests/test_decorator_patterns_comprehensive.py \
    core/tests/test_end_to_end.py \
    core/tests/test_factory_patterns_comprehensive.py \
    core/tests/test_final_working.py \
    core/tests/test_integration.py \
    core/tests/test_management_commands.py \
    core/tests/test_middleware.py \
    core/tests/test_models_comprehensive.py \
    core/tests/test_observer.py \
    core/tests/test_observers.py \
    core/tests/test_observers_simple.py \
    core/tests/test_repository.py \
    core/tests/test_security.py \
    core/tests/test_services_comprehensive.py \
    core/tests/test_simple_coverage.py \
    core/tests/test_stix1_parser.py \
    core/tests/test_stix_factory.py \
    core/tests/test_stix_mock_data.py \
    core/tests/test_taxii_integration.py \
    core/tests/test_taxii_parser_comprehensive.py \
    core/tests/test_taxii_service.py \
    core/tests/test_trust_anonymization_integration.py \
    core/tests/test_ultra_clean.py \
    core/tests/test_user_management.py \
    core/tests/test_user_views.py \
    core/tests/test_working.py \
    --cov=core \
    --cov=crisp \
    --cov-report=html:core/coverage/html \
    --cov-report=term-missing \
    --cov-report=json:core/coverage/coverage.json \
    -v

echo ""
echo "📋 Coverage Report Generated:"
echo "   - HTML Report: core/coverage/html/index.html"
echo "   - JSON Report: core/coverage/coverage.json"
echo "   - Summary: core/coverage/README.md"

echo ""
echo "🎯 Quick Stats:"
if [ -f "core/coverage/coverage.json" ]; then
    python3 -c "
import json
with open('core/coverage/coverage.json', 'r') as f:
    data = json.load(f)
    total = data['totals']['num_statements']
    covered = data['totals']['covered_lines']
    percent = data['totals']['percent_covered']
    print(f'   Total Statements: {total}')
    print(f'   Covered: {covered}')
    print(f'   Coverage: {percent:.1f}%')
"
fi

echo ""
echo "🚀 To view HTML report:"
echo "   Open: core/coverage/html/index.html"
echo ""
echo "✅