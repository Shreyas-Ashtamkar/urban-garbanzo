.PHONY: help install dev install-dev clean test lint format typecheck precommit run docs env migrate db-upgrade

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
	copy .env.example .env
	@echo "Created .env file - update with your configuration"

clean:
	powershell -NoProfile -Command "Get-ChildItem -Path . -Recurse -Directory -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -in @('__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','htmlcov') } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	powershell -NoProfile -Command "Get-ChildItem -Path . -Recurse -Directory -Force -Filter '*.egg-info' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	powershell -NoProfile -Command "Remove-Item -Force -Recurse build,dist,.eggs,.coverage -ErrorAction SilentlyContinue"

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

migrate:
	aerich migrate

db-upgrade:
	aerich upgrade

docs:
	@echo "Documentation generation not yet configured"
