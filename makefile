# Makefile for CRISP Anonymization System

.PHONY: help install install-dev test test-all test-runner demo interactive clean

# Default target
help:
	@echo "CRISP Anonymization System - Available Commands:"
	@echo ""
	@echo "  install         Install package and basic dependencies"
	@echo "  install-dev     Install package with development dependencies"
	@echo "  test            Run original unit tests"
	@echo "  test-all        Run all three test files separately"
	@echo "  test-runner     Run unified test runner with all tests"
	@echo "  demo            Run demonstration"
	@echo "  interactive     Start interactive mode"
	@echo "  clean           Clean up temporary files"
	@echo ""

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e .[dev]

# Testing targets
test:
	python test_anonymization.py

test-all:
	python test_anonymization.py
	python additional_tests.py
	python test_strategies.py

test-runner:
	python run_tests.py

test-perf:
	python run_tests.py --performance

# Development targets
demo:
	python main.py demo

interactive:
	python main.py interactive

quick-test:
	python quick_test.py

# Clean up
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf *.egg-info
	rm -rf build dist .coverage htmlcov .pytest_cache .mypy_cache