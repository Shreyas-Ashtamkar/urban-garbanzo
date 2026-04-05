"""API routers."""

from .evaluations import router as evaluations_router
from .leaderboard import router as leaderboard_router
from .prompts import router as prompts_router

__all__ = ["evaluations_router", "leaderboard_router", "prompts_router"]
