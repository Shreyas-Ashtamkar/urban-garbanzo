"""Evaluator service tests."""

from __future__ import annotations

from urban_garbanzo.config import Settings
from urban_garbanzo.services.evaluator import EvaluatorService, blend_scores, compute_weighted_total


def test_blend_scores_uses_weighted_average() -> None:
    """Blended scores should reflect the configured weighting."""

    scores = blend_scores(
        heuristic_scores={
            "clarity": 50,
            "correctness": 50,
            "information_density": 50,
            "hallucination_risk": 50,
            "redundancy": 50,
        },
        llm_scores={
            "clarity": 100,
            "correctness": 100,
            "information_density": 100,
            "hallucination_risk": 100,
            "redundancy": 100,
        },
        heuristic_weight=0.25,
        llm_weight=0.75,
    )
    assert scores["clarity"] == 87.5


def test_weighted_total_inverts_risk_dimensions() -> None:
    """Total score should reward low risk and low redundancy."""

    total = compute_weighted_total(
        {
            "clarity": 90,
            "correctness": 90,
            "information_density": 90,
            "hallucination_risk": 10,
            "redundancy": 10,
        }
    )
    assert total == 90.0


async def test_evaluator_service_uses_heuristics_when_llm_disabled() -> None:
    """The evaluator falls back to heuristics-only mode when no provider is configured."""

    service = EvaluatorService(Settings(llm_provider="none", database_url="sqlite://:memory:"))
    result = await service.evaluate(
        "Write a rollout plan with owners, dependencies, mitigations, and success metrics."
    )
    assert result.llm_provider == "none"
    assert result.heuristic_scores
    assert result.llm_scores == {}
