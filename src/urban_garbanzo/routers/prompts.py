"""Prompt API routes."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response, status
from tortoise import timezone

from urban_garbanzo.dependencies import get_evaluator, get_prompt_or_404
from urban_garbanzo.models import Evaluation, Prompt, User
from urban_garbanzo.schemas.evaluation import EvaluationRead, build_evaluation_read
from urban_garbanzo.schemas.prompt import (
    PromptCreate,
    PromptListResponse,
    PromptRead,
    build_prompt_read,
)
from urban_garbanzo.services import EvaluatorService
from urban_garbanzo.services.evaluator import to_decimal

router = APIRouter(prefix="/prompts", tags=["prompts"])


async def resolve_submitter(submitter_tag: str | None) -> User | None:
    """Resolve or create a user for the submitted prompt tag."""

    if submitter_tag is None:
        return None

    user: User
    user, _ = await User.get_or_create(tag=submitter_tag)
    return user


@router.post("", response_model=PromptRead, status_code=status.HTTP_201_CREATED)
async def create_prompt(payload: PromptCreate) -> PromptRead:
    """Store a prompt submission without evaluating it yet."""

    user = await resolve_submitter(payload.submitter_tag)
    prompt = await Prompt.create(text=payload.text, target_model=payload.target_model, user=user)
    await prompt.fetch_related("user", "evaluations")
    return build_prompt_read(prompt)


@router.get("", response_model=PromptListResponse)
async def list_prompts(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
    sort_by: Literal["created_at", "total_score"] = "created_at",
) -> PromptListResponse:
    """List prompts and their latest evaluations."""

    prompts = await Prompt.filter(deleted_at=None).prefetch_related("user", "evaluations")
    prompt_reads = [build_prompt_read(prompt) for prompt in prompts]
    sorted_prompts = sorted(
        prompt_reads,
        key=lambda prompt: (
            prompt.created_at
            if sort_by == "created_at"
            else (prompt.latest_evaluation.scores.total_score if prompt.latest_evaluation else -1)
        ),
        reverse=True,
    )

    start = (page - 1) * size
    end = start + size
    return PromptListResponse(
        items=sorted_prompts[start:end], total=len(sorted_prompts), page=page, size=size
    )


@router.get("/{prompt_id}", response_model=PromptRead)
async def get_prompt(prompt: Annotated[Prompt, Depends(get_prompt_or_404)]) -> PromptRead:
    """Return one prompt and its latest evaluation."""

    return build_prompt_read(prompt)


@router.post("/{prompt_id}/evaluate", response_model=EvaluationRead)
async def evaluate_prompt(
    prompt: Annotated[Prompt, Depends(get_prompt_or_404)],
    evaluator: Annotated[EvaluatorService, Depends(get_evaluator)],
) -> EvaluationRead:
    """Run the evaluation pipeline for a prompt and store the result."""

    result = await evaluator.evaluate(prompt.text, prompt.target_model)
    evaluation = await Evaluation.create(
        prompt=prompt,
        clarity=to_decimal(result.clarity),
        correctness=to_decimal(result.correctness),
        information_density=to_decimal(result.information_density),
        hallucination_risk=to_decimal(result.hallucination_risk),
        redundancy=to_decimal(result.redundancy),
        total_score=to_decimal(result.total_score),
        heuristic_scores=result.heuristic_scores,
        llm_scores=result.llm_scores,
        rationale=result.rationale,
        llm_provider=result.llm_provider,
    )
    await evaluation.fetch_related("prompt")
    return build_evaluation_read(evaluation)


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_prompt(prompt: Annotated[Prompt, Depends(get_prompt_or_404)]) -> Response:
    """Soft-delete a prompt so it is hidden from public queries."""

    prompt.deleted_at = timezone.now()
    await prompt.save(update_fields=["deleted_at"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
