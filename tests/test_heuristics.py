"""Heuristic scoring tests."""

from __future__ import annotations

import pytest
from urban_garbanzo.services.heuristics import (
    score_clarity,
    score_correctness,
    score_hallucination_risk,
    score_information_density,
    score_prompt,
    score_redundancy,
)


def test_score_prompt_returns_all_dimensions() -> None:
    """Heuristic scoring returns each supported dimension."""

    scores = score_prompt(
        "Write a concise plan with constraints, acceptance criteria, and examples."
    )
    assert set(scores) == {
        "clarity",
        "correctness",
        "information_density",
        "hallucination_risk",
        "redundancy",
    }
    assert all(1.0 <= value <= 100.0 for value in scores.values())


def test_redundancy_score_increases_for_repeated_text() -> None:
    """Highly repetitive text should have a higher redundancy score."""

    repetitive = score_prompt("Repeat this. Repeat this. Repeat this. Repeat this.")
    concise = score_prompt("Describe the deployment checklist in one concise paragraph.")
    assert repetitive["redundancy"] > concise["redundancy"]


# ---------------------------------------------------------------------------
# Degenerate input: pure token repetition ("hello hello hello ...")
# ---------------------------------------------------------------------------

REPETITIVE_TEXT = " ".join(["hello"] * 20)


class TestPureRepetitionScoring:
    """Ensure that pure single-token repetition scores near-zero on
    positive metrics and near-maximum on risk/redundancy metrics.

    Target ranges (from issue report):
        Clarity         ~  0 -  5
        Correctness     ~  0 -  5
        Info density    ~  0 -  2
        Hallucination   ~ 85 - 100
        Redundancy      ~ 95 - 100
    """

    def test_clarity_near_zero(self) -> None:
        assert score_clarity(REPETITIVE_TEXT) <= 5.0

    def test_correctness_near_zero(self) -> None:
        assert score_correctness(REPETITIVE_TEXT) <= 5.0

    def test_information_density_near_zero(self) -> None:
        assert score_information_density(REPETITIVE_TEXT) <= 2.0

    def test_hallucination_risk_near_max(self) -> None:
        assert score_hallucination_risk(REPETITIVE_TEXT) >= 85.0

    def test_redundancy_near_max(self) -> None:
        assert score_redundancy(REPETITIVE_TEXT) >= 95.0

    def test_all_scores_in_valid_range(self) -> None:
        scores = score_prompt(REPETITIVE_TEXT)
        assert all(1.0 <= v <= 100.0 for v in scores.values())


# ---------------------------------------------------------------------------
# Degenerate input: single token
# ---------------------------------------------------------------------------


class TestSingleTokenScoring:
    """A single meaningless word should not score well on any positive metric."""

    def test_clarity_low(self) -> None:
        assert score_clarity("hello") <= 15.0

    def test_correctness_low(self) -> None:
        assert score_correctness("hello") <= 15.0

    def test_information_density_low(self) -> None:
        assert score_information_density("hello") <= 15.0

    def test_hallucination_risk_high(self) -> None:
        assert score_hallucination_risk("hello") >= 80.0

    def test_redundancy_minimal(self) -> None:
        # A single word has no repetition, so redundancy should be low.
        assert score_redundancy("hello") <= 5.0


# ---------------------------------------------------------------------------
# Degenerate input: all-stopword text
# ---------------------------------------------------------------------------


class TestAllStopwordsScoring:
    """Text composed entirely of stopwords carries no informative content."""

    STOPWORD_TEXT = "the a an is are and for in to with"

    def test_clarity_low(self) -> None:
        assert score_clarity(self.STOPWORD_TEXT) <= 5.0

    def test_correctness_low(self) -> None:
        assert score_correctness(self.STOPWORD_TEXT) <= 5.0

    def test_information_density_at_floor(self) -> None:
        assert score_information_density(self.STOPWORD_TEXT) == 1.0

    def test_hallucination_risk_high(self) -> None:
        assert score_hallucination_risk(self.STOPWORD_TEXT) >= 85.0


# ---------------------------------------------------------------------------
# Logical consistency: quality gap between good and degenerate prompts
# ---------------------------------------------------------------------------


class TestQualityGapConsistency:
    """Good prompts must score meaningfully higher than degenerate ones on
    positive metrics, and meaningfully lower on risk metrics."""

    GOOD_PROMPT = "Write a concise plan with constraints, acceptance criteria, and examples."

    @pytest.fixture()
    def good_scores(self) -> dict[str, float]:
        return score_prompt(self.GOOD_PROMPT)

    @pytest.fixture()
    def degenerate_scores(self) -> dict[str, float]:
        return score_prompt(REPETITIVE_TEXT)

    def test_clarity_gap(self, good_scores, degenerate_scores) -> None:
        assert good_scores["clarity"] > degenerate_scores["clarity"] + 30

    def test_correctness_gap(self, good_scores, degenerate_scores) -> None:
        assert good_scores["correctness"] > degenerate_scores["correctness"] + 30

    def test_density_gap(self, good_scores, degenerate_scores) -> None:
        assert good_scores["information_density"] > degenerate_scores["information_density"] + 30

    def test_hallucination_gap(self, good_scores, degenerate_scores) -> None:
        assert good_scores["hallucination_risk"] < degenerate_scores["hallucination_risk"] - 30

    def test_redundancy_gap(self, good_scores, degenerate_scores) -> None:
        assert good_scores["redundancy"] < degenerate_scores["redundancy"] - 30

    def test_no_logical_contradiction(self, degenerate_scores) -> None:
        """High clarity + high correctness MUST NOT coexist with near-zero density.

        This guards against the original bug where clarity=70, correctness=71,
        but info_density=1 -- a numerically impossible combination for text
        that actually conveys meaning.
        """
        clarity = degenerate_scores["clarity"]
        correctness = degenerate_scores["correctness"]
        density = degenerate_scores["information_density"]

        # If density is below 5, clarity and correctness must also be low.
        if density < 5.0:
            assert clarity < 15.0, f"Logical contradiction: density={density} but clarity={clarity}"
            assert (
                correctness < 15.0
            ), f"Logical contradiction: density={density} but correctness={correctness}"
