# Python Trading Tools - Makefile
# Author: venantvr

.PHONY: help install install-dev test test-verbose coverage clean lint format build upload docs check-deps

# Default target
help:
	@echo "Python Trading Tools - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install      Install the package in production mode"
	@echo "  install-dev  Install the package in development mode with test dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test         Run tests using unittest"
	@echo "  test-verbose Run tests with verbose output"
	@echo "  pytest       Run tests using pytest (requires pytest installation)"
	@echo "  coverage     Run tests with coverage reporting"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         Run code linting (requires flake8)"
	@echo "  format       Format code using black (requires black)"
	@echo "  check-deps   Check for security vulnerabilities in dependencies"
	@echo ""
	@echo "Build & Distribution:"
	@echo "  build        Build distribution packages"
	@echo "  upload       Upload to PyPI (requires twine)"
	@echo "  upload-test  Upload to Test PyPI"
	@echo ""
	@echo "Utilities:"
	@echo "  clean        Remove build artifacts and cache files"
	@echo "  docs         Generate documentation (placeholder)"
	@echo "  demo         Run demo examples"

# Installation targets
install:
	@echo "Installing Python Trading Tools..."
	pip install .

install-dev:
	@echo "Installing Python Trading Tools in development mode..."
	pip install -e ".[dev]"
	@echo "Development installation complete!"

# Testing targets
test:
	@echo "Running tests with unittest..."
	python -m unittest discover tests -v

test-verbose:
	@echo "Running tests with detailed output..."
	python -m unittest discover tests -v -s tests -p "test_*.py"

pytest:
	@echo "Running tests with pytest..."
	@command -v pytest >/dev/null 2>&1 || { echo "pytest not installed. Run 'make install-dev' first."; exit 1; }
	pytest

coverage:
	@echo "Running tests with coverage..."
	@command -v pytest >/dev/null 2>&1 || { echo "pytest not installed. Run 'make install-dev' first."; exit 1; }
	pytest --cov=venantvr --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

# Code quality targets
lint:
	@echo "Running code linting..."
	@command -v flake8 >/dev/null 2>&1 || { echo "flake8 not installed. Install with: pip install flake8"; exit 1; }
	flake8 venantvr/ --max-line-length=100 --ignore=E203,W503

format:
	@echo "Formatting code with black..."
	@command -v black >/dev/null 2>&1 || { echo "black not installed. Install with: pip install black"; exit 1; }
	black venantvr/ tests/ --line-length=100

check-deps:
	@echo "Checking for security vulnerabilities..."
	@command -v safety >/dev/null 2>&1 || { echo "safety not installed. Install with: pip install safety"; exit 1; }
	safety check

# Build and distribution targets
build:
	@echo "Building distribution packages..."
	python -m pip install --upgrade build
	python -m build
	@echo "Distribution packages created in dist/"

upload-test:
	@echo "Uploading to Test PyPI..."
	@command -v twine >/dev/null 2>&1 || { echo "twine not installed. Install with: pip install twine"; exit 1; }
	twine upload --repository testpypi dist/*

upload:
	@echo "Uploading to PyPI..."
	@command -v twine >/dev/null 2>&1 || { echo "twine not installed. Install with: pip install twine"; exit 1; }
	@read -p "Are you sure you want to upload to PyPI? (y/N) " confirm && [ "$$confirm" = "y" ]
	twine upload dist/*

# Utility targets
clean:
	@echo "Cleaning build artifacts and cache files..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.orig" -delete
	find . -type f -name "*.rej" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

docs:
	@echo "Documentation generation not yet implemented"
	@echo "TODO: Add Sphinx documentation generation"

# Development workflow targets
dev-setup: install-dev
	@echo "Development environment ready!"
	@echo "Run 'make test' to verify everything works"

dev-test: clean test coverage
	@echo "Full development test cycle complete!"

# CI/CD pipeline simulation
ci: install-dev test coverage lint
	@echo "CI pipeline simulation complete!"

# Quick quality check
quick-check: test lint
	@echo "Quick quality check complete!"