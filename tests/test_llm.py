"""LLM provider factory and payload normalization tests."""

from __future__ import annotations

from urban_garbanzo.config import Settings
from urban_garbanzo.services.llm import OpenAIProvider, create_llm_provider, normalize_llm_payload


def test_create_llm_provider_returns_openai_provider() -> None:
    """Configured OpenAI settings should produce an OpenAI provider."""

    provider = create_llm_provider(
        Settings(
            llm_provider="openai",
            openai_api_key="test-key",
            database_url="sqlite://:memory:",
        )
    )
    assert isinstance(provider, OpenAIProvider)


def test_normalize_llm_payload_clamps_scores() -> None:
    """LLM payload normalization clamps scores into the supported range."""

    result = normalize_llm_payload(
        {
            "clarity": 101,
            "correctness": 88,
            "information_density": 77,
            "hallucination_risk": 0,
            "redundancy": 12,
            "rationale": "Looks good",
        }
    )
    assert result.scores["clarity"] == 100.0
    assert result.scores["hallucination_risk"] == 1.0
    assert result.rationale == "Looks good"
