# Development Setup Guide

This guide reflects the current implementation of urban-garbanzo: a FastAPI app with a built-in UI, Tortoise ORM, SQLite by default (PostgreSQL for development/production), Aerich migrations, unit tests, and Playwright browser coverage.

## Requirements

- Python 3.10+
- Docker Desktop or local PostgreSQL
- Git

## 1. Clone the Repository

```bash
git clone https://github.com/Shreyas-Ashtamkar/urban-garbanzo.git
cd urban-garbanzo
```

## 2. Create a Virtual Environment

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

## 3. Install Dependencies

```bash
pip install -r requirements-dev.txt
```

Or use:

```bash
make install-dev
```

## 4. Create the Environment File

Windows PowerShell:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Important variables in `.env`:

- `DATABASE_URL`
- `DATABASE_GENERATE_SCHEMAS`
- `DEBUG`
- `CORS_ORIGINS`
- `LLM_PROVIDER`
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

## 5. Start PostgreSQL

The repository includes a compose file for local Postgres.

```bash
docker compose up -d db
```

Default database credentials from `.env.example`:

```env
DATABASE_URL=postgres://ug_user:ug_pass@localhost:5432/urban_garbanzo
```

## 6. Create the Schema

Aerich is already configured in `pyproject.toml`. For a fresh database, run:

```bash
python -m aerich init-db
```

For later model changes:

```bash
python -m aerich migrate --name "describe_change"
python -m aerich upgrade
```

Make targets are also available:

```bash
make migrate
make db-upgrade
```

## 7. Run the API

```bash
make run
```

Available endpoints:

- Landing page: `http://localhost:8000/`
- Editor: `http://localhost:8000/editor`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

## 8. Use the Web UI

The app is built around a server-rendered product UI backed by the JSON API.

### Landing page

- `GET /` renders the marketing and workflow overview page
- The landing page links into the editor, shows sample prompt evaluations, and explains the review flow
- It is informational only and does not submit prompts directly

### Editor page

- `GET /editor` renders a two-pane markdown editor and live preview
- The editor uses CodeMirror 6 for the markdown pane and `marked` for preview rendering
- When the text field is empty, the preview starts empty and updates as the editor changes

### Editor form behavior

- The editor UI uses JavaScript to create prompts with `POST /api/v1/prompts`
- After a prompt is created, the UI triggers evaluation with `POST /api/v1/prompts/{id}/evaluate`
- `target_model` is optional in the form UI and defaults to `generic` when blank
- Prompt text is trimmed before validation and storage
- Prompt text must be at least `10` characters
- Prompt text must be `10,000` characters or fewer
- Validation errors come from the API endpoints and are surfaced by the UI during the async flow

## 9. Run the Tests

Unit tests:

```bash
python -m pytest tests
```

Browser E2E tests:

```bash
python -m playwright install chromium
python -m pytest --override-ini addopts="--strict-markers -v --tb=short" tests_e2e
```

Notes:

- Tests do not require Postgres
- Tests use temporary SQLite databases
- The app itself is configured for Postgres in development

## Common Commands

```bash
make run
make test
make test-e2e
make test-all
make lint
make format
make typecheck
make precommit
make migrate
make db-upgrade
```

Direct equivalents:

```bash
python -m pytest tests
python -m pytest --override-ini addopts="--strict-markers -v --tb=short" tests_e2e
python -m ruff check src tests tests_e2e
python -m mypy src
python -m black src tests tests_e2e
python -m aerich migrate --name "describe_change"
python -m aerich upgrade
```

## Implemented API Surface

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

## Implemented UI Surface

- `GET /` renders the landing page
- `GET /editor` renders the markdown editor
- `POST /editor` re-renders the editor page; browser-based evaluation is performed via the JSON API

## LLM Configuration

Set one of the following modes in `.env`:

Heuristics only:

```env
LLM_PROVIDER=none
```

OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Anthropic:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-5-haiku-latest
```

## Troubleshooting

### PostgreSQL connection errors

- Confirm Docker is running
- Confirm `docker compose up -d db` succeeded
- Confirm `DATABASE_URL` matches `.env.example`

### Migration errors

- Ensure the database container is running
- Ensure `urban_garbanzo.database.TORTOISE_ORM` is importable

### Port 8000 already in use

Change `API_PORT` in `.env` or start uvicorn manually on another port.

### LLM evaluation errors

- Verify `LLM_PROVIDER`
- Verify the matching API key is set
- Set `LLM_PROVIDER=none` to fall back to heuristics-only mode

## Next Steps

1. Start the API and inspect `/` and `/editor`
2. Inspect `/docs` for the JSON API surface
3. Create prompts and trigger evaluations
4. Generate follow-up migrations as models evolve
5. Add auth when anonymous submission is no longer sufficient
