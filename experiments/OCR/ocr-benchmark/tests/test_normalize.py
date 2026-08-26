"""Golden tests for the centralized normalization policy (v1)."""

from __future__ import annotations

import pytest

from ocrbench.metrics.normalize import (
    NORMALIZATION_VERSION,
    normalize_text,
)


class TestArabicOrthography:
    def test_tashkeel_removed(self):
        assert normalize_text("مُحَمَّدٌ") == "محمد"

    def test_alef_hamza_folded_to_bare_alef(self):
        assert normalize_text("أإآ") == "ااا"

    def test_bare_alef_unchanged(self):
        assert normalize_text("ا") == "ا"

    def test_yeh_alef_maqsura_folded(self):
        assert normalize_text("على") == "علي"
        assert normalize_text("ي") == "ي"

    def test_teh_marbuta_preserved_not_folded_to_heh(self):
        assert normalize_text("ة") == "ة"
        assert normalize_text("ه") == "ه"
        assert normalize_text("ة") != normalize_text("ه")

    def test_tatweel_preserved(self):
        # elongation formatting is NOT in the §6.2 table → kept
        assert normalize_text("ـــ") == "ـــ"

    def test_alef_wasla_preserved(self):
        # ٱ is not in the agreed fold list → preserved (conservative)
        assert normalize_text("ٱ") == "ٱ"


class TestPreservationGuards:
    def test_digits_survive_both_scripts(self):
        assert normalize_text("2026 ١٢٣") == "2026 ١٢٣"

    def test_punctuation_survives(self):
        assert normalize_text(".،!؟:") == ".،!؟:"

    @pytest.mark.parametrize("text", ["نص", "Hello", "x1.2"])
    def test_idempotent_on_already_normalized_text(self, text):
        once = normalize_text(text)
        assert normalize_text(once) == once


class TestLatinAndWhitespace:
    def test_latin_casefolded(self):
        assert normalize_text("Hello WORLD") == "hello world"

    def test_whitespace_collapsed_and_trimmed(self):
        assert normalize_text("  a\n\t b   c  ") == "a b c"


class TestUnicode:
    def test_nfc_composed_and_decomposed_equal(self):
        decomposed = "e\u0301"  # é as e + combining acute
        assert normalize_text("é") == normalize_text(decomposed)


class TestMisrajMarkup:
    def test_img_placeholder_dropped_entirely(self):
        assert normalize_text("بسم <img>image here</img> الله") == "بسم الله"

    def test_page_number_unwrapped_content_kept(self):
        assert normalize_text("<page_number>٣٧١</page_number>") == "٣٧١"

    def test_table_tags_stripped_cell_text_kept(self):
        text = "<table><thead><tr><th>الصفحة</th></tr></thead></table>"
        assert normalize_text(text) == "الصفحة"

    def test_watermark_unwrapped_content_kept(self):
        assert normalize_text("<watermark>www.rewity.com</watermark>") == "www.rewity.com"

    def test_markdown_bold_and_headings_stripped(self):
        assert normalize_text("**نص** مهم") == "نص مهم"
        assert normalize_text("# عنوان رئيسي") == "عنوان رئيسي"

    def test_version_identifier_available(self):
        assert NORMALIZATION_VERSION == "v1"
