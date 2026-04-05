# Development Setup Guide

This guide will help you set up urban-garbanzo for local development.

## System Requirements

- **Python**: 3.10 or higher (check with `python --version`)
- **PostgreSQL**: 13+ (optional, SQLite works for development)
- **pip**: Python package manager (comes with Python)
- **git**: Version control (comes pre-installed on most systems)

## Step-by-Step Setup

### Step 1: Clone and Enter Repository

```bash
git clone https://github.com/Shreyas-Ashtamkar/urban-garbanzo.git
cd urban-garbanzo
```

### Step 2: Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

You should see `(venv)` in your terminal prompt when activated.

### Step 3: Install Dependencies

**Quick install** (production only):
```bash
pip install -r requirements.txt
```

**Full install** (recommended for development):
```bash
pip install -r requirements-dev.txt
```

Or using Make:
```bash
make install-dev
```

### Step 4: Set Up Environment Variables

```bash
cp .env.example .env
```

Open `.env` and configure:
- `DATABASE_URL`: Keep as-is for SQLite, or update for PostgreSQL
- `API_HOST` and `API_PORT`: Customize if needed
- `LOG_LEVEL`: Set to DEBUG for development

### Step 5: Verify Installation

Run the test suite:
```bash
pytest
```

You should see output like:
```
============================ test session starts ============================
collected 2 items

tests/test_main.py::test_health_check PASSED                         [ 50%]
tests/test_main.py::test_app_creation PASSED                         [100%]

============================ 2 passed in 0.23s ============================
```

## Running the Development Server

```bash
# Option 1: Using uvicorn directly
uvicorn urban_garbanzo.main:app --reload

# Option 2: Using Make
make run
```

Then visit: **http://localhost:8000**
- API Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Common Development Commands

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=urban_garbanzo --cov-report=html

# Run specific test
pytest tests/test_main.py::test_health_check

# Watch mode (auto-rerun on changes)
pytest-watch
```

### Code Quality

```bash
# Check code style
ruff check src tests

# Format code automatically
black src tests

# Check type hints
mypy src

# Fix formatting issues automatically
ruff check --fix src tests
```

### Using Make

```bash
make help              # Show all available commands
make test              # Run tests
make lint              # Check code quality
make format            # Format code
make run               # Start dev server
make clean             # Clean up cache files
```

## Database Setup (Optional)

### For PostgreSQL Development

Install PostgreSQL:

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu):**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows/

Create database:
```bash
psql
CREATE DATABASE urban_garbanzo;
\q
```

Update `.env`:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/urban_garbanzo
```

### Using Docker (Easiest for PostgreSQL)

```bash
# Start PostgreSQL in Docker
docker run --name urban-garbanzo-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=urban_garbanzo \
  -p 5432:5432 \
  -d postgres:15

# Update .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/urban_garbanzo
```

## Pre-Commit Hooks

Install pre-commit hooks to automatically check code before commits:

```bash
pip install pre-commit
pre-commit install

# Run manually
make precommit
```

From now on, `git commit` will run checks automatically.

## Troubleshooting

### "Python not found"
Ensure Python 3.10+ is installed: `python --version`

### "venv not activated"
You should see `(venv)` in your terminal. If not:
- macOS/Linux: `source venv/bin/activate`
- Windows: `.\venv\Scripts\Activate.ps1`

### "Module not found"
Ensure venv is activated and dependencies installed:
```bash
pip install -r requirements-dev.txt
```

### "Port 8000 already in use"
Change port in `.env` or run:
```bash
uvicorn urban_garbanzo.main:app --port 8001
```

### PostgreSQL connection errors
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Use SQLite by default: `DATABASE_URL=sqlite://:memory:`

## Next Steps

1. **Read the documentation**: Check [README.md](../README.md)
2. **Write some code**: See [src/urban_garbanzo/](../src/urban_garbanzo/)
3. **Add tests**: See [tests/](../tests/) for examples
4. **Contribute**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## Getting Help

- Check existing [GitHub Issues](https://github.com/Shreyas-Ashtamkar/urban-garbanzo/issues)
- Open a new issue with details about your problem
- Visit the [GitHub Discussions](https://github.com/Shreyas-Ashtamkar/urban-garbanzo/discussions)

## One-Liner Quick Start

If you have everything set up already:

```bash
git clone https://github.com/Shreyas-Ashtamkar/urban-garbanzo.git && cd urban-garbanzo && python3 -m venv venv && source venv/bin/activate && pip install -r requirements-dev.txt && cp .env.example .env && make run
```

(Or use your OS-specific venv activation command)
