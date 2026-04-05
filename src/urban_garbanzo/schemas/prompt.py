"""Prompt schemas and serializers."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, cast
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .evaluation import EvaluationRead, build_evaluation_read

if TYPE_CHECKING:  # pragma: no cover
    from urban_garbanzo.models import Evaluation, Prompt


class PromptCreate(BaseModel):
    """Prompt creation payload."""

    text: str = Field(min_length=10, max_length=10_000)
    submitter_tag: str | None = Field(default=None, min_length=2, max_length=64)

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        """Trim prompt input while rejecting blank submissions."""

        normalized = value.strip()
        if not normalized:
            raise ValueError("Prompt text cannot be blank")
        return normalized

    @field_validator("submitter_tag")
    @classmethod
    def normalize_submitter_tag(cls, value: str | None) -> str | None:
        """Normalize empty submitter tags to None."""

        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class PromptRead(BaseModel):
    """Serialized prompt record with its latest evaluation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    submitter_tag: str | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    latest_evaluation: EvaluationRead | None = None


class PromptListResponse(BaseModel):
    """Paginated prompt response."""

    items: list[PromptRead]
    total: int
    page: int
    size: int


def get_latest_evaluation(prompt: Prompt) -> Evaluation | None:
    """Return the most recent evaluation for a prompt."""

    evaluations = list(getattr(prompt, "evaluations", []))
    if not evaluations:
        return None

    return cast("Evaluation", max(evaluations, key=lambda item: item.evaluated_at))


def build_prompt_read(prompt: Prompt, latest_evaluation: Evaluation | None = None) -> PromptRead:
    """Convert a prompt ORM object into the public schema."""

    latest = latest_evaluation or get_latest_evaluation(prompt)
    user = getattr(prompt, "user", None)
    submitter_tag = user.tag if user is not None else None
    return PromptRead(
        id=prompt.id,
        text=prompt.text,
        submitter_tag=submitter_tag,
        created_at=prompt.created_at,
        updated_at=prompt.updated_at,
        deleted_at=prompt.deleted_at,
        latest_evaluation=build_evaluation_read(latest) if latest is not None else None,
    )
