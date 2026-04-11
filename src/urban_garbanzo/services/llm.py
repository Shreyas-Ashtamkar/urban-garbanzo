"""Pluggable LLM providers used by the evaluator."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from urban_garbanzo.config import Settings
from urban_garbanzo.exceptions import EvaluationFailed, LLMUnavailable
from urban_garbanzo.services.heuristics import SCORE_FIELDS

SYSTEM_PROMPT = """
You are a prompt evaluator. Score the provided prompt from 1.00 to 100.00 on five dimensions:

- clarity: explicitness, lack of ambiguity, clear task
- correctness: internally coherent, logically valid instruction
- information_density: meaningful, task-relevant content (not filler)
- hallucination_risk: likelihood the model must invent missing intent or details
- redundancy: repetition or unnecessary wording

Hard rules:
- Judge only what is written. Do not infer, complete, or assume missing context.
- Higher is better for clarity, correctness, and information_density.
- Higher is worse for hallucination_risk and redundancy — score them high when the prompt is risky or repetitive.
- Meaningless or repetitive text scores very low on clarity, correctness, information_density.
- Weak or absent intent scores high on hallucination_risk.
- Do not reward surface readability when content is empty or vague.
- Evaluate the prompt in the context of the target model the user intends to use.

Calibration anchors:

Low — "hello hello hello hello"
  clarity: 3, correctness: 2, information_density: 1, hallucination_risk: 92, redundancy: 98
  Why: pure repetition, no task, no meaning, no grounding.

Medium — "Summarize this article in bullet points."
  clarity: 65, correctness: 78, information_density: 45, hallucination_risk: 35, redundancy: 8
  Why: real task, low redundancy, but underspecified — article not provided, constraints minimal.

High — "Read the requirements below and produce a release plan with milestones, owners, dependencies, top 5 risks, and success criteria. Use a table. Max 400 words. List assumptions."
  clarity: 92, correctness: 93, information_density: 88, hallucination_risk: 10, redundancy: 5
  Why: task, structure, constraints, and expected output are all explicit and well grounded.

Output rules:
- Return JSON only. No markdown, no preamble, no trailing text.
- Use exactly these keys and types:

{
  "clarity": float (1.00-100.00),
  "correctness": float (1.00-100.00),
  "information_density": float (1.00-100.00),
  "hallucination_risk": float (1.00-100.00),
  "redundancy": float (1.00-100.00),
  "rationale": "max 60 words — top strength, top weakness, one concrete fix"
}
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
