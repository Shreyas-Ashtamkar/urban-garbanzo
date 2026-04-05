"""Basic application tests."""

from urban_garbanzo.main import app


async def test_health_check(client):
    """Test the health check endpoint."""

    response = await client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "version" in payload
    assert payload["llm_provider"] == "none"


def test_app_creation() -> None:
    """Test that the app can be created without errors."""

    assert app is not None
    assert app.title == "urban-garbanzo"
