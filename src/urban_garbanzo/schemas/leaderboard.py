"""Leaderboard schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LeaderboardPromptEntry(BaseModel):
    """Prompt leaderboard entry."""

    rank: int
    prompt_id: UUID
    text_preview: str
    total_score: float
    submitter_tag: str | None = None
    evaluated_at: datetime


class LeaderboardUserEntry(BaseModel):
    """User leaderboard entry."""

    rank: int
    submitter_tag: str
    score: float
    prompt_count: int
