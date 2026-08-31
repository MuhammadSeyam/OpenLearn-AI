#!/usr/bin/env python3
"""
audit_custom_manifest.py

Read-only audit of the custom OCR benchmark dataset against the
Phase 2 canonical contract:

  raw filename stem == GT filename stem == metadata key == manifest sample_id
  (exact, case-sensitive; 85/85/85/85)

Checks performed:
- Identity across raw files / GT / metadata / manifest (exact, case-sensitive).
- Duplicate identities anywhere in the chain.
- Digital/scanned rule: ID contains "digital" -> *_born_digital category,
  otherwise *_scanned. Extension/folder/provenance are irrelevant.
- Category <-> feature consistency, both directions:
    multi_column      <-> multi_column
    tables            <-> table
    formulas          <-> formula
    figures_diagrams  <-> figure
    dense_academic    <-> dense
    noisy_low_quality <-> noisy
- Language <-> category consistency:
    english_*          -> language includes "en"
    arabic_*           -> language includes "ar"
    arabic_english_mixed -> language == {"ar","en"}
- Ground truth: exactly one non-empty UTF-8 .txt per raw identity,
  no missing, no orphans, no duplicates.
- Manifest structural validation: schema fields, duplicate IDs/pages,
  source_type/page validity (document-level PDFs have page = null),
  invalid categories/features/language/evaluation/GT values,
  filesystem cross-check.

This script never modifies anything.
"""

import argparse
import json
import os
import sys

try:
    import yaml
except ImportError:
    yaml = None

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
VALID_SOURCE_TYPES = {"pdf", "image"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
PDF_EXTS = {".pdf"}
IGNORED_FILENAMES = {"manifest.json", "readme.md"}

# Phase 2 FINAL decision: document-level samples (never expanded to pages).
DOCUMENT_LEVEL_PDFS = {"custom_multi_column_004"}

# category <-> feature pairs (both directions must hold)
CAT2FEAT = {
    "multi_column": "multi_column",
    "tables": "table",
    "formulas": "formula",
    "figures_diagrams": "figure",
    "dense_academic": "dense",
    "noisy_low_quality": "noisy",
}

DIGITAL_TOKEN = "digital"


def discover_on_disk(dataset_root):
    """Return {canonical_sample_id: relative_path} for all dataset files."""
    found = {}
    for dirpath, dirnames, filenames in os.walk(dataset_root):
        dirnames[:] = [d for d in dirnames if d != ".venv"]
        for fname in filenames:
            if fname.lower() in IGNORED_FILENAMES:
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in IMAGE_EXTS and ext not in PDF_EXTS:
                continue
            rel_path = os.path.relpath(os.path.join(dirpath, fname), dataset_root)
            rel_path = rel_path.replace(os.sep, "/")
            sid = os.path.splitext(fname)[0]  # exact, case-sensitive stem
            if sid in found:
                print(f"AUDIT FATAL: duplicate canonical identity '{sid}' "
                      f"({found[sid]} and {rel_path})", file=sys.stderr)
                sys.exit(1)
            found[sid] = rel_path
    return found


def discover_gt(gt_dir):
    """Return list of (gt_id, filename) for .txt ground-truth files."""
    gts = []
    if os.path.isdir(gt_dir):
        for fname in sorted(os.listdir(gt_dir)):
            if fname.endswith(".txt"):
                gts.append((os.path.splitext(fname)[0], fname))
    return gts


def section(title):
    print()
    print(f"== {title} ==")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/raw/custom/manifest.json")
    ap.add_argument("--dataset-root", default="data/raw/custom")
    ap.add_argument("--metadata", default="configs/custom_manifest_metadata.yaml")
    ap.add_argument("--ground-truth", default="data/ground_truth/custom")
    args = ap.parse_args()

    problems = []  # (severity, message)

    def err(msg):
        problems.append(("ERROR", msg))

    def warn(msg):
        problems.append(("WARN", msg))

    # ------------------------------------------------------------------
    # Load inputs
    # ------------------------------------------------------------------
    if not os.path.exists(args.manifest):
        print(f"AUDIT ERROR: manifest not found at {args.manifest}", file=sys.stderr)
        sys.exit(1)
    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    docs = manifest.get("documents", [])

    on_disk = discover_on_disk(args.dataset_root)
    gt_pairs = discover_gt(args.ground_truth)
    gt_map = {}
    gt_dupes = []
    for gid, fname in gt_pairs:
        if gid in gt_map:
            gt_dupes.append(gid)
        else:
            gt_map[gid] = fname

    meta = {}
    if yaml is not None and os.path.exists(args.metadata):
        with open(args.metadata, "r", encoding="utf-8") as f:
            meta_raw = yaml.safe_load(f) or {}
        meta = {k: v for k, v in meta_raw.items() if isinstance(v, dict)}

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    section("Schema")
    print(f"schema          : {manifest.get('schema')}")
    print(f"schema_version  : {manifest.get('schema_version')}")
    print(f"dataset         : {manifest.get('dataset')}")
    print(f"created         : {manifest.get('created')}")
    print(f"sample_unit     : {manifest.get('sample_unit')}")

    # ------------------------------------------------------------------
    # Identity audit (raw / GT / metadata / manifest)
    # ------------------------------------------------------------------
    section("Identity audit (raw == GT == metadata == manifest)")

    raw_ids = set(on_disk.keys())
    gt_ids = set(gt_map.keys())
    meta_ids = set(meta.keys())
    manifest_ids_list = [d.get("sample_id") for d in docs]
    manifest_ids = set(manifest_ids_list)

    print(f"raw identities       : {len(raw_ids)}")
    print(f"GT identities        : {len(gt_ids)}")
    print(f"metadata identities  : {len(meta_ids)}")
    print(f"manifest sample IDs  : {len(manifest_ids)} ({len(manifest_ids_list)} documents)")

    # duplicates within each layer
    seen = set()
    man_dupes = sorted({i for i in manifest_ids_list if i in seen or seen.add(i)})
    if man_dupes:
        for i in man_dupes:
            err(f"duplicate manifest sample_id: {i}")

    for label, layer in (("raw", raw_ids), ("metadata", meta_ids)):
        dupes = len(layer)
        # duplicates inside a set are impossible; cross-layer checks below cover it

    if not (raw_ids == gt_ids == meta_ids == manifest_ids):
        only_raw = sorted(raw_ids - manifest_ids - gt_ids - meta_ids)
        only_gt = sorted(gt_ids - raw_ids - meta_ids - manifest_ids)
        only_meta = sorted(meta_ids - raw_ids - gt_ids - manifest_ids)
        only_man = sorted(manifest_ids - raw_ids - gt_ids - meta_ids)
        if only_raw:
            for i in only_raw:
                err(f"raw identity present only on disk (no GT/metadata/manifest): {i}")
        if only_gt:
            for i in only_gt:
                err(f"orphan GT (no raw sample): {i}")
        if only_meta:
            for i in only_meta:
                err(f"orphan metadata key (no raw sample): {i}")
        if only_man:
            for i in only_man:
                err(f"manifest sample_id not found on disk: {i}")
        partial_sets = [
            ("missing from GT", raw_ids - gt_ids),
            ("missing from metadata", raw_ids - meta_ids),
            ("missing from manifest", raw_ids - manifest_ids),
        ]
        for label, s in partial_sets:
            for i in sorted(s):
                err(f"raw identity '{i}' is {label}")
    else:
        print("identity chain EXACT MATCH (case-sensitive)")

    if gt_dupes:
        for g in sorted(set(gt_dupes)):
            err(f"duplicate GT identity: {g}")

    # ------------------------------------------------------------------
    # Ground truth content audit
    # ------------------------------------------------------------------
    section("Ground-truth content")
    empty_gt, bad_encoding = [], []
    for gid, fname in gt_pairs:
        p = os.path.join(args.ground_truth, fname)
        try:
            data = open(p, "rb").read()
        except OSError as e:
            err(f"cannot read GT file {fname}: {e}")
            continue
        if len(data) == 0:
            empty_gt.append(fname)
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            bad_encoding.append(fname)
    for f in empty_gt:
        err(f"empty GT file: {f}")
    for f in bad_encoding:
        err(f"non-UTF-8 GT file: {f}")
    print(f"empty GT files     : {len(empty_gt)}")
    print(f"non-UTF-8 GT files : {len(bad_encoding)}")

    # ------------------------------------------------------------------
    # Per-document rule audits over the MANIFEST
    # ------------------------------------------------------------------
    section("Digital/scanned rule (ID token is authoritative)")
    ds_violations = 0
    for d in docs:
        sid = d.get("sample_id") or ""
        cats = d.get("categories") or []
        has_digital = DIGITAL_TOKEN in sid
        bd = [c for c in cats if c.endswith("_born_digital")]
        sc = [c for c in cats if c in ("english_scanned", "arabic_scanned")]
        if has_digital and sc:
            err(f"{sid}: ID contains '{DIGITAL_TOKEN}' but categorized scanned {sc}")
            ds_violations += 1
        if (not has_digital) and bd:
            err(f"{sid}: ID lacks '{DIGITAL_TOKEN}' but categorized born-digital {bd}")
            ds_violations += 1
    print(f"violations: {ds_violations}")

    section("Category <-> feature consistency (both directions)")
    fwd_viol = rev_viol = 0
    for d in docs:
        sid = d.get("sample_id") or ""
        cats = d.get("categories") or []
        feats = d.get("features") or {}
        for cat, feat in CAT2FEAT.items():
            if cat in cats and feats.get(feat) is not True:
                err(f"{sid}: category '{cat}' present but features.{feat} is {feats.get(feat)!r} (must be true)")
                fwd_viol += 1
            if feats.get(feat) is True and cat not in cats:
                err(f"{sid}: features.{feat}=true but category '{cat}' missing")
                rev_viol += 1
    print(f"category->feature violations: {fwd_viol}")
    print(f"feature->category violations: {rev_viol}")

    section("Language <-> category consistency")
    lang_viol = 0
    for d in docs:
        sid = d.get("sample_id") or ""
        cats = d.get("categories") or []
        lang = d.get("language")
        langs = set(lang or [])
        if any(c.startswith("english_") for c in cats) and "en" not in langs:
            err(f"{sid}: english_* category but language lacks 'en' ({lang})")
            lang_viol += 1
        if any(c.startswith("arabic_") for c in cats) and "ar" not in langs:
            err(f"{sid}: arabic_* category but language lacks 'ar' ({lang})")
            lang_viol += 1
        if "arabic_english_mixed" in cats and not {"ar", "en"} <= langs:
            err(f"{sid}: arabic_english_mixed but language is not ['ar','en'] ({lang})")
            lang_viol += 1
    print(f"violations: {lang_viol}")

    # ------------------------------------------------------------------
    # Structural manifest validation
    # ------------------------------------------------------------------
    section("Counts")
    physical_claimed = manifest.get("physical_files")
    logical_claimed = manifest.get("logical_samples")
    unique_paths = {d.get("path") for d in docs}
    print(f"physical_files (field)   : {physical_claimed}")
    print(f"logical_samples (field)  : {logical_claimed}")
    print(f"documents array length   : {len(docs)}")
    print(f"unique paths referenced  : {len(unique_paths)}")
    if logical_claimed != len(docs):
        err(f"logical_samples field ({logical_claimed}) != len(documents) ({len(docs)})")
    if physical_claimed != len(unique_paths):
        err(f"physical_files field ({physical_claimed}) != unique paths ({len(unique_paths)})")

    section("Field validation")
    inv = {"source_type": 0, "page": 0, "category": 0, "feature": 0,
           "language": 0, "evaluation": 0, "gt_status": 0}
    for d in docs:
        sid = d.get("sample_id")
        st = d.get("source_type")
        page = d.get("page")
        if st not in VALID_SOURCE_TYPES:
            err(f"{sid}: invalid source_type '{st}'")
            inv["source_type"] += 1
        else:
            if st == "image" and page is not None:
                err(f"{sid}: image sample has non-null page ({page})")
                inv["page"] += 1
            if st == "pdf":
                is_doc_level = sid in DOCUMENT_LEVEL_PDFS
                if is_doc_level and page is not None:
                    err(f"{sid}: document-level pdf must have page=null (got {page})")
                    inv["page"] += 1
                if not is_doc_level and (not isinstance(page, int) or page < 1):
                    err(f"{sid}: pdf sample has invalid page ({page})")
                    inv["page"] += 1

        cats = d.get("categories") or []
        for c in cats:
            if c not in CANONICAL_CATEGORIES:
                err(f"{sid}: invalid category '{c}'")
                inv["category"] += 1

        feats = d.get("features") or {}
        if not isinstance(feats, dict):
            err(f"{sid}: features is not a mapping")
            inv["feature"] += 1
        else:
            for k, v in feats.items():
                if k not in FEATURE_KEYS:
                    err(f"{sid}: invalid feature key '{k}'")
                    inv["feature"] += 1
                elif v is not None and not isinstance(v, bool):
                    err(f"{sid}: feature '{k}' non-boolean/non-null value {v!r}")
                    inv["feature"] += 1

        lang = d.get("language")
        if lang is not None:
            if not isinstance(lang, list) or not lang or any(t not in VALID_LANGUAGE_TOKENS for t in lang):
                err(f"{sid}: malformed language value {lang!r}")
                inv["language"] += 1

        ev = d.get("evaluation") or {}
        if not isinstance(ev.get("core"), bool) or not isinstance(ev.get("extended"), bool):
            err(f"{sid}: invalid evaluation block {ev!r}")
            inv["evaluation"] += 1

        gt = d.get("ground_truth") or {}
        if gt.get("status") not in VALID_GT_STATUSES:
            err(f"{sid}: invalid ground_truth.status {gt.get('status')!r}")
            inv["gt_status"] += 1

    for k, v in inv.items():
        print(f"invalid {k:12s}: {v}")

    # ------------------------------------------------------------------
    # Filesystem cross-check
    # ------------------------------------------------------------------
    section("Filesystem cross-check")
    missing_on_disk = sorted(set(unique_paths) - set(on_disk.values()))
    untracked = sorted(p for sid, p in on_disk.items() if p not in unique_paths)
    print(f"files on disk                      : {len(on_disk)}")
    print(f"in manifest but missing on disk    : {len(missing_on_disk)}")
    for p in missing_on_disk:
        err(f"manifest references missing file: {p}")
    print(f"on disk but absent from manifest   : {len(untracked)}")
    for p in untracked:
        err(f"file on disk not in manifest: {p}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    section("Summary")
    errors = [p for p in problems if p[0] == "ERROR"]
    warns = [p for p in problems if p[0] == "WARN"]
    print(f"errors   : {len(errors)}")
    print(f"warnings : {len(warns)}")
    if errors:
        print("\nAUDIT FAILED -- errors found:")
        for _, msg in errors:
            print(f"  [ERROR] {msg}")
        sys.exit(1)
    else:
        print("\nAUDIT PASSED (no errors)" + (f", {len(warns)} warning(s)" if warns else ""))


if __name__ == "__main__":
    main()
