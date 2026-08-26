"""Custom dataset loader (85 verified samples).

Pairs each manifest logical sample with its flat ground-truth text file under
data/ground_truth/custom. Source files are referenced as-is; PDFs are NOT
rendered here (execution-phase concern), so image_path carries the actual
source path and metadata records source_type.
"""

from __future__ import annotations

import json
from pathlib import Path

from ocrbench import paths
from ocrbench.types import Sample

CUSTOM_ROOT: Path = paths.PROCESSED_ROOT / "custom"
GT_ROOT: Path = paths.CUSTOM_GROUND_TRUTH_ROOT

EXPECTED_SAMPLES = 85
SCHEMA_VERSION = 4


def _read_manifest() -> dict:
    manifest_path = CUSTOM_ROOT / "manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _source_path(sample_id: str, relative: str) -> Path:
    resolved = (CUSTOM_ROOT / relative).resolve()
    if not resolved.is_relative_to(CUSTOM_ROOT.resolve()):
        raise ValueError(f"custom {sample_id}: source path escapes root: {relative!r}")
    if not resolved.is_file():
        raise ValueError(f"custom {sample_id}: missing source file {resolved}")
    return resolved


def _read_ground_truth(sample_id: str) -> str:
    gt_path = GT_ROOT / f"{sample_id}.txt"
    if not gt_path.is_file():
        raise ValueError(f"custom {sample_id}: missing ground truth {gt_path}")
    text = gt_path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"custom {sample_id}: empty ground truth {gt_path}")
    return text


def load_custom() -> list[Sample]:
    """Return the 85 Custom samples paired with their verified GT text."""
    manifest = _read_manifest()
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"custom: manifest schema_version {manifest.get('schema_version')!r} "
            f"!= {SCHEMA_VERSION!r}"
        )
    documents = manifest.get("documents")
    if not isinstance(documents, list):
        raise ValueError("custom: manifest has no documents list")

    samples: list[Sample] = []
    seen: set[str] = set()
    for index, entry in enumerate(documents):
        sample_id = entry.get("sample_id")
        if not isinstance(sample_id, str) or not sample_id:
            raise ValueError(f"custom: entry #{index} has invalid sample_id {sample_id!r}")
        if sample_id in seen:
            raise ValueError(f"custom: duplicate sample id {sample_id!r}")
        seen.add(sample_id)

        source_type = entry.get("source_type")
        if source_type not in ("pdf", "image"):
            raise ValueError(f"custom {sample_id}: unknown source_type {source_type!r}")

        language = entry.get("language")
        categories = entry.get("categories")
        features = entry.get("features")
        if not isinstance(language, list) or not language:
            raise ValueError(f"custom {sample_id}: missing language labels")
        if not isinstance(categories, list) or not categories:
            raise ValueError(f"custom {sample_id}: missing category labels")
        if not isinstance(features, dict):
            raise ValueError(f"custom {sample_id}: missing feature flags")

        reference_text = _read_ground_truth(sample_id)
        source_path = _source_path(sample_id, entry["path"])

        samples.append(
            Sample(
                sample_id=sample_id,
                image_path=source_path,
                reference_text=reference_text,
                categories=list(categories),
                metadata={
                    "source_type": source_type,
                    # page=None marks the one document-level PDF exception
                    # (custom_multi_column_004); preserved, never flattened.
                    "page": entry.get("page"),
                    "language": list(language),
                    "features": dict(features),
                },
            )
        )

    gt_stems = {p.stem for p in GT_ROOT.glob("*.txt")}
    if gt_stems != seen:
        orphaned = sorted(gt_stems - seen)[:5]
        unpaired = sorted(seen - gt_stems)[:5]
        raise ValueError(
            f"custom: GT/manifest identity mismatch (orphaned={orphaned}, "
            f"unpaired={unpaired})"
        )

    if len(samples) != EXPECTED_SAMPLES:
        raise ValueError(
            f"custom: expected {EXPECTED_SAMPLES} samples "
            f"(documents={len(documents)}, "
            f"physical_files={manifest.get('physical_files')}, "
            f"logical_samples={manifest.get('logical_samples')}, "
            f"loaded={len(samples)})"
        )

    samples.sort(key=lambda s: s.sample_id)
    return samples
