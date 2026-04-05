"""Evaluation API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from urban_garbanzo.dependencies import get_evaluation_or_404, get_prompt_or_404
from urban_garbanzo.models import Evaluation, Prompt
from urban_garbanzo.schemas.evaluation import (
    EvaluationHistoryResponse,
    EvaluationRead,
    build_evaluation_read,
)

router = APIRouter(tags=["evaluations"])


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationRead)
async def get_evaluation(
    evaluation: Annotated[Evaluation, Depends(get_evaluation_or_404)],
) -> EvaluationRead:
    """Return a single evaluation by id."""

    return build_evaluation_read(evaluation)


@router.get("/prompts/{prompt_id}/evaluations", response_model=EvaluationHistoryResponse)
async def list_prompt_evaluations(
    prompt: Annotated[Prompt, Depends(get_prompt_or_404)],
) -> EvaluationHistoryResponse:
    """Return the complete evaluation history for a prompt."""

    evaluations = sorted(prompt.evaluations, key=lambda item: item.evaluated_at, reverse=True)
    return EvaluationHistoryResponse(
        items=[build_evaluation_read(evaluation) for evaluation in evaluations]
    )
