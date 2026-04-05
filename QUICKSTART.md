# Quick Start Guide

## Project Setup Complete! ✅

Your **urban-garbanzo** project is now fully bootstrapped and ready for development.

### One-Liner Quick Start

**macOS/Linux:**
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements-dev.txt && cp .env.example .env && python -m pytest
```

**Windows (PowerShell):**
```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements-dev.txt; cp .env.example .env; python -m pytest
```

## Common Commands

```bash
# Development Setup
make install-dev          # Install all dependencies
make env                  # Create .env file

# Running the App
make run                  # Start development server (http://localhost:8000)

# Testing & Quality
make test                 # Run tests with coverage
make lint                 # Check code quality
make format               # Auto-format code
make typecheck            # Type checking

# Utilities
make clean                # Clean up cache files
make help                 # Show all available commands
```

## What's Been Created

### Directory Structure
```
urban-garbanzo/
├── src/urban_garbanzo/          # Main application package
│   ├── __init__.py              # Package metadata (v0.1.0)
│   ├── main.py                  # FastAPI app factory
│   └── config.py                # Configuration management
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_main.py             # Initial tests
├── docs/                        # Documentation
│   └── SETUP.md                 # Detailed setup guide
├── .github/workflows/           # CI/CD pipelines
│   ├── test.yml                 # Run tests on push/PR
│   └── lint.yml                 # Run linting on push/PR
├── .opencode/                   # OpenCode configuration
│   └── commands/                # Reusable AI agent prompts
├── pyproject.toml               # Project metadata & dependencies
├── setup.py                     # Alternative packaging
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── pytest.ini                   # Test configuration
├── .env.example                 # Environment variables template
├── .pre-commit-config.yaml      # Pre-commit hooks
├── Makefile                     # Development commands
├── AGENTS.md                    # Agent guidance
├── CONTRIBUTING.md              # Contribution guidelines
└── README.md                    # Project documentation
```

### Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| **Web Framework** | FastAPI | Modern, async-ready, auto-generated API docs |
| **Database** | PostgreSQL | Production-ready (SQLite default for dev) |
| **ORM** | Tortoise ORM | Async-first, works great with FastAPI |
| **Testing** | pytest + coverage | Standard Python testing framework |
| **Linting** | ruff | Fast, modern Rust-based linter |
| **Formatting** | black | Opinionated Python code formatter |
| **Type Checking** | mypy | Static type analysis for Python |

## Next Steps

1. **Activate virtual environment**:
   ```bash
   # macOS/Linux
   source venv/bin/activate

   # Windows
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Create .env file**:
   ```bash
   cp .env.example .env
   ```

4. **Verify everything works**:
   ```bash
   pytest              # Should pass 2 tests
   make run            # Start dev server
   ```

5. **Visit the API**:
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Project Features

✅ **Production-Ready Structure**
- Organized package layout (`src/` directory)
- Proper configuration management
- Type hints throughout

✅ **Testing Setup**
- pytest configured with asyncio support
- Coverage reporting (HTML reports in `htmlcov/`)
- CI/CD workflows for automated testing

✅ **Code Quality**
- Pre-commit hooks for automatic checks
- Automated formatting with black
- Linting with ruff
- Type checking with mypy

✅ **Documentation**
- README with detailed setup and usage
- CONTRIBUTING.md for contributor guidelines
- docs/SETUP.md for detailed dev setup
- AGENTS.md for AI agent guidance

✅ **Development Tools**
- Makefile with convenient commands
- Environment variable management (.env)
- GitHub Actions CI/CD pipelines
- OpenCode integration for AI-assisted development

## Files Modified/Created

### Configuration Files
- `pyproject.toml` — Project metadata, dependencies, build config
- `setup.py` — Alternative packaging configuration
- `requirements.txt` — Production dependencies
- `requirements-dev.txt` — Development dependencies
- `pytest.ini` — Test configuration
- `.pre-commit-config.yaml` — Pre-commit hooks
- `.env.example` — Environment variables template

### Source Code
- `src/urban_garbanzo/__init__.py` — Package metadata
- `src/urban_garbanzo/main.py` — FastAPI app
- `src/urban_garbanzo/config.py` — Configuration

### Tests
- `tests/__init__.py` — Test package init
- `tests/test_main.py` — Initial tests

### Documentation
- `README.md` — Updated with setup and usage
- `CONTRIBUTING.md` — Contributor guidelines
- `docs/SETUP.md` — Detailed setup guide
- `AGENTS.md` — AI agent guidance

### Development
- `Makefile` — Common commands
- `.github/workflows/test.yml` — Test CI workflow
- `.github/workflows/lint.yml` — Lint CI workflow

## Database Setup

### Development (SQLite - default)
Already configured! No setup needed.

### Production (PostgreSQL)

**Install PostgreSQL:**
```bash
# macOS
brew install postgresql

# Linux (Ubuntu)
sudo apt-get install postgresql

# Windows - download from https://www.postgresql.org/download/windows/
```

**Create database:**
```bash
psql
CREATE DATABASE urban_garbanzo;
\q
```

**Update .env:**
```
DATABASE_URL=postgresql://user:password@localhost:5432/urban_garbanzo
```

## Troubleshooting

### "Port 8000 already in use"
Edit `.env` and change `API_PORT=8001` or find what's using port 8000:
```bash
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### "Module not found errors"
Ensure virtual environment is activated and dependencies installed:
```bash
which python  # Should show venv path
pip install -r requirements-dev.txt
```

### "PostgreSQL connection errors"
Use SQLite (default) or ensure PostgreSQL is running:
```bash
# Check PostgreSQL status
psql --version
```

## What to Do Now

1. **Read the documentation**:
   - README.md for overview
   - docs/SETUP.md for detailed setup
   - CONTRIBUTING.md for development practices

2. **Start coding**:
   - Create new FastAPI routes in `src/urban_garbanzo/`
   - Add tests in `tests/`
   - Use OpenCode commands for assistance

3. **Use OpenCode for help**:
   - `/test` - Run tests with coverage
   - `/lint` - Check code quality
   - `/format` - Auto-format code
   - `/feature` - Plan new features
   - `/review` - Review code quality
   - Type `/` in OpenCode to see all commands

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Initial project setup"
   git push origin main
   ```

Happy coding! 🚀
