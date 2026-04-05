"""Prompt evaluation orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from starlette.concurrency import run_in_threadpool

from urban_garbanzo.config import Settings
from urban_garbanzo.services import heuristics
from urban_garbanzo.services.llm import create_llm_provider

INVERTED_SCORE_FIELDS = {"hallucination_risk", "redundancy"}


def to_decimal(value: float) -> Decimal:
    """Convert floats into fixed 2-decimal decimal values for storage."""

    return Decimal(f"{value:.2f}")


def normalize_score(value: float) -> float:
    """Clamp and round a score value to the supported range."""

    return heuristics.clamp_score(value)


def blend_scores(
    heuristic_scores: dict[str, float],
    llm_scores: dict[str, float] | None,
    heuristic_weight: float,
    llm_weight: float,
) -> dict[str, float]:
    """Blend heuristic and LLM scores according to configured weights."""

    if not llm_scores:
        return {field: normalize_score(score) for field, score in heuristic_scores.items()}

    total_weight = heuristic_weight + llm_weight
    if total_weight <= 0:
        return {field: normalize_score(score) for field, score in llm_scores.items()}

    normalized_heuristic_weight = heuristic_weight / total_weight
    normalized_llm_weight = llm_weight / total_weight
    blended: dict[str, float] = {}
    for field in heuristics.SCORE_FIELDS:
        blended[field] = normalize_score(
            heuristic_scores[field] * normalized_heuristic_weight
            + llm_scores[field] * normalized_llm_weight
        )
    return blended


def compute_weighted_total(scores: dict[str, float]) -> float:
    """Compute the public total score from the five dimension scores."""

    total = (
        scores["clarity"] * 0.25
        + scores["correctness"] * 0.25
        + scores["information_density"] * 0.20
        + (100.0 - scores["hallucination_risk"]) * 0.15
        + (100.0 - scores["redundancy"]) * 0.15
    )
    return normalize_score(total)


@dataclass(slots=True)
class EvaluationResult:
    """Completed evaluation result returned by the service layer."""

    clarity: float
    correctness: float
    information_density: float
    hallucination_risk: float
    redundancy: float
    total_score: float
    heuristic_scores: dict[str, float]
    llm_scores: dict[str, float]
    llm_provider: str
    rationale: str | None = None


class EvaluatorService:
    """Blends heuristic and optional LLM scores into a stored evaluation."""

    def __init__(self, app_settings: Settings) -> None:
        self.settings = app_settings

    async def evaluate(self, prompt_text: str) -> EvaluationResult:
        heuristic_scores = await run_in_threadpool(heuristics.score_prompt, prompt_text)
        provider = create_llm_provider(self.settings)
        llm_scores: dict[str, float] = {}
        rationale: str | None = None
        llm_provider = "none"

        if provider is not None:
            llm_result = await provider.score(prompt_text)
            llm_scores = llm_result.scores
            rationale = llm_result.rationale
            llm_provider = self.settings.llm_provider

        blended_scores = blend_scores(
            heuristic_scores=heuristic_scores,
            llm_scores=llm_scores or None,
            heuristic_weight=self.settings.heuristic_weight,
            llm_weight=self.settings.llm_weight,
        )
        total_score = compute_weighted_total(blended_scores)
        return EvaluationResult(
            clarity=blended_scores["clarity"],
            correctness=blended_scores["correctness"],
            information_density=blended_scores["information_density"],
            hallucination_risk=blended_scores["hallucination_risk"],
            redundancy=blended_scores["redundancy"],
            total_score=total_score,
            heuristic_scores=heuristic_scores,
            llm_scores=llm_scores,
            llm_provider=llm_provider,
            rationale=rationale,
        )
