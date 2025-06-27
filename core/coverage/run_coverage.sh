#!/bin/bash

# CRISP Coverage Analysis Script
# Runs comprehensive test coverage for the CRISP platform

echo "🧪 CRISP Test Coverage Analysis"
echo "================================"

# Change to project root
cd "/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone"

# Set Python path
export PYTHONPATH="/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone"

echo "📊 Running coverage analysis..."

# Check if PostgreSQL is available for full tests
if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "✅ PostgreSQL detected - running full test suite"
    DJANGO_SETTINGS_MODULE=crisp.test_settings python3 -m pytest core/tests/ \
        --cov=core \
        --cov=crisp \
        --cov-report=html:core/coverage/html \
        --cov-report=term-missing \
        --cov-report=json:core/coverage/coverage.json \
        -v
else
    echo "⚠️  PostgreSQL not available - running functional tests only"
    echo "   For full coverage, ensure PostgreSQL is running on localhost:5432"
    python3 -m pytest core/tests/test_final_working.py core/tests/test_ultra_clean.py \
        --cov=core \
        --cov-report=html:core/coverage/html \
        --cov-report=term-missing \
        --cov-report=json:core/coverage/coverage.json \
        -v
fi

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
echo "✅ Coverage analysis complete!"