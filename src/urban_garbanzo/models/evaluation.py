"""Evaluation model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:  # pragma: no cover
    from tortoise.fields.relational import ForeignKeyRelation

    from .prompt import Prompt


class Evaluation(Model):
    """Stored evaluation scores for a prompt."""

    id = fields.UUIDField(pk=True)
    prompt: ForeignKeyRelation[Prompt] = fields.ForeignKeyField(
        "models.Prompt",
        related_name="evaluations",
        on_delete=fields.CASCADE,
    )
    clarity = fields.DecimalField(max_digits=5, decimal_places=2)
    correctness = fields.DecimalField(max_digits=5, decimal_places=2)
    information_density = fields.DecimalField(max_digits=5, decimal_places=2)
    hallucination_risk = fields.DecimalField(max_digits=5, decimal_places=2)
    redundancy = fields.DecimalField(max_digits=5, decimal_places=2)
    total_score = fields.DecimalField(max_digits=5, decimal_places=2)
    heuristic_scores: dict[str, float] = fields.JSONField(default=dict)
    llm_scores: dict[str, float] = fields.JSONField(default=dict)
    rationale = fields.TextField(null=True)
    llm_provider = fields.CharField(max_length=32, default="none")
    evaluated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "evaluations"
        ordering = ["-evaluated_at"]

    def __str__(self) -> str:
        return f"Evaluation<{self.id}>"
