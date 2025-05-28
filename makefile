# Makefile for CRISP Anonymization System

.PHONY: help install install-dev test demo interactive clean

# Default target
help:
	@echo "CRISP Anonymization System - Available Commands:"
	@echo ""
	@echo "  install         Install package and basic dependencies"
	@echo "  install-dev     Install package with development dependencies"
	@echo "  test           Run unit tests"
	@echo "  demo           Run demonstration"
	@echo "  interactive    Start interactive mode"
	@echo "  clean          Clean up temporary files"
	@echo ""

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e .[dev]

# Testing targets
test:
	python test_anonymization.py

# Development targets
demo:
	python main.py demo

interactive:
	python main.py interactive

# Clean up
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf *.egg-info
	rm -rf build dist .coverage htmlcov .pytest_cache .mypy_cache