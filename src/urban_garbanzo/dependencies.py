"""Reusable FastAPI dependencies."""

from __future__ import annotations

from uuid import UUID

from urban_garbanzo.config import Settings, settings
from urban_garbanzo.exceptions import EvaluationNotFound, PromptNotFound
from urban_garbanzo.models import Evaluation, Prompt
from urban_garbanzo.services import EvaluatorService


def get_settings() -> Settings:
    """Return the active settings object."""

    return settings


def get_evaluator() -> EvaluatorService:
    """Return an evaluator service built from active settings."""

    return EvaluatorService(settings)


async def get_prompt_or_404(prompt_id: UUID) -> Prompt:
    """Load a non-deleted prompt or raise a 404-style application error."""

    prompt: Prompt | None = (
        await Prompt.filter(id=prompt_id, deleted_at=None)
        .prefetch_related("user", "evaluations")
        .first()
    )
    if prompt is None:
        raise PromptNotFound(prompt_id)
    return prompt


async def get_evaluation_or_404(evaluation_id: UUID) -> Evaluation:
    """Load an evaluation or raise a 404-style application error."""

    evaluation: Evaluation | None = (
        await Evaluation.filter(id=evaluation_id).prefetch_related("prompt__user").first()
    )
    if evaluation is None:
        raise EvaluationNotFound(evaluation_id)
    return evaluation
