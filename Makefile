.PHONY: help install install-dev test lint format clean build docs serve

# Default target
help:
	@echo "PACE - Project Analysis & Construction Estimating"
	@echo ""
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  docs         Build documentation"
	@echo "  serve        Serve documentation locally"
	@echo "  init         Initialize PACE application"
	@echo "  run          Run PACE CLI"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Testing
test:
	pytest tests/ -v --cov=src/pace --cov-report=html --cov-report=term

test-unit:
	pytest tests/ -v -m "unit" --cov=src/pace --cov-report=html --cov-report=term

test-integration:
	pytest tests/ -v -m "integration" --cov=src/pace --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/ -f json -o bandit-report.json

format:
	black src/ tests/
	isort src/ tests/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Build
build:
	python -m build

# Documentation
docs:
	cd docs && make html

serve:
	cd docs/_build/html && python -m http.server 8000

# PACE specific
init:
	python -m pace.cli.main init

run:
	python -m pace.cli.main

# Development helpers
dev-setup: install-dev
	pre-commit install
	python -m pace.cli.main init

check-all: lint test
	@echo "All checks passed!"

# Docker (if needed)
docker-build:
	docker build -t pace-construction-estimating .

docker-run:
	docker run -p 8000:8000 pace-construction-estimating 