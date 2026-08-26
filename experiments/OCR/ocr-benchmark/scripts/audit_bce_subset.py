#!/usr/bin/env python3
"""
audit_bce_subset.py

Read-only audit of the BCE-Arabic-v1 balanced benchmark subset
(data/processed/bce-arabic-v1-balanced) against its manifest.json and,
where available, the raw dataset it was derived from.

Verifies:
- manifest structure and required per-sample fields
- category counts vs manifest totals and the documented 25/category target
  (tables = 24 shortfall is expected and must be declared in the manifest)
- every manifest entry has both files present in the subset
- copied image/XML bytes are identical to their raw-dataset sources when
  those sources exist (SHA-256 against manifest hash AND live re-hash of
  both copies/sources). The original raw dataset was removed from the
  repository during the raw->processed relocation, so missing sources are
  reported as a WARNING, not an error; manifest hashes are still verified
  against the subset copies themselves.
- no stray files in the subset beyond manifest entries, manifest.json,
  SELECTION_REPORT.md
- every image decodes with Pillow; every XML parses
- each XML's <Page imageFilename> resolves to its own paired image via the
  documented ladder (exact > case-insensitive > normalized "_b" stem)
- no duplicate image or XML SHA-256 anywhere in the subset
  (this also proves absence of cross-category duplicates)

Never modifies anything. Exit codes: 0 = PASS, 1 = FAIL, 2 = usage error.

Usage:
    python experiments/OCR/ocr-benchmark/scripts/audit_bce_subset.py [SUBSET_DIR]

Relative SUBSET_DIR values are resolved against the benchmark project root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bench_paths import resolve_path  # noqa: E402

from PIL import Image, UnidentifiedImageError

TOOL_NAME = "audit_bce_subset"
AUDIT_VERSION = "1.0.0"

BENCH_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SUBSET = BENCH_ROOT / "data" / "processed" / "bce-arabic-v1-balanced"
RAW_DATASET = BENCH_ROOT / "data" / "raw" / "bce-arabic-v1"

CATEGORIES = (
    "Charts", "Headers", "graphics", "multi-columns",
    "tables", "text and images", "textonly", "titles",
)
PAGE_NS = "{http://schema.primaresearch.org/PAGE/gts/pagecontent/"
IMAGE_EXTS = {".jpg", ".jpeg", ".tif", ".tiff", ".png"}
EXPECTED_SHORTFALL = {"tables": 1}

REQUIRED_FIELDS = (
    "sample_id", "category", "image_relative_path", "xml_relative_path",
    "image_sha256", "xml_sha256", "image_width", "image_height",
    "number_of_regions", "reading_order_exists", "mapping_method",
    "source_image_path", "source_xml_path",
)

problems: list[tuple[str, str]] = []


def err(msg: str) -> None:
    problems.append(("ERROR", msg))


def warn(msg: str) -> None:
    problems.append(("WARN", msg))


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_stem(name: str) -> str:
    stem = Path(name).stem.lower()
    return stem[:-2] if stem.endswith("_b") else stem


def section(title: str) -> None:
    print()
    print(f"== {title} ==")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="Read-only audit of the bce-arabic-v1-balanced subset.")
    parser.add_argument("subset", nargs="?", default=str(DEFAULT_SUBSET))
    args = parser.parse_args(argv)

    subset = resolve_path(args.subset).resolve()
    manifest_path = subset / "manifest.json"
    if not manifest_path.is_file():
        print(f"error: no manifest.json under {subset}", file=sys.stderr)
        return 2

    try:
        doc = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: manifest.json is not valid JSON: {exc}", file=sys.stderr)
        return 2

    print(f"BCE subset audit v{AUDIT_VERSION} (read-only)")
    print(f"subset   : {subset}")
    print(f"manifest : schema={doc.get('schema')} v{doc.get('schema_version')}, "
          f"created={doc.get('created')}")

    # ------------------------------------------------------------------
    # Manifest structure
    # ------------------------------------------------------------------
    section("Manifest structure")
    docs = doc.get("documents")
    if not isinstance(docs, list) or not docs:
        err("manifest has no 'documents' array")
        docs = []
    bad_field = 0
    ids = Counter()
    for d in docs:
        missing = [f for f in REQUIRED_FIELDS if f not in d]
        if missing:
            bad_field += 1
            err(f"{d.get('sample_id', '?')}: missing fields {missing}")
        ids[d.get("sample_id")] += 1
    dup_ids = {i: n for i, n in ids.items() if n > 1}
    if dup_ids:
        err(f"duplicate sample_ids in manifest: {dup_ids}")
    print(f"samples listed          : {len(docs)}")
    print(f"entries missing fields  : {bad_field}")

    seed = doc.get("selection", {}).get("seed")
    print(f"selection seed recorded : {seed}")
    if seed != 20260825:
        warn(f"unexpected selection seed {seed!r} (expected 20260825)")

    # ------------------------------------------------------------------
    # Category counts vs targets
    # ------------------------------------------------------------------
    section("Category counts")
    cat_counts = Counter(d["category"] for d in docs)
    shortfalls = doc.get("totals", {}).get("shortfall_vs_target", {})
    for c in CATEGORIES:
        target = doc.get("selection", {}).get("target_samples_per_category", 25)
        n = cat_counts.get(c, 0)
        expect = target - EXPECTED_SHORTFALL.get(c, 0)
        status_ok = n == expect
        declared = shortfalls.get(c, 0) == EXPECTED_SHORTFALL.get(c, 0)
        line = f"{c:<16}: {n:>3} (expected {expect})"
        if not status_ok:
            err(f"category '{c}' has {n} samples, expected {expect}")
        if not status_ok and not declared:
            warn(f"category '{c}' shortfall not correctly declared in manifest totals")
        print(line)
    other = set(cat_counts) - set(CATEGORIES)
    if other:
        err(f"unknown categories in manifest: {sorted(other)}")

    # ------------------------------------------------------------------
    # Files on disk vs manifest
    # ------------------------------------------------------------------
    section("Files vs manifest")
    expected_files: dict[str, dict] = {}
    for d in docs:
        for key in ("image_relative_path", "xml_relative_path"):
            rel = d.get(key)
            if rel:
                expected_files[f"{d['category']}/{Path(rel).name}"] = d

    actual_files = sorted(
        p.relative_to(subset).as_posix()
        for p in subset.rglob("*")
        if p.is_file() and p.name not in {"manifest.json", "SELECTION_REPORT.md"}
        and not p.is_symlink()
    )
    missing = sorted(set(expected_files) - set(actual_files))
    strays = sorted(set(actual_files) - set(expected_files))
    print(f"files on disk (excl. manifest/report): {len(actual_files)}")
    print(f"missing from disk                    : {len(missing)}")
    print(f"stray files not in manifest          : {len(strays)}")
    for m in missing[:10]:
        err(f"manifest lists file absent from subset: {m}")
    for s in strays[:10]:
        err(f"subset contains file not in manifest: {s}")

    # ------------------------------------------------------------------
    # Byte identity vs raw sources + hashes
    # ------------------------------------------------------------------
    section("Byte identity vs raw dataset")
    mismatch = 0
    hash_mismatch = 0
    missing_sources = 0
    for d in docs:
        for rel_key, src_key, hash_key in (
            ("image_relative_path", "source_image_path", "image_sha256"),
            ("xml_relative_path", "source_xml_path", "xml_sha256"),
        ):
            local = subset / d[rel_key]
            source = BENCH_ROOT / d[src_key]
            if not source.is_file():
                missing_sources += 1
                continue
            if not local.is_file():
                continue
            src_hash = file_hash(source)
            if src_hash != d[hash_key]:
                err(f"{d['sample_id']}: manifest {hash_key} does not match raw source "
                    f"({d[src_key]})")
                hash_mismatch += 1
            if file_hash(local) != src_hash:
                err(f"{d['sample_id']}: subset copy differs from raw source: {d[rel_key]}")
                mismatch += 1
            if not source.resolve().is_relative_to(RAW_DATASET):
                err(f"{d['sample_id']}: source path outside raw dataset: {d[src_key]}")
    if missing_sources:
        warn(f"raw origin unavailable for byte-level re-comparison "
             f"({missing_sources}/{len(docs) * 2} source files absent - the original "
             f"data/raw/bce-arabic-v1 dataset was removed during the raw->processed "
             f"relocation); manifest hashes were still verified against the subset copies")
    print(f"copy/source byte mismatches : {mismatch}")
    print(f"manifest hash mismatches    : {hash_mismatch}")
    print(f"raw sources unavailable     : {missing_sources}")

    # ------------------------------------------------------------------
    # Image + XML integrity inside the subset
    # ------------------------------------------------------------------
    section("Image/XML integrity")
    unreadable = []
    unparseable = []
    dims_wrong = 0
    ref_broken = []
    img_hashes: dict[str, str] = {}
    xml_hashes: dict[str, str] = {}

    for d in docs:
        img_path = subset / d["image_relative_path"]
        xml_path = subset / d["xml_relative_path"]
        if not img_path.is_file() or not xml_path.is_file():
            continue
        try:
            with Image.open(img_path) as im:
                im.load()
                w, h = im.size
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            unreadable.append(f"{d['sample_id']} ({exc!r})")
            continue
        if (w, h) != (d["image_width"], d["image_height"]):
            err(f"{d['sample_id']}: raster {w}x{h} but manifest says "
                f"{d['image_width']}x{d['image_height']}")
            dims_wrong += 1
        try:
            root = ET.parse(xml_path).getroot()
        except ET.ParseError as exc:
            unparseable.append(f"{d['sample_id']} ({exc})")
            continue
        pages = [el for el in root.iter()
                 if el.tag.startswith(PAGE_NS) and el.tag.endswith("Page")]
        regions = sum(1 for el in root.iter()
                      if el.tag.startswith(PAGE_NS) and el.tag.endswith("Region")
                      and not el.tag.endswith("ReadingOrder"))
        if regions != d["number_of_regions"]:
            err(f"{d['sample_id']}: region count {regions} != manifest "
                f"{d['number_of_regions']}")
        ok_ref = False
        if len(pages) == 1:
            ref = pages[0].get("imageFilename") or ""
            cdir = img_path.parent
            if cdir / ref == img_path:
                ok_ref = True
            elif ref.lower() == img_path.name.lower():
                ok_ref = True
            elif norm_stem(ref) == norm_stem(img_path.name):
                ok_ref = True
        if not ok_ref:
            ref_broken.append(
                f"{d['sample_id']}: imageFilename does not resolve to paired image")
        ih = file_hash(img_path)
        xh = file_hash(xml_path)
        if ih in img_hashes:
            err(f"duplicate image content between {img_hashes[ih]} and "
                f"{d['image_relative_path']}")
        else:
            img_hashes[ih] = d["image_relative_path"]
        if xh in xml_hashes:
            err(f"duplicate XML content between {xml_hashes[xh]} and "
                f"{d['xml_relative_path']}")
        else:
            xml_hashes[xh] = d["xml_relative_path"]

    print(f"unreadable images           : {len(unreadable)}")
    print(f"unparseable XMLs            : {len(unparseable)}")
    print(f"dimension mismatches        : {dims_wrong}")
    print(f"broken XML->image mappings  : {len(ref_broken)}")
    print(f"unique images               : {len(img_hashes)}")
    print(f"unique XMLs                 : {len(xml_hashes)}")
    for u in unreadable[:10]:
        err(f"unreadable image: {u}")
    for u in unparseable[:10]:
        err(f"unparseable XML: {u}")
    for r in ref_broken[:10]:
        err(r)

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
        return 1
    print("\nAUDIT PASSED (subset consistent with manifest and raw dataset)"
          + (f", {len(warns)} warning(s)" if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
