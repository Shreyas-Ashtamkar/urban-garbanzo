# urban-garbanzo

**Stop guessing if your prompts work.** urban-garbanzo is a FastAPI app with a built-in prompt review UI, evaluation history, and leaderboards for prompt quality.

## Overview

urban-garbanzo is a UI-first prompt evaluation app backed by FastAPI and Tortoise ORM. The current implementation supports:

- A landing page and in-browser markdown editor
- Prompt submission and retrieval
- On-demand prompt evaluation
- Evaluation history per prompt
- Prompt leaderboard
- User leaderboard by best score
- User leaderboard by average score

Authentication is intentionally not included yet. Prompt ownership is tracked with an optional anonymous `submitter_tag`.

## Scoring Model

Each evaluation produces scores from `1.00` to `100.00` for:

- `clarity`
- `correctness`
- `information_density`
- `hallucination_risk`
- `redundancy`

The evaluator currently supports a hybrid architecture:

- Heuristic scoring is always available
- LLM scoring is optional and pluggable
- Supported LLM providers: OpenAI, Anthropic, or `none`

`hallucination_risk` and `redundancy` are interpreted as lower-is-better in the final weighted total.

## Tech Stack

- FastAPI
- Tortoise ORM
- SQLite in-memory by default; PostgreSQL for development and production
- Aerich for migrations
- pytest + pytest-asyncio + Playwright
- Ruff
- Black
- mypy

## Project Structure

```text
urban-garbanzo/
├── src/urban_garbanzo/
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── exceptions.py
│   ├── main.py
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   └── services/
├── tests/
├── docs/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── Makefile
```

## Prerequisites

- Python 3.10+
- Docker Desktop or a local PostgreSQL instance
- Git

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Shreyas-Ashtamkar/urban-garbanzo.git
cd urban-garbanzo
```

### 2. Create and activate a virtual environment

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements-dev.txt
```

### 4. Create `.env`

Windows PowerShell:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

### 5. Start PostgreSQL with Docker Compose

```bash
docker compose up -d db
```

The default `.env.example` already points at this container:

```env
DATABASE_URL=postgres://ug_user:ug_pass@localhost:5432/urban_garbanzo
```

### 6. Initialize the database schema

```bash
python -m aerich init-db
```

Aerich is already configured in `pyproject.toml`. After the initial schema setup, future model changes use:

```bash
python -m aerich migrate --name "describe_change"
python -m aerich upgrade
```

### 7. Start the API

```bash
make run
```

Docs and health endpoints:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI: `http://localhost:8000/openapi.json`
- Health: `http://localhost:8000/health`

## Environment Variables

Key settings from `.env.example`:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `DATABASE_GENERATE_SCHEMAS` | Dev-only auto schema generation toggle |
| `API_HOST` | Uvicorn host |
| `API_PORT` | Uvicorn port |
| `DEBUG` | FastAPI debug flag |
| `CORS_ORIGINS` | Allowed origins list |
| `LLM_PROVIDER` | `none`, `openai`, or `anthropic` |
| `OPENAI_MODEL` | OpenAI model name |
| `ANTHROPIC_MODEL` | Anthropic model name |
| `HEURISTIC_WEIGHT` | Weight for heuristic scoring |
| `LLM_WEIGHT` | Weight for LLM scoring |

If you want LLM scoring enabled, set one of:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

or:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
```

## API Endpoints

### Health

- `GET /health`

### Prompts

- `POST /api/v1/prompts`
- `GET /api/v1/prompts`
- `GET /api/v1/prompts/{prompt_id}`
- `POST /api/v1/prompts/{prompt_id}/evaluate`
- `DELETE /api/v1/prompts/{prompt_id}`

### Evaluations

- `GET /api/v1/evaluations/{evaluation_id}`
- `GET /api/v1/prompts/{prompt_id}/evaluations`

### Leaderboards

- `GET /api/v1/leaderboard/prompts`
- `GET /api/v1/leaderboard/users/best`
- `GET /api/v1/leaderboard/users/average`

## Example Requests

Create a prompt:

```bash
curl -X POST http://localhost:8000/api/v1/prompts \
  -H "Content-Type: application/json" \
  -d '{"text":"Write a release note with risks, owners, and rollback steps.","submitter_tag":"alice"}'
```

Evaluate a prompt:

```bash
curl -X POST http://localhost:8000/api/v1/prompts/<prompt-id>/evaluate
```

List prompt leaderboard:

```bash
curl "http://localhost:8000/api/v1/leaderboard/prompts?limit=10"
```

## Development Commands

| Command | Description |
|---|---|
| `make install-dev` | Install development dependencies |
| `make env` | Copy `.env.example` to `.env` |
| `make run` | Start the FastAPI dev server |
| `make test` | Run unit tests with coverage |
| `make test-e2e` | Run Playwright browser tests |
| `make test-all` | Run unit and browser tests |
| `make lint` | Run Ruff and mypy |
| `make format` | Run Black and Ruff autofix |
| `make migrate` | Create a new Aerich migration |
| `make db-upgrade` | Apply migrations |

## Testing

### Unit Tests

```bash
python -m pytest tests
```

The test suite uses temporary SQLite databases for isolation and speed. Development and production remain Postgres-oriented.

### Browser E2E Tests

The browser suite uses Playwright against a live FastAPI subprocess.
Install the Chromium browser once before running E2E tests:

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium
```

Then run the browser suite explicitly:

```bash
python -m pytest --override-ini addopts="--strict-markers -v --tb=short" tests_e2e
```

The browser tests boot the FastAPI app with SQLite and `LLM_PROVIDER=none`, then run deterministic browser coverage for `/` and `/editor`.

## Quality Checks

```bash
python -m ruff check src tests tests_e2e
python -m mypy src
python -m black src tests tests_e2e
python -m pytest tests
```

## Current Limitations

- No authentication yet
- No background job queue for evaluations
- No rate limiting

## Contributing

See `CONTRIBUTING.md` for workflow and code quality expectations.

## License

GNU GPL v2.0. See `LICENSE`.
