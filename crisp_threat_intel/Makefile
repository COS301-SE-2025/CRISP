.PHONY: help install test lint format clean coverage stix-tests

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  test        Run all tests"
	@echo "  stix-tests  Run STIX-specific tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  coverage    Run tests with coverage"
	@echo "  clean       Clean generated files"

install:
	pip install -r requirements/development.txt

test:
	python tools/test_runners/run_tests.py

stix-tests:
	python tools/test_runners/run_stix_tests.py

lint:
	flake8 crisp_threat_intel/ tests/
	mypy crisp_threat_intel/

format:
	black crisp_threat_intel/ tests/

coverage:
	python -m pytest --cov=crisp_threat_intel --cov-report=html

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf coverage/htmlcov/
	rm -f coverage/coverage.xml