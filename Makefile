.PHONY: help build run test clean docs docker lint format install dev-install

# Default target
help:
	@echo "Seneca Development Commands:"
	@echo "  make install      - Install Seneca in production mode"
	@echo "  make dev-install  - Install Seneca in development mode"
	@echo "  make run          - Run Seneca server"
	@echo "  make test         - Run all tests"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run code linters"
	@echo "  make format       - Format code with Black"
	@echo "  make docs         - Build documentation"
	@echo "  make docker       - Build Docker image"
	@echo "  make docker-run   - Run Seneca in Docker"
	@echo "  make clean        - Clean build artifacts"

# Installation
install:
	pip install -e .

dev-install:
	pip install -e ".[dev,docs]"
	pre-commit install

# Running
run:
	python start_seneca.py

run-debug:
	python -m debugpy --listen 5678 --wait-for-client start_seneca.py

# Testing
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/ tests/
	mypy src/ --ignore-missing-imports
	bandit -r src/

format:
	black src/ tests/
	isort src/ tests/

check: lint test

# Documentation
docs:
	cd docs && make clean && make html

docs-serve:
	cd docs/_build/html && python -m http.server

# Docker
docker:
	docker build -t seneca:latest .

docker-dev:
	docker build -f Dockerfile.dev -t seneca:dev .

docker-run:
	docker-compose up -d

docker-run-dev:
	docker-compose -f docker-compose.dev.yml up

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f seneca

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/ docs/_build/

# Release
release-test:
	python -m build
	twine check dist/*

release:
	python -m build
	twine upload dist/*

# Development workflow
dev: dev-install
	@echo "Development environment ready!"
	@echo "Run 'make run' to start Seneca"

# CI/CD helpers
ci-test:
	pytest tests/ -v --cov=src --cov-report=xml

ci-lint:
	flake8 src/ tests/ --exit-zero
	mypy src/ --ignore-missing-imports --no-error-summary

ci-security:
	bandit -r src/ -f json -o bandit-report.json
	safety check --json