"""Deterministic tests for the pure text metrics."""

from __future__ import annotations

import pytest

from ocrbench.metrics.normalize import normalize_text
from ocrbench.metrics.text import (
    cer,
    macro_cer,
    macro_wer,
    micro_cer,
    micro_wer,
    wer,
)


class TestPerSample:
    def test_perfect_match(self):
        assert cer("abc", "abc") == 0.0
        assert wer("a b c", "a b c") == 0.0

    def test_substitution(self):
        assert cer("abc", "axc") == pytest.approx(1 / 3)
        assert wer("a b c", "a x c") == pytest.approx(1 / 3)

    def test_insertion(self):
        assert cer("abc", "abxc") == pytest.approx(1 / 3)
        assert wer("a b", "a x b") == pytest.approx(1 / 2)

    def test_deletion(self):
        assert cer("abc", "ac") == pytest.approx(1 / 3)
        assert wer("a b c", "a c") == pytest.approx(1 / 3)

    def test_failed_sample_empty_hypothesis_scores_one(self):
        # worst-case rule: empty hypothesis vs non-empty reference → exactly 1.0
        assert cer("anything", "") == 1.0
        assert wer("some words here", "") == 1.0

    def test_empty_reference_rejected_not_scored_as_zero(self):
        with pytest.raises(ValueError, match="empty reference"):
            cer("", "x")
        with pytest.raises(ValueError, match="empty reference"):
            wer("   ", "x")


class TestRawVsNormalized:
    def test_normalization_changes_the_score(self):
        reference = "مُحَمَّد أَحْمَد"
        hypothesis = "محمد احمد"  # engine emitted plain, folded forms
        raw = cer(reference, hypothesis)
        normalized = cer(normalize_text(reference), normalize_text(hypothesis))
        assert raw > 0
        assert normalized == 0.0

    def test_raw_path_ignores_normalization(self):
        # punctuation errors are real errors: normalization must not hide them
        reference, hypothesis = "نص.", "نص"
        assert cer(reference, hypothesis) > 0
        assert cer(normalize_text(reference), normalize_text(hypothesis)) > 0


class TestAggregation:
    def test_micro_pools_distances_not_averages_ratios(self):
        pairs = [("abc", "axc"), ("de", "df")]
        pooled_ed = 1 + 1          # 1/3 + 1/2 per-sample
        pooled_len = 3 + 2
        assert micro_cer(pairs) == pytest.approx(pooled_ed / pooled_len)
        assert micro_cer(pairs) != pytest.approx((1 / 3 + 1 / 2) / 2)

    def test_macro_is_mean_of_per_sample(self):
        pairs = [("abc", "axc"), ("de", "df")]
        expected = ((1 / 3) + (1 / 2)) / 2
        assert macro_cer(pairs) == pytest.approx(expected)
        assert macro_wer([("a b", "a x"), ("c d e", "c d")]) == pytest.approx(
            (1 / 2 + 1 / 3) / 2
        )

    def test_micro_wer_word_pooling(self):
        pairs = [("a b c d", "a x c d"), ("one two", "own to")]
        assert micro_wer(pairs) == pytest.approx((1 + 2) / (4 + 2))

    def test_aggregates_reject_all_empty_input_and_empty_refs(self):
        with pytest.raises(ValueError):
            micro_cer([])
        with pytest.raises(ValueError, match="empty reference"):
            micro_cer([("", "x")])
