"""Heuristic scoring tests."""

from __future__ import annotations

from urban_garbanzo.services.heuristics import score_prompt


def test_score_prompt_returns_all_dimensions() -> None:
    """Heuristic scoring returns each supported dimension."""

    scores = score_prompt(
        "Write a concise plan with constraints, acceptance criteria, and examples."
    )
    assert set(scores) == {
        "clarity",
        "correctness",
        "information_density",
        "hallucination_risk",
        "redundancy",
    }
    assert all(1.0 <= value <= 100.0 for value in scores.values())


def test_redundancy_score_increases_for_repeated_text() -> None:
    """Highly repetitive text should have a higher redundancy score."""

    repetitive = score_prompt("Repeat this. Repeat this. Repeat this. Repeat this.")
    concise = score_prompt("Describe the deployment checklist in one concise paragraph.")
    assert repetitive["redundancy"] > concise["redundancy"]
