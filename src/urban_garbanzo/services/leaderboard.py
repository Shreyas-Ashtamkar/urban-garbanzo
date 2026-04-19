"""Leaderboard aggregation helpers."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Literal

from urban_garbanzo.models import Evaluation, Prompt
from urban_garbanzo.schemas.evaluation import score_to_float
from urban_garbanzo.schemas.leaderboard import LeaderboardPromptEntry, LeaderboardUserEntry
from urban_garbanzo.schemas.prompt import get_latest_evaluation

PromptDimension = Literal[
    "total_score",
    "clarity",
    "correctness",
    "information_density",
    "hallucination_risk",
    "redundancy",
]


def prompt_preview(text: str) -> str:
    """Build a compact preview for prompt leaderboard entries."""

    preview = " ".join(text.split())
    return preview[:77] + "..." if len(preview) > 80 else preview


def prompt_sort_key(entry: tuple[Prompt, Evaluation], dimension: PromptDimension) -> float:
    """Return the numeric sort key for prompt leaderboard ranking."""

    _, evaluation = entry
    value = score_to_float(getattr(evaluation, dimension))
    if dimension in {"hallucination_risk", "redundancy"}:
        return -value
    return value


async def get_prompt_leaderboard(
    limit: int,
    dimension: PromptDimension = "total_score",
) -> list[LeaderboardPromptEntry]:
    """Return the highest-ranked prompts by latest evaluation.

    Leaderboards require in-memory sorting because the sort key lives on the
    latest evaluation, but the queryset is bounded by ``limit`` on output so
    the working set stays small for typical usage.
    """

    # Cap the working set: fetch at most ``limit * 5`` prompts so we don't
    # load the entire table, while still having enough to produce ``limit``
    # results after filtering for evaluated prompts.
    fetch_limit = max(limit * 5, 100)
    prompts = (
        await Prompt.filter(deleted_at=None)
        .order_by("-created_at")
        .limit(fetch_limit)
        .prefetch_related("user", "evaluations")
    )
    scored_prompts: list[tuple[Prompt, Evaluation]] = []
    for prompt in prompts:
        latest = get_latest_evaluation(prompt)
        if latest is not None:
            scored_prompts.append((prompt, latest))

    ranked = sorted(scored_prompts, key=lambda item: prompt_sort_key(item, dimension), reverse=True)
    entries: list[LeaderboardPromptEntry] = []
    for rank, (prompt, evaluation) in enumerate(ranked[:limit], start=1):
        user = getattr(prompt, "user", None)
        entries.append(
            LeaderboardPromptEntry(
                rank=rank,
                prompt_id=prompt.id,
                text_preview=prompt_preview(prompt.text),
                total_score=score_to_float(evaluation.total_score),
                submitter_tag=user.tag if user is not None else None,
                evaluated_at=evaluation.evaluated_at,
            )
        )
    return entries


async def get_user_leaderboard(
    mode: Literal["best", "average"], limit: int
) -> list[LeaderboardUserEntry]:
    """Return user rankings based on each user's latest prompt evaluations.

    Similar to the prompt leaderboard, the aggregation requires in-memory
    grouping.  The queryset is bounded to keep the working set manageable.
    """

    fetch_limit = max(limit * 10, 200)
    prompts = (
        await Prompt.filter(deleted_at=None, user_id__not_isnull=True)
        .order_by("-created_at")
        .limit(fetch_limit)
        .prefetch_related("user", "evaluations")
    )
    grouped_scores: dict[str, list[float]] = defaultdict(list)
    prompt_counts: dict[str, int] = defaultdict(int)

    for prompt in prompts:
        latest = get_latest_evaluation(prompt)
        user = getattr(prompt, "user", None)
        if latest is None or user is None:
            continue
        grouped_scores[user.tag].append(score_to_float(latest.total_score))
        prompt_counts[user.tag] += 1

    if mode == "best":
        ordered = sorted(
            ((tag, max(scores), prompt_counts[tag]) for tag, scores in grouped_scores.items()),
            key=lambda item: item[1],
            reverse=True,
        )
    else:
        ordered = sorted(
            (
                (tag, round(mean(scores), 2), prompt_counts[tag])
                for tag, scores in grouped_scores.items()
            ),
            key=lambda item: item[1],
            reverse=True,
        )

    entries: list[LeaderboardUserEntry] = []
    for rank, (tag, score, prompt_count) in enumerate(ordered[:limit], start=1):
        entries.append(
            LeaderboardUserEntry(
                rank=rank,
                submitter_tag=tag,
                score=round(score, 2),
                prompt_count=prompt_count,
            )
        )
    return entries
