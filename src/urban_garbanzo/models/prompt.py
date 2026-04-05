"""Prompt model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:  # pragma: no cover
    from tortoise.fields.relational import ForeignKeyNullableRelation, ReverseRelation

    from .evaluation import Evaluation
    from .user import User


class Prompt(Model):
    """Submitted prompt text awaiting evaluation."""

    id = fields.UUIDField(pk=True)
    text = fields.TextField()
    user: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="prompts",
        null=True,
        on_delete=fields.SET_NULL,
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    evaluations: ReverseRelation[Evaluation]

    class Meta:
        table = "prompts"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Prompt<{self.id}>"
