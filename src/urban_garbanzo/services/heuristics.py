"""Heuristic scoring utilities.

Each scoring function operates on a 1.00-100.00 scale.  All functions share
two foundational signal extractors -- :func:`_vocabulary_diversity` and
:func:`_semantic_quality` -- that detect degenerate inputs (pure repetition,
no actionable content, etc.) and penalise them toward the extremes rather
than collapsing to mid-range defaults.

Clarity, correctness, and information density use a **multiplicative quality
gate**: the raw surface-level score is multiplied by ``semantic_quality``
(floored at a small minimum).  This ensures that text with zero meaningful
content cannot reach mid-range scores regardless of surface-level properties.

Formula reference (per dimension)
=================================

vocabulary_diversity  = unique_tokens / total_tokens          (0.0-1.0)
semantic_quality      = diversity * (unique_informative / 8)  (0.0-1.0, soft-capped)

clarity
-------
  readability       = clamp(textstat.flesch_reading_ease)
  sentence_score    = clamp(100 - max(avg_sentence_len - 18, 0) * 2.5)
  raw_clarity       = readability * 0.65 + sentence_score * 0.35
  quality_factor    = max(semantic_quality, 0.01)
  final             = clamp(raw_clarity * quality_factor)

correctness
-----------
  structural_score  = 85 - delimiter_penalty - spacing - punctuation - ellipsis
  quality_factor    = max(semantic_quality, 0.05)
  final             = clamp(structural_score * quality_factor)

information_density
-------------------
  unique_ratio      = unique_informative / informative_count  (0.0-1.0)
  adjusted_ratio    = unique_ratio ^ 1.5                      (power-curve penalty)
  density_bonus     = min(unique_informative, 60) / 60 * 20   (only unique tokens)
  raw_density       = adjusted_ratio * 80 + density_bonus
  quality_factor    = max(semantic_quality, 0.01)
  final             = clamp(raw_density * quality_factor)

hallucination_risk
------------------
  keyword_risk      = risk_ratio * 500 + vague_markers * 12
  emptiness_risk    = (1 - semantic_quality) * 92             (lack of content → risk)
  final             = clamp(5 + keyword_risk + emptiness_risk)

redundancy
----------
  token_ratio       = repeated_token_count / total_tokens
  sentence_ratio    = repeated_sentences / total_sentences
  final             = clamp(token_ratio * 110 + sentence_ratio * 35)
"""

from __future__ import annotations

import re
from collections import Counter

import textstat

SCORE_FIELDS = (
    "clarity",
    "correctness",
    "information_density",
    "hallucination_risk",
    "redundancy",
)

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "if",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
    "you",
    "your",
}

RISK_TERMS = {
    "always",
    "certainly",
    "guaranteed",
    "never",
    "obviously",
    "proven",
    "undeniably",
}


def clamp_score(value: float) -> float:
    """Clamp scores to the supported 1.00-100.00 range."""

    return round(min(100.0, max(1.0, value)), 2)


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase word tokens."""

    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def split_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation boundaries."""

    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
    return sentences or [text.strip()]


# ---------------------------------------------------------------------------
# Shared signal extractors
# ---------------------------------------------------------------------------


def _vocabulary_diversity(tokens: list[str]) -> float:
    """Return unique/total ratio for a token list.  0.0 when empty."""

    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def _semantic_quality(tokens: list[str], informative_tokens: list[str]) -> float:
    """Score 0.0-1.0 representing whether the text carries actionable meaning.

    Combines vocabulary diversity with a soft-capped count of unique
    informative (non-stopword) tokens.  A text that is 100 % repetition of
    a single word scores near 0.  A well-written prompt with 8+ unique
    informative words scores near 1.0.
    """

    diversity = _vocabulary_diversity(tokens)
    unique_informative_count = len(set(informative_tokens))
    # Soft cap at 8 unique informative tokens → full credit.
    richness = min(unique_informative_count / 8.0, 1.0)
    return diversity * richness


# ---------------------------------------------------------------------------
# Dimension scorers
# ---------------------------------------------------------------------------


def score_clarity(text: str) -> float:
    """Estimate clarity using readability, sentence complexity, and semantic quality.

    The raw surface-level clarity (Flesch readability 0.65 + sentence-length
    penalty 0.35) is *multiplied* by the semantic quality factor.  This
    ensures that text with zero meaningful content cannot reach mid-range
    clarity no matter how "readable" the surface form appears to textstat.
    """

    tokens = tokenize(text)
    informative = [t for t in tokens if t not in STOPWORDS]
    quality = _semantic_quality(tokens, informative)

    readability = clamp_score(float(textstat.flesch_reading_ease(text)))
    sentences = split_sentences(text)
    avg_sentence_length = len(tokens) / max(len(sentences), 1)
    sentence_score = clamp_score(100.0 - max(avg_sentence_length - 18.0, 0.0) * 2.5)

    raw_clarity = (readability * 0.65) + (sentence_score * 0.35)
    # Multiplicative gate: meaningless text (quality ~ 0) → score ~ 1
    quality_factor = max(quality, 0.01)
    return clamp_score(raw_clarity * quality_factor)


def score_correctness(text: str) -> float:
    """Estimate structural correctness, scaled by semantic quality.

    The raw structural score starts at 85 and is penalised for mechanical
    defects (unbalanced delimiters, double spaces, missing terminal
    punctuation, ellipsis abuse).  It is then *multiplied* by a semantic
    quality factor so that meaningless text — even with perfect structure —
    scores near 1.
    """

    structural_score = 85.0
    delimiter_pairs = {"(": ")", "[": "]", "{": "}"}
    for opening, closing in delimiter_pairs.items():
        structural_score -= abs(text.count(opening) - text.count(closing)) * 8.0

    double_spaces = text.count("  ")
    if double_spaces:
        structural_score -= double_spaces * 2.5

    if text and text[-1] not in ".!?":
        structural_score -= 6.0

    if "..." in text or "???" in text:
        structural_score -= 5.0

    structural_score = max(structural_score, 0.0)

    tokens = tokenize(text)
    informative = [t for t in tokens if t not in STOPWORDS]
    quality = _semantic_quality(tokens, informative)
    # Floor at 0.05 so a structurally perfect but empty prompt → ~4 not 0.
    quality_factor = max(quality, 0.05)

    return clamp_score(structural_score * quality_factor)


def score_information_density(text: str) -> float:
    """Estimate information density using unique non-stopword token ratio.

    The density bonus counts only *unique* informative tokens so repeating
    the same word N times adds no bonus.  A multiplicative semantic-quality
    gate (consistent with clarity and correctness) ensures that trivially
    "unique" but meaningless inputs (e.g. a single word, or pure repetition)
    cannot reach mid-range scores.
    """

    tokens = tokenize(text)
    if not tokens:
        return 1.0

    informative_tokens = [token for token in tokens if token not in STOPWORDS]
    if not informative_tokens:
        return 1.0

    quality = _semantic_quality(tokens, informative_tokens)

    unique_informative = set(informative_tokens)
    unique_ratio = len(unique_informative) / max(len(informative_tokens), 1)
    # Apply power curve: low diversity penalised more steeply (0.1 → 0.032)
    adjusted_ratio = unique_ratio**1.5
    density_bonus = min(len(unique_informative), 60) / 60 * 20.0
    raw_density = (adjusted_ratio * 80.0) + density_bonus
    # Multiplicative gate: meaningless text (quality ~ 0) → score ~ 1
    quality_factor = max(quality, 0.01)
    return clamp_score(raw_density * quality_factor)


def score_hallucination_risk(text: str) -> float:
    """Estimate hallucination risk from certainty keywords *and* content emptiness.

    A prompt that provides no grounding context forces the model to invent
    everything.  The ``emptiness_risk`` component — ``(1 - quality) * 90`` —
    pushes the score toward 95 for meaningless inputs, reflecting the near-
    certainty of hallucination.
    """

    tokens = tokenize(text)
    if not tokens:
        return 1.0

    informative = [t for t in tokens if t not in STOPWORDS]
    quality = _semantic_quality(tokens, informative)

    risk_hits = sum(1 for token in tokens if token in RISK_TERMS)
    risk_ratio = risk_hits / len(tokens)
    vague_markers = text.lower().count("everyone") + text.lower().count("nobody")

    keyword_risk = (risk_ratio * 500.0) + (vague_markers * 12.0)
    emptiness_risk = (1.0 - quality) * 92.0

    return clamp_score(5.0 + keyword_risk + emptiness_risk)


def score_redundancy(text: str) -> float:
    """Estimate redundancy from repeated tokens and repeated sentences.

    The token-repetition coefficient is 110 so that a 90 % repetition
    rate produces ~99.  No fixed base — clean text with zero repetition
    starts at clamp minimum (1.0).
    """

    tokens = tokenize(text)
    if not tokens:
        return 1.0

    counts = Counter(tokens)
    repeated_tokens = sum(count - 1 for count in counts.values() if count > 1)
    token_ratio = repeated_tokens / len(tokens)

    sentences = split_sentences(text)
    repeated_sentences = len(sentences) - len({sentence.lower() for sentence in sentences})
    sentence_ratio = repeated_sentences / max(len(sentences), 1)

    return clamp_score((token_ratio * 110.0) + (sentence_ratio * 35.0))


def score_prompt(text: str) -> dict[str, float]:
    """Compute heuristic scores for all evaluation dimensions."""

    normalized = text.strip()
    return {
        "clarity": score_clarity(normalized),
        "correctness": score_correctness(normalized),
        "information_density": score_information_density(normalized),
        "hallucination_risk": score_hallucination_risk(normalized),
        "redundancy": score_redundancy(normalized),
    }
