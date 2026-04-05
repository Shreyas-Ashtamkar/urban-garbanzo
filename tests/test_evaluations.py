"""Evaluation endpoint tests."""

from __future__ import annotations


async def test_get_evaluation_by_id(client) -> None:
    """An evaluation can be fetched directly by its identifier."""

    prompt_response = await client.post(
        "/api/v1/prompts",
        json={"text": "Summarize the API contract and identify validation edge cases."},
    )
    prompt_id = prompt_response.json()["id"]

    evaluation_response = await client.post(f"/api/v1/prompts/{prompt_id}/evaluate")
    evaluation_id = evaluation_response.json()["id"]

    response = await client.get(f"/api/v1/evaluations/{evaluation_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == evaluation_id
    assert payload["prompt_id"] == prompt_id


async def test_prompt_evaluation_history_returns_all_runs(client) -> None:
    """Each evaluation request is retained in prompt history."""

    prompt_response = await client.post(
        "/api/v1/prompts",
        json={"text": "Write instructions that avoid repetition and unsupported claims."},
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
