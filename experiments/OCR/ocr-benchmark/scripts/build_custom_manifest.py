#!/usr/bin/env python3
"""
build_custom_manifest.py

Builds a deterministic, multi-label manifest for the finalized custom OCR
benchmark dataset located at data/processed/custom/.

CANONICAL IDENTITY CONTRACT (Phase 2 decision - FINAL)
------------------------------------------------------
The current raw filename STEM is the canonical sample ID:

    raw filename stem == GT filename stem == metadata key == manifest sample_id

- The comparison is exact and case-sensitive ("Custom_English_scanned_002"
  stays exactly that; no lowercasing, no normalization).
- The builder NEVER prepends an additional prefix:
  "custom_custom_english_born_digital_001_p001" must remain exactly that,
  never "custom_custom_custom_english_born_digital_001_p001".
- Each physical file contributes exactly ONE logical sample
  ("one benchmark sample = one PDF page or one standalone image"; all
  currently shipped PDFs are single-page extractions).

DOCUMENT-LEVEL EXCEPTION (Phase 2 decision - FINAL)
---------------------------------------------------
Stems listed in DOCUMENT_LEVEL_PDFS are single document-level samples
(currently: "custom_multi_column_004"). They get source_type "pdf" with
page = null and are never expanded into _pNNN pages.

DESIGN
------
- The dataset on disk is treated as READ-ONLY except manifest.json.
- Folders are physical organization only; never a source of semantics.
- All semantic metadata comes exclusively from
  configs/custom_manifest_metadata.yaml, keyed by canonical sample_id.
  Metadata keys that do not correspond to any discovered sample_id are an
  identity mismatch -> the build FAILS loudly instead of inventing IDs.
- A multi-page PDF whose stem is not in DOCUMENT_LEVEL_PDFS is rejected
  (split it first with data/raw/custom/script.py or declare it
  document-level); this prevents silently generating new _pNNN identities.
- Ground truth defaults to {"status": "pending"} unless overridden here.

USAGE
-----
    python3 scripts/build_custom_manifest.py \
        --dataset-root data/processed/custom \
        --metadata configs/custom_manifest_metadata.yaml \
        --output data/processed/custom/manifest.json

Relative CLI paths are interpreted against the benchmark project root
(ocr-benchmark/), regardless of the current working directory.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bench_paths import resolve_path  # noqa: E402

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(1)

SCHEMA_NAME = "openlearn-ocrbench-manifest"
SCHEMA_VERSION = 4

IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
PDF_EXTS = {".pdf"}
IGNORED_FILENAMES = {"manifest.json", "readme.md"}

# Phase 2 FINAL decision: these stems are document-level samples.
# They are NOT split into pages even if the PDF contains multiple pages.
DOCUMENT_LEVEL_PDFS = {"custom_multi_column_004"}

CANONICAL_CATEGORIES = [
    "english_born_digital",
    "arabic_born_digital",
    "english_scanned",
    "arabic_scanned",
    "arabic_english_mixed",
    "multi_column",
    "tables",
    "formulas",
    "figures_diagrams",
    "slides",
    "dense_academic",
    "noisy_low_quality",
]

FEATURE_KEYS = ["multi_column", "table", "formula", "figure", "dense", "noisy"]

VALID_LANGUAGE_TOKENS = {"en", "ar"}
VALID_GT_STATUSES = {"pending", "verified", "partial"}


class BuildError(Exception):
    """Raised for any condition that should fail the build loudly."""


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def discover_files(dataset_root):
    """Find all supported dataset files, sorted by relative path."""
    found = []
    for dirpath, dirnames, filenames in os.walk(dataset_root):
        dirnames[:] = [d for d in dirnames if d != ".venv"]
        for fname in sorted(filenames):
            if fname.lower() in IGNORED_FILENAMES:
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in IMAGE_EXTS and ext not in PDF_EXTS:
                continue
            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, dataset_root)
            found.append((rel_path.replace(os.sep, "/"), fname, ext))
    return sorted(found)


def pdf_page_count(dataset_root, rel_path):
    full_path = os.path.join(dataset_root, rel_path)
    try:
        out = subprocess.run(
            ["pdfinfo", full_path],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except FileNotFoundError:
        raise BuildError(
            "pdfinfo (poppler-utils) is not installed. Install it to read "
            "PDF page counts, e.g.: apt-get install poppler-utils"
        )
    except subprocess.CalledProcessError as e:
        raise BuildError(f"pdfinfo failed on '{rel_path}': {e.stderr.strip()}")

    m = re.search(r"^Pages:\s+(\d+)", out, flags=re.MULTILINE)
    if not m:
        raise BuildError(f"Could not parse page count from pdfinfo output for '{rel_path}'")
    return int(m.group(1))


def canonical_sample_id(fname):
    """
    Canonical sample ID = exact filename stem, byte-for-byte.

    No prefixing, no slugification, no case folding, no whitespace
    normalization. The stem IS the identity.
    """
    return os.path.splitext(fname)[0]


# ---------------------------------------------------------------------------
# Metadata loading + validation
# ---------------------------------------------------------------------------

def load_metadata(metadata_path):
    if not os.path.exists(metadata_path):
        return {}
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise BuildError(f"Metadata file '{metadata_path}' must be a mapping of sample_id -> metadata")
    return data


def validate_metadata_entry(sample_id, entry):
    if entry is None:
        return
    if not isinstance(entry, dict):
        raise BuildError(f"Metadata entry for '{sample_id}' must be a mapping")

    allowed_keys = {"language", "categories", "features", "evaluation", "ground_truth"}
    unknown = set(entry.keys()) - allowed_keys
    if unknown:
        raise BuildError(f"Metadata entry for '{sample_id}' has unknown keys: {sorted(unknown)}")

    lang = entry.get("language")
    if lang is not None:
        if not isinstance(lang, list) or not lang:
            raise BuildError(f"'{sample_id}': language must be null or a non-empty list, got {lang!r}")
        for tok in lang:
            if tok not in VALID_LANGUAGE_TOKENS:
                raise BuildError(f"'{sample_id}': invalid language token '{tok}'")

    cats = entry.get("categories")
    if cats is not None:
        if not isinstance(cats, list):
            raise BuildError(f"'{sample_id}': categories must be a list, got {cats!r}")
        for c in cats:
            if c not in CANONICAL_CATEGORIES:
                raise BuildError(f"'{sample_id}': invalid category '{c}'")

    features = entry.get("features")
    if features is not None:
        if not isinstance(features, dict):
            raise BuildError(
                f"'{sample_id}': features must be a mapping (got {type(features).__name__}). "
                "Use 'features:' followed by indented 'key: value' lines, not '- key: value' list items."
            )
        unknown_f = set(features.keys()) - set(FEATURE_KEYS)
        if unknown_f:
            raise BuildError(f"'{sample_id}': unknown feature keys {sorted(unknown_f)}")
        missing_f = set(FEATURE_KEYS) - set(features.keys())
        if missing_f:
            raise BuildError(f"'{sample_id}': missing feature keys {sorted(missing_f)}")
        for k, v in features.items():
            if v is not None and not isinstance(v, bool):
                raise BuildError(f"'{sample_id}': feature '{k}' must be null/true/false, got {v!r}")

    evaluation = entry.get("evaluation")
    if evaluation is not None:
        if not isinstance(evaluation, dict):
            raise BuildError(f"'{sample_id}': evaluation must be a mapping")
        unknown_e = set(evaluation.keys()) - {"core", "extended"}
        if unknown_e:
            raise BuildError(f"'{sample_id}': unknown evaluation keys {sorted(unknown_e)}")
        for k in ("core", "extended"):
            if k in evaluation and not isinstance(evaluation[k], bool):
                raise BuildError(f"'{sample_id}': evaluation.{k} must be boolean")

    gt = entry.get("ground_truth")
    if gt is not None:
        if not isinstance(gt, dict) or "status" not in gt:
            raise BuildError(f"'{sample_id}': ground_truth must be a mapping with a 'status' key")
        if gt["status"] not in VALID_GT_STATUSES:
            raise BuildError(f"'{sample_id}': invalid ground_truth.status '{gt['status']}'")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_documents(dataset_root, metadata):
    files = discover_files(dataset_root)

    # Identity integrity: every stem must be unique across the dataset.
    seen_stems = {}
    for rel_path, fname, _ext in files:
        sid = canonical_sample_id(fname)
        if sid in seen_stems:
            raise BuildError(
                f"Duplicate canonical sample_id '{sid}': files "
                f"'{seen_stems[sid]}' and '{rel_path}' share the same stem."
            )
        seen_stems[sid] = rel_path

    documents = []
    physical_files = 0
    known_ids = set()

    for rel_path, fname, ext in files:
        physical_files += 1
        sample_id = canonical_sample_id(fname)

        if ext in IMAGE_EXTS:
            source_type = "image"
            page = None
        else:
            n_pages = pdf_page_count(dataset_root, rel_path)
            if sample_id in DOCUMENT_LEVEL_PDFS:
                source_type = "pdf"
                page = None          # document-level sample: whole file
            elif n_pages == 1:
                source_type = "pdf"
                page = 1             # single-page extraction
            else:
                # Refuse to silently mint new _pNNN identities.
                raise BuildError(
                    f"Multi-page PDF '{rel_path}' ({n_pages} pages) is not declared "
                    f"document-level. Split it into one-page PDFs first "
                    f"(data/processed/custom/script.py) or add its stem to "
                    f"DOCUMENT_LEVEL_PDFS in scripts/build_custom_manifest.py."
                )

        if sample_id in known_ids:
            raise BuildError(f"Duplicate sample_id generated: '{sample_id}'")
        known_ids.add(sample_id)

        entry = metadata.get(sample_id)
        validate_metadata_entry(sample_id, entry)
        entry = entry or {}

        features_in = entry.get("features") or {}
        features = {k: features_in.get(k, None) for k in FEATURE_KEYS}

        evaluation_in = entry.get("evaluation") or {}
        evaluation = {
            "core": evaluation_in.get("core", False),
            "extended": evaluation_in.get("extended", True),
        }

        gt_in = entry.get("ground_truth") or {"status": "pending"}

        documents.append({
            "sample_id": sample_id,
            "path": rel_path,
            "source_type": source_type,
            "page": page,
            "language": entry.get("language", None),
            "categories": entry.get("categories", []),
            "features": features,
            "evaluation": evaluation,
            "ground_truth": gt_in,
        })

    documents.sort(key=lambda d: d["sample_id"])
    return documents, physical_files


def check_orphan_metadata(metadata, documents):
    """Identity mismatch: metadata keys with no matching sample_id are fatal."""
    known_ids = {d["sample_id"] for d in documents}
    return sorted(set(metadata.keys()) - known_ids)


def load_existing_created(output_path):
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            return existing.get("created")
        except (json.JSONDecodeError, OSError):
            return None
    return None


def atomic_write_json(path, data):
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(prefix=".manifest_", suffix=".json.tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=False)
            f.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def main():
    parser = argparse.ArgumentParser(description="Build the custom OCR benchmark manifest.")
    parser.add_argument("--dataset-root", default="data/processed/custom")
    parser.add_argument("--metadata", default="configs/custom_manifest_metadata.yaml")
    parser.add_argument("--output", default="data/processed/custom/manifest.json")
    parser.add_argument(
        "--freeze-created",
        action="store_true",
        default=True,
        help="Preserve the existing 'created' timestamp across rebuilds (default: on).",
    )
    args = parser.parse_args()
    args.dataset_root = resolve_path(args.dataset_root)
    args.metadata = resolve_path(args.metadata)
    args.output = resolve_path(args.output)

    if not os.path.isdir(args.dataset_root):
        raise BuildError(f"Dataset root not found: {args.dataset_root}")

    metadata = load_metadata(args.metadata)
    documents, physical_files = build_documents(args.dataset_root, metadata)

    # Identity mismatch check: FAIL, do not silently create new IDs.
    orphans = check_orphan_metadata(metadata, documents)
    if orphans:
        print("IDENTITY MISMATCH: metadata entries with no matching sample_id:", file=sys.stderr)
        for o in orphans:
            print(f"  - {o}", file=sys.stderr)
        raise BuildError(
            f"{len(orphans)} metadata key(s) do not match any canonical sample_id "
            "(canonical ID = exact filename stem). Fix the metadata keys."
        )

    missing_meta = sorted({d["sample_id"] for d in documents} - set(metadata.keys()))
    if missing_meta:
        print("WARNING: samples with no metadata entry (will be null/unassigned):", file=sys.stderr)
        for m in missing_meta:
            print(f"  - {m}", file=sys.stderr)

    created = load_existing_created(args.output) if args.freeze_created else None
    if not created:
        created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "dataset": "custom",
        "created": created,
        "sample_unit": "one benchmark sample = one PDF page or one standalone image",
        "physical_files": physical_files,
        "logical_samples": len(documents),
        "categories": {c: {"label": c} for c in CANONICAL_CATEGORIES},
        "documents": documents,
    }

    atomic_write_json(args.output, manifest)

    print(f"Wrote {args.output}")
    print(f"  physical_files  = {physical_files}")
    print(f"  logical_samples = {len(documents)}")


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        print(f"BUILD ERROR: {e}", file=sys.stderr)
        sys.exit(1)
