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
    assert "database_url" not in payload


async def test_chrome_devtools_probe_hidden_by_default(client) -> None:
    """The Chrome DevTools probe stays hidden unless debug is enabled."""

    response = await client.get("/.well-known/appspecific/com.chrome.devtools.json")
    assert response.status_code == 404


async def test_chrome_devtools_probe_in_debug(monkeypatch) -> None:
    """The Chrome DevTools probe returns minimal metadata in debug mode."""

    monkeypatch.setattr(settings, "debug", True)
    app_instance = create_app()

    async with LifespanManager(app_instance):
        transport = ASGITransport(app=app_instance)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/.well-known/appspecific/com.chrome.devtools.json")

    assert response.status_code == 200
    assert response.json() == {
        "name": settings.app_name,
        "version": settings.app_version,
        "debug": True,
    }


# ---------------------------------------------------------------------------
# Landing page tests
# ---------------------------------------------------------------------------


async def test_landing_page_renders(client) -> None:
    """The root route serves the minimal landing page."""

    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "Open Editor" in body


async def test_landing_page_has_cta_link(client) -> None:
    """The landing page contains a link to /editor."""

    response = await client.get("/")
    assert response.status_code == 200
    assert "/editor" in response.text


async def test_landing_no_submit_form(client) -> None:
    """The landing page does not expose a POST form."""

    response = await client.get("/")
    assert response.status_code == 200
    assert '<form method="post"' not in response.text


# ---------------------------------------------------------------------------
# Editor page tests
# ---------------------------------------------------------------------------


async def test_editor_page_renders(client) -> None:
    """GET /editor returns the editor page with expected elements."""

    response = await client.get("/editor")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "Check prompt" in body
    assert "codemirror" in body.lower()


async def test_editor_check_returns_scores(client, mock_openai_scores) -> None:
    """POST /editor with a valid prompt renders score cards."""

    response = await client.post(
        "/editor",
        data={
            "text": "Create a product requirements prompt with constraints, acceptance criteria, and review checklist.",
            "target_model": "gpt-4.1",
        },
    )
    assert response.status_code == 200
    assert "Total score" in response.text
    assert "Mock LLM rationale." in response.text
    assert "gpt-4.1" in response.text


async def test_editor_check_no_target_model(client, mock_openai_scores) -> None:
    """POST /editor without target_model defaults to 'generic' and still evaluates."""

    response = await client.post(
        "/editor",
        data={
            "text": "Write a detailed system prompt for a coding assistant with strict output constraints.",
        },
    )
    assert response.status_code == 200
    assert "Total score" in response.text
    assert "generic" in response.text


async def test_editor_check_short_prompt(client) -> None:
    """POST /editor with a prompt under 10 chars returns a 422 with an inline error."""

    response = await client.post(
        "/editor",
        data={"text": "short"},
    )
    assert response.status_code == 422
    assert "Prompt text must be at least 10 characters long." in response.text


async def test_editor_check_persists_prompt(client, mock_openai_scores) -> None:
    """Submitting the editor form persists the prompt and evaluation to the DB."""

    response = await client.post(
        "/editor",
        data={
            "text": "Create a reusable incident response prompt for SRE handoffs with measurable acceptance criteria.",
            "target_model": "gpt-4.1",
        },
    )
    assert response.status_code == 200

    prompts_response = await client.get("/api/v1/prompts")
    payload = prompts_response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["target_model"] == "gpt-4.1"


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------


def test_app_creation() -> None:
    """Test that the app can be created without errors."""

    assert app is not None
    assert app.title == "urban-garbanzo"


async def test_editor_bootstraps_fresh_sqlite_db(
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
                "/editor",
                data={
                    "text": "Build an onboarding prompt with measurable success criteria and edge cases.",
                    "target_model": "gpt-4.1",
                },
            )

    assert response.status_code == 200
    assert "Total score" in response.text
