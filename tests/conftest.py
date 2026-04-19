"""Shared async test fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from urban_garbanzo.config import settings
from urban_garbanzo.main import create_app


@pytest.fixture
async def client(monkeypatch: pytest.MonkeyPatch, tmp_path) -> AsyncIterator[AsyncClient]:
    """Create an async test client backed by a temporary SQLite database."""

    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setattr(settings, "database_generate_schemas", True)
    monkeypatch.setattr(settings, "llm_provider", "none")
    app = create_app()

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
            yield async_client


@pytest.fixture
def mock_openai_scores(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the OpenAI provider to return deterministic scores."""

    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", SecretStr("test-key"))

    from urban_garbanzo.services.llm import OpenAIProvider

    async def fake_score(self: OpenAIProvider, prompt_text: str, target_model: str):
        del self
        del prompt_text
        del target_model
        from urban_garbanzo.services.llm import LLMScoreResult

        return LLMScoreResult(
            scores={
                "clarity": 92.0,
                "correctness": 89.0,
                "information_density": 87.0,
                "hallucination_risk": 8.0,
                "redundancy": 11.0,
            },
            rationale="Mock LLM rationale.",
        )

    monkeypatch.setattr(OpenAIProvider, "score", fake_score)
