"""Basic application tests."""
import pytest
from fastapi.testclient import TestClient
from urban_garbanzo.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "version" in response.json()


def test_app_creation():
    """Test that the app can be created without errors."""
    assert app is not None
    assert app.title == "urban-garbanzo"
