"""Basic application tests."""

from pathlib import Path

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from urban_garbanzo.config import settings
from urban_garbanzo.main import app, create_app


async def test_health_check(client):
    """Test the health check endpoint."""

    response = await client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "version" in payload
    assert payload["llm_provider"] == "none"


async def test_root_page_renders_ui(client) -> None:
    """The root route serves the server-rendered evaluation UI."""

    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "Evaluate prompt" in body
    assert "Target model" in body


async def test_root_submission_creates_and_evaluates_prompt(client, mock_openai_scores) -> None:
    """Submitting the root form persists a prompt and renders evaluation results."""

    response = await client.post(
        "/",
        data={
            "text": "Create a product requirements prompt with constraints, acceptance criteria, and review checklist.",
            "target_model": "gpt-4.1",
        },
    )
    assert response.status_code == 200
    assert "Total score" in response.text
    assert "Mock LLM rationale." in response.text
    assert "gpt-4.1" in response.text

    prompts_response = await client.get("/api/v1/prompts")
    payload = prompts_response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["target_model"] == "gpt-4.1"


async def test_root_submission_rejects_short_target_model(client) -> None:
    """The root form returns a validation-style error for invalid target models."""

    response = await client.post(
        "/",
        data={
            "text": "Create a reusable incident response prompt for SRE handoffs.",
            "target_model": " ",
        },
    )
    assert response.status_code == 422
    assert "Target model must be at least 2 characters long." in response.text


def test_app_creation() -> None:
    """Test that the app can be created without errors."""

    assert app is not None
    assert app.title == "urban-garbanzo"


async def test_root_submission_bootstraps_fresh_sqlite_db(
    monkeypatch,
    tmp_path: Path,
    mock_openai_scores,
) -> None:
    """A fresh local SQLite database should not require manual schema creation."""

    db_path = tmp_path / "fresh.sqlite3"
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setattr(settings, "database_generate_schemas", False)
    app_instance = create_app()

    async with LifespanManager(app_instance):
        transport = ASGITransport(app=app_instance)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/",
                data={
                    "text": "Build an onboarding prompt with measurable success criteria and edge cases.",
                    "target_model": "gpt-4.1",
                },
            )

    assert response.status_code == 200
    assert "Total score" in response.text
