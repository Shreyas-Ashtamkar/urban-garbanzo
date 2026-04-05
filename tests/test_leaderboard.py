"""Leaderboard endpoint tests."""

from __future__ import annotations

from typing import Any, cast


async def seed_scored_prompt(client, text: str, submitter_tag: str | None = None) -> dict[str, Any]:
    """Create and evaluate a prompt for leaderboard tests."""

    response = await client.post(
        "/api/v1/prompts",
        json={"text": text, "submitter_tag": submitter_tag},
    )
    prompt = cast(dict[str, Any], response.json())
    await client.post(f"/api/v1/prompts/{prompt['id']}/evaluate")
    return prompt


async def test_prompt_leaderboard_returns_ranked_prompts(client) -> None:
    """Prompt leaderboard returns ranked prompt entries."""

    await seed_scored_prompt(
        client, "Provide a release checklist with clear acceptance criteria.", "alice"
    )
    await seed_scored_prompt(client, "Generate a testing plan with risks and mitigations.", "bob")

    response = await client.get("/api/v1/leaderboard/prompts?limit=5")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["rank"] == 1


async def test_user_best_leaderboard_groups_by_submitter(client) -> None:
    """User best leaderboard groups prompt scores by submitter tag."""

    await seed_scored_prompt(client, "Create a launch summary with owners and deadlines.", "alice")
    await seed_scored_prompt(client, "Create a second launch summary with more evidence.", "alice")
    await seed_scored_prompt(client, "Outline a migration strategy with rollback steps.", "bob")

    response = await client.get("/api/v1/leaderboard/users/best")
    assert response.status_code == 200
    payload = response.json()
    assert {entry["submitter_tag"] for entry in payload} == {"alice", "bob"}


async def test_user_average_leaderboard_returns_prompt_counts(client) -> None:
    """Average leaderboard exposes each user's evaluated prompt count."""

    await seed_scored_prompt(
        client, "Document the happy path, failure path, and retry flow.", "alice"
    )
    await seed_scored_prompt(
        client, "Document the support escalation path with ownership.", "alice"
    )

    response = await client.get("/api/v1/leaderboard/users/average")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["submitter_tag"] == "alice"
    assert payload[0]["prompt_count"] == 2
