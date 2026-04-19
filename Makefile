.PHONY: help install dev install-dev clean test test-unit test-e2e test-all lint format typecheck precommit run docs env migrate db-upgrade

VENV_PYTHON := $(strip $(shell powershell -NoProfile -Command "$${venv} = Get-ChildItem -Path . -Directory -Force -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $$_.FullName 'pyvenv.cfg') } | Select-Object -First 1 -ExpandProperty FullName; if ($${venv}) { Join-Path $${venv} 'Scripts\\python.exe' }"))
PYTHON ?= $(if $(VENV_PYTHON),$(VENV_PYTHON),python)
PIP := "$(PYTHON)" -m pip

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
	@echo "  make test             Run unit tests with coverage"
	@echo "  make test-e2e         Run Playwright browser tests"
	@echo "  make test-all         Run unit and browser tests"
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
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements-dev.txt

dev: install-dev
	$(PIP) install -e .

env:
	copy .env.example .env
	@echo "Created .env file - update with your configuration"

clean:
	powershell -NoProfile -Command "Get-ChildItem -Path . -Recurse -Directory -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -in @('__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','htmlcov') } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	powershell -NoProfile -Command "Get-ChildItem -Path . -Recurse -Directory -Force -Filter '*.egg-info' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	powershell -NoProfile -Command "Remove-Item -Force -Recurse build,dist,.eggs,.coverage -ErrorAction SilentlyContinue"

test:
	"$(PYTHON)" -m pytest tests

test-unit:
	"$(PYTHON)" -m pytest

test-e2e:
	"$(PYTHON)" -m pytest --override-ini addopts="--strict-markers -v --tb=short" tests_e2e

test-all:
	"$(PYTHON)" -m pytest tests
	"$(PYTHON)" -m pytest --override-ini addopts="--strict-markers -v --tb=short" tests_e2e

test-watch:
	"$(PYTHON)" -m pytest_watch

lint:
	"$(PYTHON)" -m ruff check src tests tests_e2e
	"$(PYTHON)" -m mypy src

format:
	"$(PYTHON)" -m black src tests tests_e2e
	"$(PYTHON)" -m ruff check --fix src tests tests_e2e

typecheck:
	"$(PYTHON)" -m mypy src

precommit:
	"$(PYTHON)" -m pre_commit run --all-files

run:
	"$(PYTHON)" -m uvicorn urban_garbanzo.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	"$(PYTHON)" -m aerich migrate

db-upgrade:
	"$(PYTHON)" -m aerich upgrade

docs:
	@echo "Documentation generation not yet configured"
