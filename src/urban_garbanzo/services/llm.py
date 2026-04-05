"""Pluggable LLM providers used by the evaluator."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from urban_garbanzo.config import Settings
from urban_garbanzo.exceptions import EvaluationFailed, LLMUnavailable
from urban_garbanzo.services.heuristics import SCORE_FIELDS, clamp_score

SYSTEM_PROMPT = """
You are an expert prompt evaluator. Score the provided prompt across these dimensions from 1.00 to 100.00:
- clarity
- correctness
- information_density
- hallucination_risk
- redundancy

Return JSON only with the keys:
clarity, correctness, information_density, hallucination_risk, redundancy, rationale

Hallucination risk and redundancy should be higher when the prompt is more risky or repetitive.
Keep rationale under 80 words.
""".strip()


@dataclass(slots=True)
class LLMScoreResult:
    """Normalized LLM scoring response."""

    scores: dict[str, float]
    rationale: str | None = None


class LLMProvider(Protocol):
    """Protocol for pluggable LLM backends."""

    async def score(self, prompt_text: str) -> LLMScoreResult:
        """Return evaluation scores for a prompt."""


def normalize_llm_payload(payload: dict[str, Any]) -> LLMScoreResult:
    """Normalize a provider JSON payload into a shared result object."""

    try:
        scores = {field: clamp_score(float(payload[field])) for field in SCORE_FIELDS}
    except (KeyError, TypeError, ValueError) as exc:  # pragma: no cover - defensive parsing guard
        raise EvaluationFailed("LLM returned an invalid score payload") from exc

    rationale = payload.get("rationale")
    if rationale is not None:
        rationale = str(rationale).strip() or None

    return LLMScoreResult(scores=scores, rationale=rationale)


class OpenAIProvider:
    """OpenAI-backed scoring provider."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def _get_client(self) -> Any:
        from openai import AsyncOpenAI

        return AsyncOpenAI(api_key=self.api_key)

    async def score(self, prompt_text: str) -> LLMScoreResult:
        if not self.api_key:
            raise LLMUnavailable("OPENAI_API_KEY is not configured")

        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_text},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise EvaluationFailed("OpenAI returned an empty response")

        return normalize_llm_payload(json.loads(content))


class AnthropicProvider:
    """Anthropic-backed scoring provider."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def _get_client(self) -> Any:
        from anthropic import AsyncAnthropic

        return AsyncAnthropic(api_key=self.api_key)

    async def score(self, prompt_text: str) -> LLMScoreResult:
        if not self.api_key:
            raise LLMUnavailable("ANTHROPIC_API_KEY is not configured")

        client = self._get_client()
        response = await client.messages.create(
            model=self.model,
            max_tokens=512,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt_text}],
        )
        content_blocks = getattr(response, "content", [])
        if not content_blocks:
            raise EvaluationFailed("Anthropic returned an empty response")

        content = getattr(content_blocks[0], "text", "")
        if not content:
            raise EvaluationFailed("Anthropic returned an empty response")

        return normalize_llm_payload(json.loads(content))


def create_llm_provider(app_settings: Settings) -> LLMProvider | None:
    """Build the configured LLM provider, if one is enabled."""

    if app_settings.llm_provider == "none":
        return None

    if app_settings.llm_provider == "openai":
        return OpenAIProvider(
            api_key=app_settings.openai_api_key or "",
            model=app_settings.openai_model,
        )

    if app_settings.llm_provider == "anthropic":
        return AnthropicProvider(
            api_key=app_settings.anthropic_api_key or "",
            model=app_settings.anthropic_model,
        )

    raise LLMUnavailable(f"Unsupported LLM provider '{app_settings.llm_provider}'")
