"""Centralized text normalization (handbook §6.2, normalization_version v1).

Applied identically to reference and hypothesis before the *normalized*
score. Raw scores are always computed on unmodified strings first.

Policy (v1) — deliberately light; anything not listed here is NOT applied:

1. Unicode NFC
2. Misraj markup stripped to plain text:
   - ``<img>...</img>`` dropped entirely (figure placeholders whose inner
     text "image here" is not content an engine should reproduce)
   - every other tag (``<page_number>``, ``<table>``/``<tr>``/``<td>``,
     ``<watermark>``, ``<ins>``, ...) unwrapped — tags removed, inner
     textual content KEPT
3. Markdown emphasis markers removed: ``**``, ``__``, backticks;
   ATX heading markers (line-leading #..######) removed, heading text kept
4. Whitespace collapsed to single spaces, trimmed
5. Tashkeel stripped: U+064B-U+0652 + superscript-alef U+0670
6. Alef/Hamza folding: أ إ آ → ا  (bare alef unchanged)
7. Yeh/Alef-maqsura folding: ى → ي
8. Latin casefold

Explicitly PRESERVED (over-normalization guards): digits (Western and
Arabic-Indic), punctuation, teh marbuta ة vs heh ه distinction, tatweel ـ,
alef-wasla ٱ, all other Arabic letters, semantic content.

Deviation note: ى→ي is required by the implementation-stage policy but not
yet present in handbook §6.2's table — flagged for the next handbook
revision (the table's own protocol requires recording additions).
"""

from __future__ import annotations

import re
import unicodedata

NORMALIZATION_VERSION = "v1"

NORMALIZATION_NOTES = (
    "v1: NFC; markup stripped to plain text (<img> dropped whole, other tags "
    "unwrapped keeping inner text); **/__/backtick/heading markers removed; "
    "whitespace collapsed; tashkeel U+064B-0652+U+0670 stripped; alef-hamza "
    "أإآ→ا; yeh ى→ي; Latin casefold. Digits, punctuation, ة/ه, tatweel, "
    "ٱ preserved."
)

_TASHKEEL_RE = re.compile(r"[\u064B-\u0652\u0670]")
_IMG_BLOCK_RE = re.compile(r"<img\b.*?</img\s*>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
_MD_EMPH_RE = re.compile(r"\*\*|__|`")
_MD_HEADING_RE = re.compile(r"^(#{1,6})\s+", re.MULTILINE)

_ALEF_FOLD = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا"})
_YEH_FOLD = str.maketrans({"ى": "ي"})


def normalize_text(text: str) -> str:
    """Normalize one side of a comparison; never mutates stored raw text."""
    if not isinstance(text, str):
        raise TypeError(f"normalize_text expects str, got {type(text)!r}")

    normalized = unicodedata.normalize("NFC", text)
    normalized = _IMG_BLOCK_RE.sub(" ", normalized)
    normalized = _TAG_RE.sub(" ", normalized)
    normalized = _MD_EMPH_RE.sub("", normalized)
    normalized = _MD_HEADING_RE.sub("", normalized)
    normalized = " ".join(normalized.split())
    normalized = _TASHKEEL_RE.sub("", normalized)
    normalized = normalized.translate(_ALEF_FOLD).translate(_YEH_FOLD)
    return normalized.casefold().strip()
