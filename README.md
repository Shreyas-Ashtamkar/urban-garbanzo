# urban-garbanzo

**Stop guessing if your prompts work.** Get instant ratings on clarity, correctness, information density, hallucination risk, and redundancy. Build better AI workflows, climb the leaderboard, and prove your skills to the world.

## Overview

urban-garbanzo is a platform designed to help you evaluate and improve your AI prompts. Instead of manually testing and iterating on prompts without concrete feedback, this tool provides instant, objective ratings across multiple dimensions to help you optimize your AI interactions and workflows.

## Features

- **Instant Prompt Ratings** - Get real-time feedback on your prompts across multiple criteria:
  - Clarity: How well-structured and understandable is your prompt?
  - Correctness: Does your prompt lead to accurate results?
  - Information Density: How efficiently is information conveyed?
  - Hallucination Risk: What's the likelihood of the AI generating false information?
  - Redundancy: Are there unnecessary repetitions or verbose elements?

- **Leaderboard System** - Compete with others and prove your prompt engineering skills
- **Workflow Optimization** - Build and refine better AI workflows based on data-driven feedback
- **Community-Driven** - Learn from top performers and contribute to the collective knowledge

## Tech Stack

- **Framework**: FastAPI (async-ready, modern Python web framework)
- **Database**: PostgreSQL (production-ready relational database)
- **ORM**: Tortoise ORM (async-first Python ORM)
- **Testing**: pytest with coverage
- **Linting**: ruff (fast Python linter)
- **Formatting**: black (code formatter)
- **Type Checking**: mypy

## Prerequisites

- **Python**: 3.10 or higher
- **PostgreSQL**: 13+ (or use SQLite for development)
- **pip**: Python package manager
- **Git**: For version control

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Shreyas-Ashtamkar/urban-garbanzo.git
cd urban-garbanzo
```

### 2. Create a Python virtual environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Or with development tools
pip install -r requirements-dev.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and configure:
- `DATABASE_URL`: PostgreSQL connection string (default: SQLite for development)
- `API_PORT`: Port for dev server (default: 8000)
- `API_DEBUG`: Debug mode (default: false)

### 5. Verify installation

```bash
pytest              # Run tests
uvicorn urban_garbanzo.main:app --reload  # Start dev server
```

## Quick Start

### Using Make (recommended)

```bash
# Install everything and get started
make install-dev
make env           # Create .env file
make run           # Start dev server

# In another terminal, run tests
make test
```

### Common Commands

| Command | Description |
|---------|-------------|
| `make run` | Start development server (http://localhost:8000) |
| `make test` | Run test suite with coverage |
| `make lint` | Check code quality (ruff, mypy) |
| `make format` | Auto-format code (black, ruff) |
| `make precommit` | Run pre-commit hooks |
| `make clean` | Remove build artifacts and cache |

### Direct Commands (without Make)

```bash
# Start development server
uvicorn urban_garbanzo.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Check code quality
ruff check src tests
mypy src

# Format code
black src tests
ruff check --fix src tests
```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and write tests:
   ```bash
   # Edit files, then run tests
   make test
   ```

3. **Check code quality**:
   ```bash
   make lint
   make format
   ```

4. **Commit with clear messages**:
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push and create a Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Project Structure

```
urban-garbanzo/
├── src/urban_garbanzo/       # Main application package
│   ├── __init__.py           # Package metadata
│   ├── main.py               # FastAPI app factory
│   ├── config.py             # Settings & configuration
│   └── ...                   # Feature modules
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_main.py          # Application tests
│   └── ...                   # Feature tests
├── docs/                     # Documentation
├── .github/workflows/        # CI/CD pipelines
├── pyproject.toml            # Project metadata & build config
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── pytest.ini                # Pytest configuration
├── Makefile                  # Development commands
├── .pre-commit-config.yaml   # Pre-commit hooks
└── README.md                 # This file
```

## API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc (ReDoc)
- **OpenAPI schema**: http://localhost:8000/openapi.json

## Database Setup (PostgreSQL)

### Development with PostgreSQL

1. **Install PostgreSQL** (or use Docker):
   ```bash
   # macOS
   brew install postgresql

   # Or use Docker
   docker run --name urban-garbanzo-db -e POSTGRES_PASSWORD=password -d postgres:15
   ```

2. **Create database**:
   ```bash
   createdb urban_garbanzo
   ```

3. **Update .env**:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/urban_garbanzo
   ```

### Development with SQLite (simpler)

SQLite is configured by default in development. No additional setup needed!

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_main.py

# Run with coverage report
pytest --cov=urban_garbanzo

# Run in watch mode (requires pytest-watch)
pytest-watch
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Setting up your development environment
- Code style and formatting
- Testing requirements
- Pull request process

## License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

## Related Resources

- GitHub: https://github.com/Shreyas-Ashtamkar/urban-garbanzo
