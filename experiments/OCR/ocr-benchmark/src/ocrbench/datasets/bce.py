"""BCE Arabic v1 loader (199-sample processed subset).

Pairing is manifest-driven only: the manifest is the sole identity/lineage
anchor, and 80 of the 199 image↔XML mappings use normalized stems, so
filename-based inference is forbidden by construction.
"""

from __future__ import annotations

import json
from pathlib import Path

from ocrbench import paths
from ocrbench.types import Sample

BCE_ROOT: Path = paths.PROCESSED_ROOT / "bce-arabic-v1-balanced"

EXPECTED_SAMPLES = 199
DATASET_NAME = "bce-arabic-v1"
REQUIRED_FIELDS = (
    "sample_id",
    "category",
    "image_relative_path",
    "xml_relative_path",
    "mapping_method",
    "reading_order_exists",
)


def _resolve_under_root(relative: str) -> Path:
    resolved = (BCE_ROOT / relative).resolve()
    if not resolved.is_relative_to(BCE_ROOT.resolve()):
        raise ValueError(f"bce: manifest path escapes dataset root: {relative!r}")
    return resolved


def load_bce() -> list[Sample]:
    """Return the 199 manifest-defined BCE samples with PAGE-XML GT paths."""
    manifest = json.loads((BCE_ROOT / "manifest.json").read_text(encoding="utf-8"))

    if manifest.get("dataset") != DATASET_NAME:
        raise ValueError(
            f"bce: manifest dataset {manifest.get('dataset')!r} != {DATASET_NAME!r}"
        )
    documents = manifest.get("documents")
    if not isinstance(documents, list):
        raise ValueError("bce: manifest has no documents list")

    totals = manifest.get("totals") or {}
    declared = totals.get("selected_samples", EXPECTED_SAMPLES)
    if len(documents) != EXPECTED_SAMPLES or declared != EXPECTED_SAMPLES:
        raise ValueError(
            f"bce: expected {EXPECTED_SAMPLES} manifest entries "
            f"(documents={len(documents)}, totals.selected_samples={declared})"
        )

    samples: list[Sample] = []
    seen: set[str] = set()
    for index, entry in enumerate(documents):
        missing = [f for f in REQUIRED_FIELDS if f not in entry]
        if missing:
            raise ValueError(f"bce: entry #{index} missing fields {missing}")

        sample_id = entry["sample_id"]
        if sample_id in seen:
            raise ValueError(f"bce: duplicate sample id {sample_id!r}")
        seen.add(sample_id)

        mapping_method = entry["mapping_method"]
        if mapping_method not in ("exact", "normalized-stem"):
            raise ValueError(
                f"bce {sample_id}: unknown mapping_method {mapping_method!r}"
            )

        image_path = _resolve_under_root(entry["image_relative_path"])
        xml_path = _resolve_under_root(entry["xml_relative_path"])
        if not image_path.is_file():
            raise ValueError(f"bce {sample_id}: missing image {image_path}")
        if not xml_path.is_file():
            raise ValueError(f"bce {sample_id}: missing xml {xml_path}")

        samples.append(
            Sample(
                sample_id=sample_id,
                image_path=image_path,
                gt_xml_path=xml_path,
                categories=[entry["category"]],
                metadata={
                    "mapping_method": mapping_method,
                    "reading_order_exists": bool(entry["reading_order_exists"]),
                    "image_width": entry.get("image_width"),
                    "image_height": entry.get("image_height"),
                    "number_of_regions": entry.get("number_of_regions"),
                },
            )
        )

    if len(samples) != EXPECTED_SAMPLES:
        raise ValueError(f"bce: expected {EXPECTED_SAMPLES} samples, loaded {len(samples)}")

    samples.sort(key=lambda s: s.sample_id)
    return samples
