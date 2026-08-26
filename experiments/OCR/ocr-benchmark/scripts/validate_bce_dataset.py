#!/usr/bin/env python3
"""
validate_bce_dataset.py

Read-only structural/integrity validation of the BCE-Arabic-v1 OCR
benchmark dataset (data/raw/bce-arabic-v1).

Authority: experiments/OCR/OCR_BENCHMARKING_HANDBOOK.md (v1.x), which fixes:
  - unit        : 1 PAGE-XML file = 1 page, across exactly 8 categories
                  (Charts, Headers, graphics, multi-columns, tables,
                   "text and images", textonly, titles)
  - role        : layout/region/reading-order evaluation ONLY
                  (no transcription GT exists; CER/WER is forbidden)
  - known defect: XML files whose referenced page image cannot be matched on
                  disk (historical .tif -> .jpg conversion gap) "must be
                  resolved before any image-based BCE evaluation run"
                  (handbook section 3.2 / 8.3) -> hard failure here.

What this validator answers:
    "Is this dataset structurally and technically safe to enter the OCR
     benchmark pipeline?"

Checks (severity):
  ERROR   unreadable/corrupt image; unparseable XML; XML page image that no
          matching strategy resolves; zero-byte files; missing expected
          category directory; empty category directory.
  WARNING OS junk files (Thumbs.db etc.); unexpected extensions; unexpected
          top-level entries; symlinks; image refs resolvable only after
          normalization (.tif->.jpg rename / "_b" suffix); declared vs actual
          page dimension mismatch; exact duplicate files; cross-category
          duplicates; suspiciously tiny images.
  INFO    case-only ref mismatches, duplicate basenames with differing
          content, non-RGB pixel modes, dataset statistics.

The dataset itself is never modified, and nothing is written inside it.
With --output, a report copy is written to the given path only.

Exit codes: 0 = PASS (or PASS WITH WARNINGS), 1 = FAIL, 2 = usage/config error.

Usage:
    python experiments/OCR/ocr-benchmark/scripts/validate_bce_dataset.py \
        [DATASET_PATH] [--strict] [--json] [--output FILE] [--verbose]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

try:
    from PIL import Image, UnidentifiedImageError
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

TOOL_NAME = "validate_bce_dataset"
TOOL_VERSION = "1.0.0"

DEFAULT_DATASET = Path(__file__).resolve().parent.parent / "data" / "raw" / "bce-arabic-v1"

EXPECTED_CATEGORIES = (
    "Charts",
    "Headers",
    "graphics",
    "multi-columns",
    "tables",
    "text and images",
    "textonly",
    "titles",
)

XML_EXTS = {".xml"}
IMAGE_EXTS = {".jpg", ".jpeg", ".tif", ".tiff", ".png"}
ALLOWED_EXTS = XML_EXTS | IMAGE_EXTS
JUNK_BASENAMES = {"thumbs.db", ".ds_store", "desktop.ini"}
PAGE_NS_PREFIX = "{http://schema.primaresearch.org/PAGE/gts/pagecontent/"

ERROR, WARNING, INFO = "ERROR", "WARNING", "INFO"
DISPLAY_LIMIT = 20


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    items: list[str] = field(default_factory=list)

    def render(self, limit: int) -> list[str]:
        lines = [f"[{self.severity}] {self.code}: {self.message} ({len(self.items)})"]
        for item in self.items[:limit]:
            lines.append(f"    - {item}")
        if len(self.items) > limit:
            lines.append(f"    ... and {len(self.items) - limit} more (--verbose to show all)")
        return lines


@dataclass
class Report:
    dataset: Path
    findings: list[Finding] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def add(self, severity: str, code: str, message: str, items: list[str] | None = None) -> None:
        items = items or []
        for existing in self.findings:
            if existing.code == code:
                existing.items.extend(items)
                return
        self.findings.append(Finding(severity, code, message, list(items)))

    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == ERROR]

    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == WARNING]

    def status(self, strict: bool) -> str:
        if self.errors():
            return "FAIL"
        if strict and self.warnings():
            return "FAIL"
        if self.warnings() or any(f.severity == WARNING for f in self.findings):
            return "PASS WITH WARNINGS"
        return "PASS"


def iter_files(root: Path) -> list[Path]:
    """All regular files under root, sorted by relative path for determinism."""
    files = [
        p for p in root.rglob("*")
        if p.is_file() and not p.is_symlink()
    ]
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def check_structure(report: Report, root: Path) -> None:
    present = {p.name for p in root.iterdir() if p.is_dir()}
    for category in EXPECTED_CATEGORIES:
        if category not in present:
            report.add(ERROR, "MISSING_CATEGORY",
                       "expected category directory missing", [category])
    extras = sorted(present - set(EXPECTED_CATEGORIES))
    if extras:
        report.add(WARNING, "UNEXPECTED_DIR",
                   "unexpected directories at dataset root", extras)
    strays = sorted(p.name for p in root.iterdir() if p.is_file())
    if strays:
        report.add(WARNING, "STRAY_ROOT_FILE",
                   "files at dataset root (expected only category directories)", strays)
    symlinks = sorted(
        p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_symlink()
    )
    if symlinks:
        report.add(WARNING, "SYMLINK",
                   "symlinked entries found (dataset should contain regular files only)",
                   symlinks)


def normalize_ref(ref: str) -> tuple[str, str]:
    """(case-folded name, normalized stem) used by the matching ladder."""
    low = ref.strip().lower()
    stem = Path(low).stem
    if stem.endswith("_b"):
        stem = stem[:-2]
    return low, stem


def build_image_index(category_dir: Path) -> tuple[dict[str, Path], dict[str, Path]]:
    by_name: dict[str, Path] = {}
    by_stem: dict[str, Path] = {}
    for p in sorted(category_dir.iterdir()):
        if not p.is_file() or p.is_symlink():
            continue
        if p.suffix.lower() not in IMAGE_EXTS:
            continue
        by_name.setdefault(p.name.lower(), p)
        stem = p.stem.lower()
        if stem.endswith("_b"):
            stem = stem[:-2]
        by_stem.setdefault(stem, p)
    return by_name, by_stem


def parse_page_attrs(xml_path: Path) -> dict | None:
    """Extract first Page element attributes from a PAGE-XML file."""
    import xml.etree.ElementTree as ET

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return None
    pages = [el for el in tree.getroot().iter() if el.tag.startswith(PAGE_NS_PREFIX)
             and el.tag.endswith("Page")]
    if not pages:
        return {}
    page = pages[0]
    regions = sum(
        1 for el in tree.getroot().iter()
        if el.tag.startswith(PAGE_NS_PREFIX) and el.tag.endswith("Region")
    )
    has_reading_order = any(
        el.tag.startswith(PAGE_NS_PREFIX) and el.tag.endswith("ReadingOrder")
        for el in tree.getroot().iter()
    )
    return {
        "imageFilename": page.get("imageFilename"),
        "width": page.get("imageWidth"),
        "height": page.get("imageHeight"),
        "regions": regions,
        "reading_order": has_reading_order,
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(report: Report, root: Path, pil_available: bool) -> Report:
    check_structure(report, root)

    category_dirs = {
        p.name: p for p in sorted(root.iterdir())
        if p.is_dir() and not p.is_symlink()
    }
    all_files = iter_files(root)

    zero_byte = [p.relative_to(root).as_posix() for p in all_files if p.stat().st_size == 0]
    if zero_byte:
        report.add(ERROR, "ZERO_BYTE", "zero-byte files", zero_byte)

    junk = [
        p.relative_to(root).as_posix() for p in all_files
        if p.name.lower() in JUNK_BASENAMES
    ]
    if junk:
        report.add(WARNING, "JUNK_FILE",
                   "OS-generated junk files (not dataset content)", junk)

    hidden = [
        p.relative_to(root).as_posix() for p in all_files if p.name.startswith(".")
    ]
    if hidden:
        report.add(WARNING, "HIDDEN_FILE", "hidden files", hidden)

    bad_ext = [
        p.relative_to(root).as_posix() for p in all_files
        if p.suffix.lower() not in ALLOWED_EXTS and p.name.lower() not in JUNK_BASENAMES
    ]
    if bad_ext:
        report.add(WARNING, "UNEXPECTED_EXT",
                   f"extensions outside {sorted(ALLOWED_EXTS)}", bad_ext)

    ext_counts = Counter(p.suffix.lower() or "<none>" for p in all_files)

    xml_by_category: dict[str, list[Path]] = {}
    images_by_category: dict[str, list[Path]] = {}
    for name, cdir in category_dirs.items():
        cat_files = [p for p in cdir.iterdir() if p.is_file() and not p.is_symlink()]
        xml_by_category[name] = sorted(p for p in cat_files if p.suffix.lower() in XML_EXTS)
        images_by_category[name] = sorted(
            p for p in cat_files if p.suffix.lower() in IMAGE_EXTS
        )

    empty_cats = sorted(n for n, x in xml_by_category.items() if len(x) + len(images_by_category[n]) == 0)
    if empty_cats:
        report.add(ERROR, "EMPTY_CATEGORY", "category directories without any files", empty_cats)

    ref_exact = ref_case = ref_renamed = 0
    unresolved: list[str] = []
    renamed_refs: list[str] = []
    case_refs: list[str] = []
    missing_attrs: list[str] = []
    unparseable: list[str] = []

    dim_mismatch: list[str] = []
    dims_actual: Counter = Counter()
    modes: Counter = Counter()
    tiny_images: list[str] = []
    unreadable: list[tuple[str, str]] = []
    size_totals: list[int] = []
    actual_dims_by_path: dict[Path, tuple[int, int]] = {}
    total_regions = 0
    reading_order_count = 0

    if pil_available:
        for cat_name, images in images_by_category.items():
            for img_path in images:
                try:
                    with Image.open(img_path) as im:
                        im.load()
                        w, h = im.size
                except (UnidentifiedImageError, OSError, ValueError) as exc:
                    unreadable.append((img_path.relative_to(root).as_posix(), repr(exc)))
                    continue
                modes[im.mode] += 1
                dims_actual[(w, h)] += 1
                size_totals.append(img_path.stat().st_size)
                actual_dims_by_path[img_path.resolve()] = (w, h)
                if min(w, h) < 100:
                    tiny_images.append(f"{img_path.relative_to(root).as_posix()} ({w}x{h})")

    for cat_name, xmls in xml_by_category.items():
        by_name, by_stem = build_image_index(category_dirs[cat_name])
        for xml_path in xmls:
            rel = xml_path.relative_to(root).as_posix()
            attrs = parse_page_attrs(xml_path)
            if attrs is None:
                unparseable.append(rel)
                continue
            if attrs == {}:
                missing_attrs.append(f"{rel} (no <Page> element)")
                continue
            total_regions += attrs["regions"]
            reading_order_count += int(attrs["reading_order"])
            ref = attrs["imageFilename"]
            if not ref or not attrs["width"] or not attrs["height"]:
                missing_attrs.append(f"{rel} (missing imageFilename/imageWidth/imageHeight)")
                continue

            low, norm_stem = normalize_ref(ref)
            target: Path | None = None
            direct = xml_path.with_name(ref)
            if direct.is_file():
                target = direct
                ref_exact += 1
            elif low in by_name:
                target = by_name[low]
                ref_case += 1
                case_refs.append(f"{rel} -> {ref} (actual: {target.name})")
            elif norm_stem in by_stem:
                target = by_stem[norm_stem]
                ref_renamed += 1
                renamed_refs.append(f"{rel} -> {ref} (resolved: {target.name})")
            if target is None:
                unresolved.append(f"{rel} -> {ref}")
                continue

            actual = actual_dims_by_path.get(target.resolve())
            if actual is not None and actual != (int(attrs["width"]), int(attrs["height"])):
                dim_mismatch.append(
                    f"{rel} declares {attrs['width']}x{attrs['height']}, "
                    f"{target.relative_to(root).as_posix()} is {actual[0]}x{actual[1]}"
                )

    if unparseable:
        report.add(ERROR, "XML_UNPARSEABLE", "XML files that fail to parse", unparseable)
    if missing_attrs:
        report.add(WARNING, "XML_MISSING_PAGE_ATTRS",
                   "XML files without a usable <Page imageFilename/imageWidth/imageHeight>",
                   missing_attrs)
    if unreadable:
        report.add(
            ERROR, "IMAGE_UNREADABLE",
            "images that Pillow cannot open/decode",
            [f"{path} ({err})" for path, err in unreadable],
        )
    if unresolved:
        report.add(
            ERROR, "IMAGE_REF_UNRESOLVED",
            "XML page-image references that no matching strategy resolves "
            "(handbook 3.2/8.3: must be resolved before image-based evaluation)",
            unresolved,
        )
    if renamed_refs:
        report.add(
            WARNING, "REF_RESOLVED_VIA_RENAME",
            "refs resolved only after normalization (.tif/.jpg rename or '_b' suffix) "
            "- documented conversion gap, count should trend to zero",
            renamed_refs,
        )
    if case_refs:
        report.add(INFO, "REF_CASE_MISMATCH",
                   "refs differing from disk filename only by letter case", case_refs)
    if dim_mismatch:
        report.add(
            WARNING, "DIM_MISMATCH",
            "declared <Page> dimensions differ from actual raster "
            "(coordinate scoring may be affected)",
            dim_mismatch,
        )
    if tiny_images:
        report.add(WARNING, "TINY_IMAGE", "images smaller than 100px on a side", tiny_images)

    hashes: dict[str, list[Path]] = {}
    for p in all_files:
        if p.stat().st_size == 0:
            continue
        hashes.setdefault(sha256(p), []).append(p)
    dup_groups = {h: paths for h, paths in hashes.items() if len(paths) > 1}
    dup_files = sorted(
        p.relative_to(root).as_posix()
        for paths in dup_groups.values() for p in paths
    )
    cross_groups = [
        paths for paths in dup_groups.values()
        if len({p.parent.name for p in paths}) > 1
    ]
    cross_files = sorted(
        p.relative_to(root).as_posix()
        for paths in cross_groups for p in paths
    )
    if dup_groups:
        report.add(
            WARNING, "EXACT_DUPLICATE",
            "exact SHA-256 duplicate groups (inflates per-category sample counts)",
            [f"{h[:12]}: " + ", ".join(p.relative_to(root).as_posix() for p in paths)
             for h, paths in sorted(dup_groups.items())],
        )
    if cross_groups:
        report.add(
            WARNING, "CROSS_CATEGORY_DUPLICATE",
            "duplicate groups spanning multiple categories (same page in several samples)",
            [", ".join(sorted(p.relative_to(root).as_posix() for p in paths))
             for paths in sorted(cross_groups, key=lambda ps: sorted(x.name for x in ps))],
        )

    basename_index: dict[str, set[str]] = {}
    content_differs: list[str] = []
    for p in all_files:
        basename_index.setdefault(p.name.lower(), set()).add(str(p.parent))
    multi_loc = {n: locs for n, locs in basename_index.items() if len(locs) > 1}
    for name in sorted(multi_loc):
        holders = [p for p in all_files if p.name.lower() == name]
        digests = {sha256(p) for p in holders}
        if len(digests) > 1:
            content_differs.append(name)

    if not pil_available:
        report.add(WARNING, "NO_PILLOW",
                   "Pillow unavailable - image decode/dimension checks skipped")

    aspect_ratios = Counter(round(w / h, 3) for (w, h) in dims_actual.elements())

    report.stats = {
        "total_files": len(all_files),
        "total_bytes": sum(p.stat().st_size for p in all_files),
        "categories": {
            name: {
                "xml": len(xml_by_category.get(name, [])),
                "images": len(images_by_category.get(name, [])),
            }
            for name in sorted(set(category_dirs) | set(EXPECTED_CATEGORIES))
        },
        "extension_counts": dict(sorted(ext_counts.items())),
        "xml_total": sum(len(v) for v in xml_by_category.values()),
        "image_total": sum(len(v) for v in images_by_category.values()),
        "page_image_refs": {
            "exact": ref_exact,
            "case_insensitive": ref_case,
            "renamed_normalized": ref_renamed,
            "unresolved": len(unresolved),
        },
        "regions_total": total_regions,
        "xml_with_reading_order": reading_order_count,
        "dimensions_actual": {f"{w}x{h}": n for (w, h), n in sorted(dims_actual.items())},
        "aspect_ratios": {str(r): n for r, n in sorted(aspect_ratios.items())},
        "pixel_modes": dict(sorted(modes.items())),
        "duplicate_groups": len(dup_groups),
        "duplicate_files": len(dup_files),
        "cross_category_duplicate_groups": len(cross_groups),
        "cross_category_duplicate_files": len(cross_files),
        "duplicate_basenames_differing_content": sorted(content_differs),
        "image_bytes": sum(size_totals),
        "image_bytes_min": min(size_totals) if size_totals else None,
        "image_bytes_max": max(size_totals) if size_totals else None,
        "image_bytes_mean": round(sum(size_totals) / len(size_totals)) if size_totals else None,
    }

    return report


def render_text(report: Report, verbose: bool, strict: bool = False) -> str:
    limit = 10**9 if verbose else DISPLAY_LIMIT
    s = report.stats
    lines: list[str] = []
    add = lines.append

    add("")
    add("=" * 72)
    add(f"BCE Arabic v1 dataset validation  ({TOOL_NAME} v{TOOL_VERSION}, read-only)")
    add("=" * 72)
    add(f"Dataset : {report.dataset}")
    add("")

    add("-- Summary --")
    add(f"Files                    : {s['total_files']} ({s['total_bytes'] / 1e6:.1f} MB)")
    add(f"PAGE-XML pages           : {s['xml_total']}")
    add(f"Image files              : {s['image_total']}")
    add(f"Categories               : {len(s['categories'])}")
    err_n = len(report.errors())
    warn_n = len(report.warnings())
    add(f"Errors                   : {err_n}")
    add(f"Warnings                 : {warn_n}")
    add("")

    add("-- Page-image reference resolution --")
    refs = s["page_image_refs"]
    add(f"exact match              : {refs['exact']}")
    add(f"case-insensitive match   : {refs['case_insensitive']}")
    add(f"rename-normalized match  : {refs['renamed_normalized']}")
    add(f"UNRESOLVED               : {refs['unresolved']}")
    add(f"regions annotated        : {s['regions_total']}")
    add(f"XML with reading order   : {s['xml_with_reading_order']}")
    add("")

    add("-- Duplicates --")
    add(f"Exact duplicate groups   : {s['duplicate_groups']} "
        f"({s['duplicate_files']} files)")
    add(f"Cross-category dup groups: {s['cross_category_duplicate_groups']} "
        f"({s['cross_category_duplicate_files']} files)")
    add("")

    add("-- Category counts (xml / images) --")
    width = max(len(n) for n in s["categories"])
    for name, counts in s["categories"].items():
        add(f"{name:<{width}} : {counts['xml']:>5} / {counts['images']:>5}")
    add("")

    add("-- File extensions --")
    for ext, n in s["extension_counts"].items():
        add(f"{ext:<8}: {n}")
    add("")

    if s["dimensions_actual"]:
        add("-- Image statistics --")
        add("Dimensions:")
        for d, n in s["dimensions_actual"].items():
            add(f"  {d:<12}: {n}")
        add("Aspect ratios (w/h):")
        for r, n in s["aspect_ratios"].items():
            add(f"  {r:<8}: {n}")
        add(f"Pixel modes       : {s['pixel_modes']}")
        bmin, bmax, bmean = s["image_bytes_min"], s["image_bytes_max"], s["image_bytes_mean"]
        add(f"Image sizes (B)   : min={bmin} mean={bmean} max={bmax}")
        add("")

    if report.findings:
        add("-- Findings --")
        for finding in sorted(report.findings, key=lambda f: (f.severity != ERROR, f.code)):
            lines.extend(finding.render(limit))
        add("")

    status = report.status(strict)
    add("-- Decision --")
    if status == "PASS":
        add("STATUS: PASS - dataset is structurally sound.")
    elif status == "PASS WITH WARNINGS":
        add("STATUS: PASS WITH WARNINGS - usable, review warnings above.")
    else:
        add("STATUS: FAIL - resolve ERROR findings above before benchmark use "
            "(dataset was NOT modified by this validator).")
    add("=" * 72)
    return "\n".join(lines)


def render_json(report: Report, strict: bool) -> str:
    payload = {
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "schema_version": "1.0",
        "dataset": str(report.dataset),
        "status": report.status(strict),
        "errors": len(report.errors()),
        "warnings": len(report.warnings()),
        "stats": report.stats,
        "findings": [
            {
                "severity": f.severity,
                "code": f.code,
                "message": f.message,
                "count": len(f.items),
                "items": sorted(f.items),
            }
            for f in sorted(report.findings, key=lambda x: (x.severity, x.code))
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="Read-only integrity validation of the BCE-Arabic-v1 dataset.",
    )
    parser.add_argument(
        "dataset",
        nargs="?",
        default=str(DEFAULT_DATASET),
        help=f"path to the dataset root (default: {DEFAULT_DATASET})",
    )
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as failures (exit 1)")
    parser.add_argument("--json", action="store_true",
                        help="emit deterministic machine-readable JSON")
    parser.add_argument("--output", type=Path, default=None,
                        help="also write the report to this file (outside the dataset)")
    parser.add_argument("--verbose", action="store_true",
                        help="list every finding item instead of a capped sample")
    args = parser.parse_args(argv)

    root = Path(args.dataset).expanduser().resolve()
    if not root.is_dir():
        print(f"error: dataset path is not a directory: {root}", file=sys.stderr)
        return 2

    report = Report(dataset=root)
    try:
        validate(report, root, pil_available=HAVE_PIL)
    except PermissionError as exc:
        print(f"error: permission denied while reading dataset: {exc}", file=sys.stderr)
        return 2

    if args.json:
        text = render_json(report, args.strict)
    else:
        text = render_text(report, args.verbose, args.strict)
    print(text)

    if args.output is not None:
        out = args.output.expanduser().resolve()
        if out.is_relative_to(root):
            print(f"error: --output must point outside the dataset (got {out})", file=sys.stderr)
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")

    status = report.status(args.strict)
    return 0 if status != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
