#!/bin/bash
# Code quality check script

set -e

echo "Running code quality checks for Trust Management..."

# Check if we're in the right directory
if [ ! -d "trust_management_app" ]; then
    echo "Error: Please run this script from the trust_management root directory"
    exit 1
fi

# Use explicit paths for tools (they're installed in ~/.local/bin/)
BLACK_CMD="python -m black"
ISORT_CMD="python -m isort"
FLAKE8_CMD="python -m flake8"
MYPY_CMD="python -m mypy"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

echo "1. Running Black code formatter..."
$BLACK_CMD trust_management_app/ tests/ --check --diff || echo "Black formatting issues found"

echo "2. Running isort import sorter..."
$ISORT_CMD trust_management_app/ tests/ --check-only --diff || echo "Import sorting issues found"

echo "3. Running flake8 linter..."
$FLAKE8_CMD trust_management_app/ tests/ || echo "Flake8 issues found"

echo "4. Running mypy type checker..."
$MYPY_CMD trust_management_app/ || echo "Type checking issues found"

# Optional security checks (install if needed)
if command -v bandit &> /dev/null; then
    echo "5. Running bandit security linter..."
    bandit -r trust_management_app/ -f json -o reports/bandit_report.json || echo "Bandit issues found"
else
    echo "5. Skipping bandit (not installed) - run: pip install bandit"
fi

if command -v safety &> /dev/null; then
    echo "6. Running safety security checker..."
    safety check --json --output reports/safety_report.json || echo "Safety issues found"
else
    echo "6. Skipping safety (not installed) - run: pip install safety"
fi

echo "Code quality checks completed!"
echo "Reports saved in reports/ directory"
echo "Note: Some issues may have been found - check output above"
