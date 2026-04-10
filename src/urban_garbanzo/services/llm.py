"""Pluggable LLM providers used by the evaluator."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from urban_garbanzo.config import Settings
from urban_garbanzo.exceptions import EvaluationFailed, LLMUnavailable
from urban_garbanzo.services.heuristics import SCORE_FIELDS

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
Evaluate the prompt in the context of the target model the user intends to use.
""".strip()


@dataclass(slots=True)
class LLMScoreResult:
    """Normalized LLM scoring response."""

    scores: dict[str, float]
    rationale: str | None = None


class LLMProvider(Protocol):
    """Protocol for pluggable LLM backends."""

    async def score(self, prompt_text: str, target_model: str) -> LLMScoreResult:
        """Return evaluation scores for a prompt."""


def normalize_llm_payload(payload: dict[str, Any]) -> LLMScoreResult:
    """Normalize a provider JSON payload into a shared result object."""

    try:
        scores = {field: float(payload[field]) for field in SCORE_FIELDS}
    except (KeyError, TypeError, ValueError) as exc:  # pragma: no cover - defensive parsing guard
        raise EvaluationFailed("LLM returned an invalid score payload") from exc

    invalid_fields = [field for field, value in scores.items() if value < 1.0 or value > 100.0]
    if invalid_fields:
        invalid_field_list = ", ".join(invalid_fields)
        raise EvaluationFailed(
            f"LLM returned out-of-range scores for: {invalid_field_list}. Expected values between 1 and 100."
        )

    scores = {field: round(value, 2) for field, value in scores.items()}

    rationale = payload.get("rationale")
    if rationale is not None:
        rationale = str(rationale).strip() or None

    return LLMScoreResult(scores=scores, rationale=rationale)


class OpenAIProvider:
    """OpenAI-backed scoring provider."""

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def _get_client(self) -> Any:
        from openai import AsyncOpenAI

        if self.base_url:
            return AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        return AsyncOpenAI(api_key=self.api_key)

    async def score(self, prompt_text: str, target_model: str) -> LLMScoreResult:
        if not self.api_key:
            raise LLMUnavailable("OPENAI_API_KEY is not configured")

        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Target model: {target_model}\n\nPrompt to evaluate:\n{prompt_text}"
                    ),
                },
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

    async def score(self, prompt_text: str, target_model: str) -> LLMScoreResult:
        if not self.api_key:
            raise LLMUnavailable("ANTHROPIC_API_KEY is not configured")

        client = self._get_client()
        response = await client.messages.create(
            model=self.model,
            max_tokens=512,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Target model: {target_model}\n\nPrompt to evaluate:\n{prompt_text}"
                    ),
                }
            ],
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
        api_key = app_settings.openai_api_key
        if not api_key and app_settings.openai_base_url:
            api_key = "ollama"
        return OpenAIProvider(
            api_key=api_key or "",
            model=app_settings.openai_model,
            base_url=app_settings.openai_base_url,
        )

    if app_settings.llm_provider == "anthropic":
        return AnthropicProvider(
            api_key=app_settings.anthropic_api_key or "",
            model=app_settings.anthropic_model,
        )

    raise LLMUnavailable(f"Unsupported LLM provider '{app_settings.llm_provider}'")
