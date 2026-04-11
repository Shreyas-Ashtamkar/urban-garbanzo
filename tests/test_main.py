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


async def test_editor_page_uses_module_script_for_codemirror(client) -> None:
    """The editor should not load an ES module through a classic script tag."""

    response = await client.get("/editor")
    assert response.status_code == 200
    body = response.text
    assert '<script type="module">' in body
    assert 'src="https://cdn.jsdelivr.net/npm/@codemirror/state@6/dist/index.js"' not in body


async def test_editor_page_has_results_container(client) -> None:
    """GET /editor page contains the #results-container element for JS-rendered scores."""

    response = await client.get("/editor")
    assert response.status_code == 200
    assert 'id="results-container"' in response.text


async def test_editor_page_has_loading_state(client) -> None:
    """GET /editor page contains the #loading-state skeleton element."""

    response = await client.get("/editor")
    assert response.status_code == 200
    assert 'id="loading-state"' in response.text


async def test_editor_page_button_enabled_by_default(client) -> None:
    """The Check prompt button is not disabled on initial page load."""

    response = await client.get("/editor")
    assert response.status_code == 200
    body = response.text
    # The button must be present and must NOT carry a disabled attribute
    assert 'id="check-button"' in body
    assert "check-button" in body
    # A disabled attribute on the check button would look like: disabled
    # We verify the button tag itself doesn't contain 'disabled'
    import re

    button_match = re.search(r'<button[^>]*id="check-button"[^>]*>', body)
    assert button_match is not None
    assert "disabled" not in button_match.group(0)


async def test_editor_check_returns_editor_page(client) -> None:
    """POST /editor re-renders the editor (evaluation is handled via JS + REST API)."""

    response = await client.post(
        "/editor",
        data={
            "text": "Create a product requirements prompt with constraints.",
            "target_model": "gpt-4.1",
        },
    )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # The page should still have the editor elements
    assert "Check prompt" in response.text
    assert 'id="results-container"' in response.text


async def test_editor_check_no_target_model(client) -> None:
    """POST /editor without target_model still returns the editor page."""

    response = await client.post(
        "/editor",
        data={
            "text": "Write a detailed system prompt for a coding assistant with strict output constraints.",
        },
    )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Check prompt" in response.text


async def test_editor_check_persists_prompt(client, mock_openai_scores) -> None:
    """Prompts submitted via the REST API are persisted to the DB."""

    response = await client.post(
        "/api/v1/prompts",
        json={
            "text": "Create a reusable incident response prompt for SRE handoffs with measurable acceptance criteria.",
            "target_model": "gpt-4.1",
        },
    )
    assert response.status_code == 201
    prompt_id = response.json()["id"]

    eval_response = await client.post(f"/api/v1/prompts/{prompt_id}/evaluate")
    assert eval_response.status_code == 200

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
                "/api/v1/prompts",
                json={
                    "text": "Build an onboarding prompt with measurable success criteria and edge cases.",
                    "target_model": "gpt-4.1",
                },
            )

    assert response.status_code == 201
