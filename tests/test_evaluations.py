"""Evaluation endpoint tests."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
from urban_garbanzo.schemas.evaluation import EvaluationRead


async def test_get_evaluation_by_id(client) -> None:
    """An evaluation can be fetched directly by its identifier."""

    prompt_response = await client.post(
        "/api/v1/prompts",
        json={
            "text": "Summarize the API contract and identify validation edge cases.",
            "target_model": "gemini-2.5-flash",
        },
    )
    prompt_id = prompt_response.json()["id"]

    evaluation_response = await client.post(f"/api/v1/prompts/{prompt_id}/evaluate")
    evaluation_id = evaluation_response.json()["id"]

    response = await client.get(f"/api/v1/evaluations/{evaluation_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == evaluation_id
    assert payload["prompt_id"] == prompt_id
    assert payload["scores"]["hallucination_risk"] >= 1.0
    assert payload["scores"]["hallucination_risk"] <= 100.0
    assert payload["heuristic_scores"]["hallucination_risk"] >= 1.0
    assert payload["heuristic_scores"]["hallucination_risk"] <= 100.0
    assert payload["llm_scores"] is None


async def test_get_evaluation_by_id_returns_llm_hallucination_risk(
    client, mock_openai_scores
) -> None:
    """Evaluation detail should expose hallucination risk from the model output."""

    prompt_response = await client.post(
        "/api/v1/prompts",
        json={
            "text": "Map the rollout dependencies, assumptions, validation checks, and known risks.",
            "target_model": "gpt-4.1",
        },
    )
    prompt_id = prompt_response.json()["id"]

    evaluation_response = await client.post(f"/api/v1/prompts/{prompt_id}/evaluate")
    evaluation_id = evaluation_response.json()["id"]

    response = await client.get(f"/api/v1/evaluations/{evaluation_id}")
    assert response.status_code == 200
    payload = response.json()

    assert payload["llm_provider"] == "openai"
    assert payload["llm_scores"]["hallucination_risk"] == 8.0
    assert payload["llm_scores"]["redundancy"] == 11.0


async def test_prompt_evaluation_history_returns_all_runs(client) -> None:
    """Each evaluation request is retained in prompt history."""

    prompt_response = await client.post(
        "/api/v1/prompts",
        json={
            "text": "Write instructions that avoid repetition and unsupported claims.",
            "target_model": "gpt-4.1-mini",
        },
    )
    prompt_id = prompt_response.json()["id"]

    first = await client.post(f"/api/v1/prompts/{prompt_id}/evaluate")
    second = await client.post(f"/api/v1/prompts/{prompt_id}/evaluate")
    assert first.status_code == 200
    assert second.status_code == 200

    response = await client.get(f"/api/v1/prompts/{prompt_id}/evaluations")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 2


def test_evaluation_read_rejects_malformed_llm_scores() -> None:
    """Serialized evaluations should fail validation when llm_scores are malformed."""

    with pytest.raises(ValidationError):
        EvaluationRead.model_validate(
            {
                "id": str(uuid4()),
                "prompt_id": str(uuid4()),
                "scores": {
                    "clarity": 90.0,
                    "correctness": 90.0,
                    "information_density": 90.0,
                    "hallucination_risk": 10.0,
                    "redundancy": 10.0,
                    "total_score": 90.0,
                },
                "heuristic_scores": {
                    "clarity": 90.0,
                    "correctness": 90.0,
                    "information_density": 90.0,
                    "hallucination_risk": 10.0,
                    "redundancy": 10.0,
                },
                "llm_scores": {
                    "clarity": 92.0,
                    "correctness": 89.0,
                    "information_density": 87.0,
                    "redundancy": 11.0,
                },
                "rationale": "Model rationale.",
                "llm_provider": "openai",
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
