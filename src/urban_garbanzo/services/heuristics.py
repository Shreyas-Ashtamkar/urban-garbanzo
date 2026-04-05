"""Heuristic scoring utilities."""

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


def score_clarity(text: str) -> float:
    """Estimate clarity using readability and sentence complexity."""

    readability = clamp_score(float(textstat.flesch_reading_ease(text)))
    sentences = split_sentences(text)
    words = tokenize(text)
    avg_sentence_length = len(words) / max(len(sentences), 1)
    sentence_score = clamp_score(100.0 - max(avg_sentence_length - 18.0, 0.0) * 2.5)
    return clamp_score((readability * 0.65) + (sentence_score * 0.35))


def score_correctness(text: str) -> float:
    """Estimate structural correctness from balanced delimiters and punctuation."""

    score = 85.0
    delimiter_pairs = {"(": ")", "[": "]", "{": "}"}
    for opening, closing in delimiter_pairs.items():
        score -= abs(text.count(opening) - text.count(closing)) * 8.0

    double_spaces = text.count("  ")
    if double_spaces:
        score -= double_spaces * 2.5

    if text and text[-1] not in ".!?":
        score -= 6.0

    if "..." in text or "???" in text:
        score -= 5.0

    return clamp_score(score)


def score_information_density(text: str) -> float:
    """Estimate information density using unique non-stopword token ratio."""

    tokens = tokenize(text)
    if not tokens:
        return 1.0

    informative_tokens = [token for token in tokens if token not in STOPWORDS]
    unique_ratio = len(set(informative_tokens)) / max(len(informative_tokens), 1)
    density_bonus = min(len(informative_tokens), 60) / 60 * 20.0
    return clamp_score((unique_ratio * 80.0) + density_bonus)


def score_hallucination_risk(text: str) -> float:
    """Estimate hallucination risk from risky certainty language and vagueness."""

    tokens = tokenize(text)
    if not tokens:
        return 1.0

    risk_hits = sum(1 for token in tokens if token in RISK_TERMS)
    risk_ratio = risk_hits / len(tokens)
    vague_markers = text.lower().count("everyone") + text.lower().count("nobody")
    return clamp_score(5.0 + (risk_ratio * 500.0) + (vague_markers * 12.0))


def score_redundancy(text: str) -> float:
    """Estimate redundancy from repeated tokens and repeated sentences."""

    tokens = tokenize(text)
    if not tokens:
        return 1.0

    counts = Counter(tokens)
    repeated_tokens = sum(count - 1 for count in counts.values() if count > 1)
    token_ratio = repeated_tokens / len(tokens)

    sentences = split_sentences(text)
    repeated_sentences = len(sentences) - len({sentence.lower() for sentence in sentences})
    sentence_ratio = repeated_sentences / max(len(sentences), 1)

    return clamp_score(5.0 + (token_ratio * 60.0) + (sentence_ratio * 35.0))


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
