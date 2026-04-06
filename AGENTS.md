# AGENTS.md

## Project Overview

**urban-garbanzo** is a platform for evaluating and improving AI prompts. It provides ratings across:
- Clarity, Correctness, Information Density, Hallucination Risk, Redundancy
- Leaderboard system for prompt engineering competitions
- Workflow optimization tools

**Status**: Python project using FastAPI + Tortoise ORM.

## Development Setup

Note: The virtual Python environment is located in `venv/`. The terminal environment is Windows PowerShell, so commands and paths should be used accordingly (e.g., use `.\` for relative paths).

```bash
# Clone and setup
git clone https://github.com/Shreyas-Ashtamkar/urban-garbanzo.git
cd urban-garbanzo

# Create venv (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
make install-dev  # or: pip install -r requirements-dev.txt

# Create .env
make env  # or: cp .env.example .env
```

## Running Locally

```bash
make run  # uvicorn urban_garbanzo.main:app --reload --host 0.0.0.0 --port 8000
```

API docs at http://localhost:8000/docs

## Testing

```bash
make test           # Run tests with coverage
pytest              # Direct pytest
pytest tests/       # Specific test path
```

## Linting & Formatting

```bash
make lint           # ruff check + mypy
make format         # black + ruff --fix
make typecheck      # mypy only
make precommit      # Run pre-commit hooks
```

Tools: ruff (linting + import sorting), black (formatting), mypy (type checking), pre-commit hooks

## CI Expectations

Before committing, ensure:
1. `make test` passes
2. `make lint` passes
3. `make format` applied

CI runs: lint.yml (ruff, black, mypy), test.yml (pytest with coverage)

## Project Structure

```
src/urban_garbanzo/    # Main package
├── main.py            # FastAPI app
├── config.py          # Settings
└── __init__.py
tests/                 # Test suite
docs/                  # Documentation
.github/workflows/    # CI pipelines
```

## Database

- Development: SQLite (default, no setup)
- Production: PostgreSQL (set DATABASE_URL in .env)
