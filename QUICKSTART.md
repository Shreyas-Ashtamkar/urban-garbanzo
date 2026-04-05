# Quick Start Guide

urban-garbanzo is now a working FastAPI backend for prompt submission, evaluation, and leaderboard ranking.

## What You Get

- Prompt submission API
- On-demand evaluation pipeline
- Evaluation history per prompt
- Prompt leaderboard
- User leaderboards by best and average score
- Hybrid-ready heuristic + LLM evaluation architecture

## One-Minute Setup

### macOS/Linux

```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements-dev.txt && cp .env.example .env && docker compose up -d db && python -m pytest
```

### Windows PowerShell

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements-dev.txt; copy .env.example .env; docker compose up -d db; python -m pytest
```

## First Run

### 1. Install dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. Create `.env`

Windows PowerShell:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

### 3. Start Postgres

```bash
docker compose up -d db
```

### 4. Initialize the database schema

```bash
python -m aerich init-db
```

### 5. Start the API

```bash
make run
```

### 6. Run tests

```bash
python -m pytest
```

## Key Endpoints

- `GET /health`
- `POST /api/v1/prompts`
- `GET /api/v1/prompts`
- `GET /api/v1/prompts/{prompt_id}`
- `POST /api/v1/prompts/{prompt_id}/evaluate`
- `GET /api/v1/prompts/{prompt_id}/evaluations`
- `GET /api/v1/evaluations/{evaluation_id}`
- `GET /api/v1/leaderboard/prompts`
- `GET /api/v1/leaderboard/users/best`
- `GET /api/v1/leaderboard/users/average`

Docs:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

## Common Commands

```bash
make install-dev
make env
make run
make test
make lint
make format
make typecheck
make migrate
make db-upgrade
```

## Core Files

```text
src/urban_garbanzo/
├── config.py
├── database.py
├── dependencies.py
├── exceptions.py
├── main.py
├── models/
├── routers/
├── schemas/
└── services/
```

## Environment Highlights

Important values in `.env.example`:

- `DATABASE_URL`
- `DATABASE_GENERATE_SCHEMAS`
- `DEBUG`
- `CORS_ORIGINS`
- `LLM_PROVIDER`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `HEURISTIC_WEIGHT`
- `LLM_WEIGHT`

## LLM Modes

Heuristics only:

```env
LLM_PROVIDER=none
```

OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

Anthropic:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
```

## Current State

- Auth is not implemented yet
- Tests run against temporary SQLite databases
- Development and production target Postgres
- Aerich is configured for schema migrations

## Next Useful Steps

1. Start the API and inspect `/docs`
2. Create a prompt and evaluate it
3. Enable an LLM provider if you want hybrid scoring
4. Add migrations as models evolve
