.PHONY: test test-verbose test-coverage test-models test-services test-api test-views
.PHONY: test-commands test-access test-anon test-utils test-integration test-performance
.PHONY: coverage-report coverage-html coverage-xml coverage-json clean-coverage
.PHONY: install-deps setup-test help

# Variables
PYTHON = python
COVERAGE = coverage
MANAGE = $(PYTHON) manage.py
TEST_PATH = TrustManagement.tests
SOURCE = TrustManagement

# Default target
help:
	@echo "🚀 Trust Management Test Commands"
	@echo "================================="
	@echo "test                 - Run all tests with coverage"
	@echo "test-verbose         - Run all tests with verbose output"
	@echo "test-coverage        - Run tests and generate all coverage reports"
	@echo "test-models          - Run model tests only"
	@echo "test-services        - Run service tests only" 
	@echo "test-api             - Run API tests only"
	@echo "test-views           - Run view tests only"
	@echo "test-commands        - Run management command tests only"
	@echo "test-access          - Run access control tests only"
	@echo "test-anon            - Run anonymization tests only"
	@echo "test-utils           - Run utility tests only"
	@echo "test-integration     - Run integration tests only"
	@echo "test-performance     - Run performance tests only"
	@echo "coverage-report      - Generate console coverage report"
	@echo "coverage-html        - Generate HTML coverage report"
	@echo "coverage-xml         - Generate XML coverage report"
	@echo "coverage-json        - Generate JSON coverage report"
	@echo "clean-coverage       - Clean coverage data"
	@echo "install-deps         - Install test dependencies"
	@echo "setup-test           - Setup test environment"

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
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH)
	$(COVERAGE) report --show-missing

# Run all tests with verbose output
test-verbose: clean-coverage
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH) -v 2
	$(COVERAGE) report --show-missing

# Run comprehensive test suite with all reports
test-coverage: clean-coverage
	@echo "🧪 Running comprehensive test suite..."
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_models -v 2
	$(COVERAGE) run -a --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_services -v 2
	$(COVERAGE) run -a --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_api -v 2
	$(COVERAGE) run -a --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_views -v 2
	$(COVERAGE) run -a --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_management_commands -v 2
	$(COVERAGE) run -a --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_access_control -v 2
	$(COVERAGE) run -a --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_anonymization -v 2
	$(COVERAGE) run -a --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_utils -v 2
	$(COVERAGE) run -a --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_integrations -v 2
	$(COVERAGE) run -a --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_performance -v 2
	$(COVERAGE) combine
	@echo "📊 Generating coverage reports..."
	$(COVERAGE) report --show-missing --fail-under=96
	$(COVERAGE) html
	$(COVERAGE) xml
	$(COVERAGE) json
	@echo "✅ All tests completed! Reports available in htmlcov/index.html"

# Individual test categories
test-models:
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_models -v 2

test-services:
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_services -v 2

test-api:
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_api -v 2

test-views:
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_views -v 2

test-commands:
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_management_commands -v 2

test-access:
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_access_control -v 2

test-anon:
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_anonymization -v 2

test-utils:
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_utils -v 2

test-integration:
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_integrations -v 2

test-performance:
	$(COVERAGE) run --source=$(SOURCE) $(MANAGE) test $(TEST_PATH).test_performance -v 2

# Coverage reports
coverage-report:
	$(COVERAGE) report --show-missing --fail-under=96

coverage-html:
	$(COVERAGE) html
	@echo "HTML report: htmlcov/index.html"

coverage-xml:
	$(COVERAGE) xml
	@echo "XML report: coverage.xml"

coverage-json:
	$(COVERAGE) json
	@echo "JSON report: coverage.json"
