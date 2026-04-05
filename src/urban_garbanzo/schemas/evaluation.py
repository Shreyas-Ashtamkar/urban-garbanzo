"""Evaluation schemas and serializers."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:  # pragma: no cover
    from urban_garbanzo.models import Evaluation


def score_to_float(value: Decimal | float | int) -> float:
    """Convert stored numeric score values into JSON-friendly floats."""

    return round(float(value), 2)


class EvaluationScores(BaseModel):
    """Dimension scores for a prompt evaluation."""

    clarity: float = Field(ge=1.0, le=100.0)
    correctness: float = Field(ge=1.0, le=100.0)
    information_density: float = Field(ge=1.0, le=100.0)
    hallucination_risk: float = Field(ge=1.0, le=100.0)
    redundancy: float = Field(ge=1.0, le=100.0)
    total_score: float = Field(ge=1.0, le=100.0)


class EvaluationRead(BaseModel):
    """Serialized evaluation record."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    prompt_id: UUID
    scores: EvaluationScores
    heuristic_scores: dict[str, Any]
    llm_scores: dict[str, Any]
    rationale: str | None = None
    llm_provider: str
    evaluated_at: datetime


class EvaluationHistoryResponse(BaseModel):
    """Evaluation history for a prompt."""

    items: list[EvaluationRead]


def build_evaluation_read(evaluation: Evaluation) -> EvaluationRead:
    """Convert an evaluation ORM object into the public schema."""

    prompt_id = getattr(evaluation, "prompt_id", None)
    if prompt_id is None:
        prompt_id = evaluation.prompt.id

    return EvaluationRead(
        id=evaluation.id,
        prompt_id=prompt_id,
        scores=EvaluationScores(
            clarity=score_to_float(evaluation.clarity),
            correctness=score_to_float(evaluation.correctness),
            information_density=score_to_float(evaluation.information_density),
            hallucination_risk=score_to_float(evaluation.hallucination_risk),
            redundancy=score_to_float(evaluation.redundancy),
            total_score=score_to_float(evaluation.total_score),
        ),
        heuristic_scores=dict(evaluation.heuristic_scores or {}),
        llm_scores=dict(evaluation.llm_scores or {}),
        rationale=evaluation.rationale,
        llm_provider=evaluation.llm_provider,
        evaluated_at=evaluation.evaluated_at,
    )
