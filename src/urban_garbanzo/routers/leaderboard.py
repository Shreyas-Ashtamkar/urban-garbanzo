"""Leaderboard API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Query

from urban_garbanzo.schemas.leaderboard import LeaderboardPromptEntry, LeaderboardUserEntry
from urban_garbanzo.services.leaderboard import get_prompt_leaderboard, get_user_leaderboard

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/prompts", response_model=list[LeaderboardPromptEntry])
async def prompt_leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
    dimension: Literal[
        "total_score",
        "clarity",
        "correctness",
        "information_density",
        "hallucination_risk",
        "redundancy",
    ] = "total_score",
) -> list[LeaderboardPromptEntry]:
    """Return the prompt leaderboard for the selected dimension."""

    return await get_prompt_leaderboard(limit=limit, dimension=dimension)


@router.get("/users/best", response_model=list[LeaderboardUserEntry])
async def best_user_leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
) -> list[LeaderboardUserEntry]:
    """Return users ranked by their best prompt score."""

    return await get_user_leaderboard(mode="best", limit=limit)


@router.get("/users/average", response_model=list[LeaderboardUserEntry])
async def average_user_leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
) -> list[LeaderboardUserEntry]:
    """Return users ranked by their average prompt score."""

    return await get_user_leaderboard(mode="average", limit=limit)
