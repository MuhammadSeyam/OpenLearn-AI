"""Pure text metrics: CER/WER, raw and normalized, micro and macro.

Tokenization policy: whitespace splitting only (str.split) — no
language-specific tokenizers, no Arabic NLP preprocessing.

Conventions (handbook §6.1-6.3):
- CER = edit_distance(reference, hypothesis) / len(reference)
- WER = word_edit_distance / reference_word_count
- Micro = pooled distances / pooled reference lengths (primary aggregate)
- Macro = mean of per-sample scores (secondary)
- Empty references are the caller's exclusion responsibility; these
  functions raise ValueError on them so they can never silently score 0.
- A failed sample is scored with an empty hypothesis, which naturally
  yields exactly 1.0 against any non-empty reference (worst-case rule).
"""

from __future__ import annotations

import editdistance

Pair = tuple[str, str]


def cer(reference: str, hypothesis: str) -> float:
    """Character error rate for one sample."""
    if not reference.strip():
        raise ValueError("cer: empty reference (must be excluded upstream)")
    return editdistance.eval(reference, hypothesis) / len(reference)


def wer(reference: str, hypothesis: str) -> float:
    """Word error rate for one sample (whitespace tokenization)."""
    if not reference.strip():
        raise ValueError("wer: empty reference (must be excluded upstream)")
    reference_words = reference.split()
    hypothesis_words = hypothesis.split()
    return editdistance.eval(reference_words, hypothesis_words) / len(reference_words)


def _require_pairs(pairs: list[Pair]) -> None:
    if not pairs:
        raise ValueError("aggregate: no scorable samples")
    for reference, _ in pairs:
        if not reference.strip():
            raise ValueError("aggregate: empty reference (exclude upstream)")


def micro_cer(pairs: list[Pair]) -> float:
    """Pooled CER: sum(edit distance) / sum(reference characters)."""
    _require_pairs(pairs)
    total_distance = sum(editdistance.eval(r, h) for r, h in pairs)
    total_length = sum(len(r) for r, _ in pairs)
    return total_distance / total_length


def macro_cer(pairs: list[Pair]) -> float:
    """Mean of per-sample CER."""
    _require_pairs(pairs)
    values = [cer(r, h) for r, h in pairs]
    return sum(values) / len(values)


def micro_wer(pairs: list[Pair]) -> float:
    """Pooled WER: sum(word edits) / sum(reference words)."""
    _require_pairs(pairs)
    total_distance = sum(
        editdistance.eval(r.split(), h.split()) for r, h in pairs
    )
    total_words = sum(len(r.split()) for r, _ in pairs)
    return total_distance / total_words


def macro_wer(pairs: list[Pair]) -> float:
    """Mean of per-sample WER."""
    _require_pairs(pairs)
    values = [wer(r, h) for r, h in pairs]
    return sum(values) / len(values)
