"""Prompt endpoint tests."""

from __future__ import annotations


async def test_create_and_get_prompt(client) -> None:
    """Prompts can be created and retrieved with their metadata."""

    create_response = await client.post(
        "/api/v1/prompts",
        json={
            "text": "Write a concise onboarding guide for new contributors.",
            "target_model": "gpt-4.1",
            "submitter_tag": "alice",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["submitter_tag"] == "alice"
    assert created["latest_evaluation"] is None

    fetch_response = await client.get(f"/api/v1/prompts/{created['id']}")
    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert fetched["id"] == created["id"]
    assert fetched["text"] == "Write a concise onboarding guide for new contributors."
    assert fetched["target_model"] == "gpt-4.1"


async def test_list_prompts_returns_pagination(client) -> None:
    """Prompt listing includes pagination metadata."""

    for index in range(3):
        response = await client.post(
            "/api/v1/prompts",
            json={
                "text": f"Create a short project summary for sprint item {index}.",
                "target_model": "gemini-2.5-pro",
            },
        )
        assert response.status_code == 201

    response = await client.get("/api/v1/prompts?page=1&size=2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 3
    assert payload["page"] == 1
    assert payload["size"] == 2
    assert len(payload["items"]) == 2


async def test_evaluate_prompt_persists_scores(client) -> None:
    """Prompt evaluation stores blended scores and returns them."""

    prompt_response = await client.post(
        "/api/v1/prompts",
        json={
            "text": "Explain the rollout plan with owners, dates, and measurable success criteria.",
            "target_model": "claude-3.7-sonnet",
        },
    )
    prompt_id = prompt_response.json()["id"]

    evaluation_response = await client.post(f"/api/v1/prompts/{prompt_id}/evaluate")
    assert evaluation_response.status_code == 200
    payload = evaluation_response.json()
    assert payload["prompt_id"] == prompt_id
    assert payload["scores"]["total_score"] >= 1.0
    assert payload["llm_provider"] == "none"
    assert payload["heuristic_scores"]


async def test_delete_prompt_soft_deletes_record(client) -> None:
    """Soft-deleted prompts are hidden from subsequent fetches."""

    prompt_response = await client.post(
        "/api/v1/prompts",
        json={
            "text": "Draft a customer-facing announcement for next week's release.",
            "target_model": "gpt-4o-mini",
        },
    )
    prompt_id = prompt_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/prompts/{prompt_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/prompts/{prompt_id}")
    assert get_response.status_code == 404
