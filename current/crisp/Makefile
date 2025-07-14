.PHONY: test test-verbose test-coverage test-models test-services test-api test-views
.PHONY: test-commands test-access test-anon test-utils test-integration test-performance
.PHONY: coverage-report coverage-html coverage-xml coverage-json clean-coverage
.PHONY: install-deps setup-test help

# Variables
PYTHON = python3
COVERAGE = coverage
MANAGE = python3 manage.py
TEST_PATH = core.tests core.user_management core.trust
SOURCE = ../core

# Default target
help:
	@echo "🚀 CRISP Trust Management Test Commands"
	@echo "========================================"
	@echo "test                 - Run all 143 tests with coverage"
	@echo "test-verbose         - Run all tests with verbose output"
	@echo "test-coverage        - Run tests and generate all coverage reports"
	@echo "test-models          - Run model tests only"
	@echo "test-services        - Run service tests only" 
	@echo "test-user-management - Run user management tests only"
	@echo "test-trust           - Run trust management tests only"
	@echo "test-integration     - Run integration tests only"
	@echo "test-repositories    - Run repository tests only"
	@echo "test-validators      - Run validator tests only"
	@echo "coverage-report      - Generate console coverage report"
	@echo "coverage-html        - Generate HTML coverage report"
	@echo "coverage-xml         - Generate XML coverage report"
	@echo "coverage-json        - Generate JSON coverage report"
	@echo "clean-coverage       - Clean coverage data"
	@echo "install-deps         - Install test dependencies"
	@echo "setup-test           - Setup test environment"
	@echo ""
	@echo "🎯 Quick start: make test (runs all 143 tests)"

# Install dependencies
install-deps:
	pip install coverage pytest pytest-django pytest-cov factory-boy

# Setup test environment
setup-test:
	$(MANAGE) migrate
	$(MANAGE) setup_trust --create-defaults

# Clean coverage data
clean-coverage:
	$(COVERAGE) erase
	rm -rf htmlcov/
	rm -f coverage.xml coverage.json .coverage*

# Run all tests with coverage
test: clean-coverage
	$(COVERAGE) run --source=$(SOURCE) manage.py test $(TEST_PATH) --settings=test_settings
	$(COVERAGE) report --show-missing

# Run all tests with verbose output
test-verbose: clean-coverage
	$(COVERAGE) run --source=$(SOURCE) manage.py test $(TEST_PATH) --settings=test_settings -v 2
	$(COVERAGE) report --show-missing

# Run comprehensive test suite with all reports
test-coverage: clean-coverage
	@echo "🧪 Running comprehensive test suite..."
	$(COVERAGE) run --source=$(SOURCE) manage.py test $(TEST_PATH) --settings=test_settings -v 2
	@echo "📊 Generating coverage reports..."
	$(COVERAGE) report --show-missing --fail-under=75
	$(COVERAGE) html
	$(COVERAGE) xml
	$(COVERAGE) json
	@echo "✅ All tests completed! Reports available in htmlcov/index.html"

# Individual test categories
test-models:
	$(COVERAGE) run --source=$(SOURCE) manage.py test $(TEST_PATH).tests.test_models --settings=test_settings -v 2

test-services:
	$(COVERAGE) run --source=$(SOURCE) manage.py test $(TEST_PATH).tests.test_services --settings=test_settings -v 2

test-user-management:
	$(COVERAGE) run --source=$(SOURCE) manage.py test $(TEST_PATH).user_management --settings=test_settings -v 2

test-trust:
	$(COVERAGE) run --source=$(SOURCE) manage.py test $(TEST_PATH).trust --settings=test_settings -v 2

test-integration:
	$(COVERAGE) run --source=$(SOURCE) manage.py test $(TEST_PATH).tests.test_integration --settings=test_settings -v 2

test-repositories:
	$(COVERAGE) run --source=$(SOURCE) manage.py test $(TEST_PATH).tests.test_repositories --settings=test_settings -v 2

test-validators:
	$(COVERAGE) run --source=$(SOURCE) manage.py test $(TEST_PATH).tests.test_validators --settings=test_settings -v 2

# Coverage reports
coverage-report:
	$(COVERAGE) report --show-missing --fail-under=75

coverage-html:
	$(COVERAGE) html
	@echo "HTML report: htmlcov/index.html"

coverage-xml:
	$(COVERAGE) xml
	@echo "XML report: coverage.xml"

coverage-json:
	$(COVERAGE) json
	@echo "JSON report: coverage.json"
