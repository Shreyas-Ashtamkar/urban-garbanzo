.PHONY: help install dev install-dev clean test lint format typecheck precommit run docs

help:
	@echo "urban-garbanzo development commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make env              Create .env file from .env.example"
	@echo ""
	@echo "Development:"
	@echo "  make run              Run development server"
	@echo "  make test             Run tests with coverage"
	@echo "  make lint             Run linters (ruff, mypy)"
	@echo "  make format           Auto-format code (black, ruff)"
	@echo "  make typecheck        Run type checking (mypy)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make precommit        Run pre-commit hooks"
	@echo "  make clean            Clean up build artifacts"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs             Build documentation"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

dev: install-dev
	pip install -e .

env:
	cp .env.example .env
	@echo "Created .env file - update with your configuration"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -name .coverage -delete 2>/dev/null || true
	find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist .eggs .pytest_cache .mypy_cache

test:
	pytest

test-watch:
	pytest-watch

lint:
	ruff check src tests
	mypy src

format:
	black src tests
	ruff check --fix src tests

typecheck:
	mypy src

precommit:
	pre-commit run --all-files

run:
	uvicorn urban_garbanzo.main:app --reload --host 0.0.0.0 --port 8000

docs:
	@echo "Documentation generation not yet configured"
