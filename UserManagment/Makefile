.PHONY: help install test lint format clean coverage

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  test        Run all tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  coverage    Run tests with coverage"
	@echo "  clean       Clean generated files"

install:
	pip install -r requirements/development.txt

test:
	python -m pytest

lint:
	flake8 UserManagement/ tests/
	mypy UserManagement/

format:
	black UserManagement/ tests/

coverage:
	python -m pytest --cov=UserManagement --cov-report=html

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf coverage/htmlcov/
	rm -f coverage/coverage.xml