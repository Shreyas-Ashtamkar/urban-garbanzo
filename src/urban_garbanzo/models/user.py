"""User model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:  # pragma: no cover
    from tortoise.fields.relational import ReverseRelation

    from .prompt import Prompt


class User(Model):
    """Anonymous handle used to group prompt submissions."""

    id = fields.UUIDField(pk=True)
    tag = fields.CharField(max_length=64, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    prompts: ReverseRelation[Prompt]

    class Meta:
        table = "users"

    def __str__(self) -> str:
        return str(self.tag)
