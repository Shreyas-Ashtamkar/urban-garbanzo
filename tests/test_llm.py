"""LLM provider factory and payload normalization tests."""

from __future__ import annotations

import pytest
from urban_garbanzo.config import Settings
from urban_garbanzo.exceptions import EvaluationFailed
from urban_garbanzo.services.llm import (
    SYSTEM_PROMPT,
    OpenAIProvider,
    create_llm_provider,
    normalize_llm_payload,
)


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


def test_normalize_llm_payload_accepts_in_range_scores() -> None:
    """LLM payload normalization keeps valid scores on the supported range."""

    result = normalize_llm_payload(
        {
            "clarity": 99.2,
            "correctness": 88,
            "information_density": 77,
            "hallucination_risk": 8,
            "redundancy": 12,
            "rationale": "Looks good",
        }
    )
    assert result.scores["clarity"] == 99.2
    assert result.scores["hallucination_risk"] == 8.0
    assert result.rationale == "Looks good"


def test_normalize_llm_payload_rejects_out_of_range_scores() -> None:
    """LLM payload normalization rejects scores outside the supported range."""

    with pytest.raises(EvaluationFailed, match="hallucination_risk"):
        normalize_llm_payload(
            {
                "clarity": 91,
                "correctness": 88,
                "information_density": 77,
                "hallucination_risk": 0,
                "redundancy": 12,
            }
        )


def test_normalize_llm_payload_requires_hallucination_risk() -> None:
    """LLM payloads must include hallucination risk with the other score fields."""

    with pytest.raises(EvaluationFailed):
        normalize_llm_payload(
            {
                "clarity": 91,
                "correctness": 88,
                "information_density": 77,
                "redundancy": 12,
            }
        )


def test_system_prompt_includes_score_band_examples() -> None:
    """The LLM system prompt should anchor low, medium, and high quality cases."""

    assert 'Low — "hello hello hello hello"' in SYSTEM_PROMPT
    assert "clarity: 3, correctness: 2" in SYSTEM_PROMPT
    assert 'Medium — "Summarize this article in bullet points."' in SYSTEM_PROMPT
    assert "clarity: 65, correctness: 78" in SYSTEM_PROMPT
    assert "High — " in SYSTEM_PROMPT
    assert "clarity: 92, correctness: 93" in SYSTEM_PROMPT
    # Inversion direction must be explicit
    assert "Higher is worse for hallucination_risk and redundancy" in SYSTEM_PROMPT
    # Anti-inference rule
    assert "Judge only what is written" in SYSTEM_PROMPT
    # No markdown rule
    assert "No markdown" in SYSTEM_PROMPT
    # Structured rationale
    assert "top strength, top weakness, one concrete fix" in SYSTEM_PROMPT
