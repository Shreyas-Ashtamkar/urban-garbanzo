---
description: Bootstrap initial Python project structure
agent: build
---

Set up the initial project structure for urban-garbanzo, a Python-based prompt evaluation platform.

Create the following:

1. **Project structure**:
   - `src/urban_garbanzo/` - main package
   - `tests/` - test directory with pytest
   - `docs/` - documentation
   - Root-level config files

2. **Core configuration files**:
   - `pyproject.toml` - project metadata, dependencies, build config
   - `requirements.txt` - pinned dependencies for reproducibility
   - `setup.py` - alternative packaging setup
   - `pytest.ini` - pytest configuration
   - `.env.example` - environment variables template

3. **Development files**:
   - `Makefile` - common dev commands (install, test, lint, format)
   - `pre-commit` config if appropriate
   - `.github/workflows/` - CI/CD templates (test, lint)

4. **Initial code**:
   - `src/urban_garbanzo/__init__.py` - package init with version
   - `src/urban_garbanzo/main.py` - entry point stub
   - `tests/__init__.py` - test package init

5. **Documentation**:
   - Update README.md with installation and usage instructions
   - Create CONTRIBUTING.md for contributor guidelines

Base the tech stack on what's most appropriate:
- Web framework: FastAPI (modern) or Flask (simple)
- Database: PostgreSQL or SQLite
- Testing: pytest with coverage
- Linting: ruff or flake8
- Formatting: black
- Type checking: mypy

Ask for clarification on architectural choices if unclear.
