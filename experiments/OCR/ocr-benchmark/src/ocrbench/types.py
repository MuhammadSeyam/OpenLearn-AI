"""Minimal shared dataclasses for the OCR benchmark.

One Sample per dataset unit, one Prediction per engine invocation, one Region
per layout region. Deliberately small: no schema versioning, no base classes,
no fields without a current consumer.

Rules encoded here:
- Prediction.raw_output carries the engine's verbatim output; normalization
  belongs exclusively to the metric layer.
- Failed predictions stay in the data (ok=False + error); they are never
  silently dropped.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Region:
    """A single layout region emitted by an engine or present in GT XML."""

    box: tuple[float, float, float, float]
    type: str
    region_id: str | None = None
    text: str | None = None


@dataclass
class Sample:
    """One benchmark unit: an image plus whatever GT exists for it."""

    sample_id: str
    image_path: Path
    reference_text: str | None = None
    gt_xml_path: Path | None = None
    categories: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class Prediction:
    """The result of one engine invocation on one sample."""

    sample_id: str
    ok: bool
    text: str | None
    raw_output: str
    regions: list[Region] | None = None
    reading_order: list[str] | None = None
    error: str | None = None
    elapsed_s: float = 0.0


__all__ = [
    "Region",
    "Sample",
    "Prediction",
]
