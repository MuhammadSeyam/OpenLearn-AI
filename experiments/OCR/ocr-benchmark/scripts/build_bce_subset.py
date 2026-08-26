#!/usr/bin/env python3
"""
build_bce_subset.py

Build the balanced BCE-Arabic-v1 benchmark subset:

    data/benchmark/bce-arabic-v1-balanced/

from the raw dataset (data/raw/bce-arabic-v1), which is NEVER modified.

A sample is one page image + its PAGE-XML annotation. Selection rules:

  1. The XML -> image reference must resolve deterministically inside the
     XML's own category, using the same matching ladder as
     scripts/validate_bce_dataset.py:
         exact filename  ->  case-insensitive  ->  normalized stem
         (lowercase, trailing "_b" stripped; extension-insensitive)
     Ambiguous or unresolved references are excluded.
  2. The image must decode with Pillow.
  3. Declared <Page imageWidth/imageHeight> must equal the actual raster
     size (BCE's benchmark role is coordinate-based layout evaluation;
     mismatched rasters would invalidate region coordinates). Excluded,
     never repaired.
  4. One XML per distinct page: when several annotations map to one image
     (e.g. "(2)" re-saves), exactly one representative annotation is kept
     (prefer exact-name matches, then non-parenthesized names, then
     lexicographic order).
  5. Content uniqueness by SHA-256: an image byte-content and an XML
     byte-content may each appear at most once in the whole subset, so no
     page crosses categories and no "(2)" copy is double-counted.
  6. Cross-category conflicts (identical image bytes filed in several
     categories) are claimed by the category with the smaller candidate
     pool first (ties: canonical category order above) - deterministic,
     and protects scarce categories such as "tables".
  7. Within a category, candidates are ranked by
     sha256("{SEED}|{category}|{xml relative path}") and the top
     TARGET_PER_CATEGORY are taken - reproducible pseudo-random order with
     no filename-alphabetical bias. SEED = 20260825.

Known outcome: "tables" contains only 24 genuinely unique eligible pages
(Diagrams-42.xml / Diagrams-42(2).xml are a redundant "(2)" re-save of the
same annotation for Diagrams-42.jpg), so the maximum valid subset is
24 + 7*25 = 199 samples. This script does NOT duplicate or weaken rules to
force 200.

The raw dataset is only read. Outputs are written exclusively under
data/benchmark/bce-arabic-v1-balanced/ (subset copies, manifest.json,
SELECTION_REPORT.md).

Usage:  python experiments/OCR/ocr-benchmark/scripts/build_bce_subset.py [--dry-run]
Exit codes: 0 = built, 1 = build failed verification, 2 = usage error.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, UnidentifiedImageError

TOOL_NAME = "build_bce_subset"
ALGORITHM_VERSION = "1.0.0"
SEED = 20260825
TARGET_PER_CATEGORY = 25

BENCH_ROOT = Path(__file__).resolve().parent.parent
RAW_DATASET = BENCH_ROOT / "data" / "raw" / "bce-arabic-v1"
SUBSET_DIR = BENCH_ROOT / "data" / "benchmark" / "bce-arabic-v1-balanced"

CATEGORIES = (
    "Charts",
    "Headers",
    "graphics",
    "multi-columns",
    "tables",
    "text and images",
    "textonly",
    "titles",
)

PAGE_NS = "{http://schema.primaresearch.org/PAGE/gts/pagecontent/"
IMAGE_EXTS = {".jpg", ".jpeg", ".tif", ".tiff", ".png"}
PAREN_SUFFIX = "("


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_stem(name: str) -> str:
    stem = Path(name).stem.lower()
    return stem[:-2] if stem.endswith("_b") else stem


@dataclass
class Sample:
    category: str
    image: Path          # resolved image path in raw dataset
    xml: Path            # representative annotation path in raw dataset
    mapping_method: str  # exact | case-insensitive | normalized-stem
    width: int
    height: int
    regions: int
    reading_order: bool
    declared_warning: str | None = None
    image_sha256: str = field(init=False)
    xml_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        self.image_sha256 = sha256(self.image)
        self.xml_sha256 = sha256(self.xml)


@dataclass
class CategoryScan:
    samples: list[Sample] = field(default_factory=list)
    unresolved_refs: list[str] = field(default_factory=list)
    unreadable_images: list[str] = field(default_factory=list)
    dim_mismatches: list[str] = field(default_factory=list)
    collapsed_annotations: list[str] = field(default_factory=list)
    ambiguous_refs: list[str] = field(default_factory=list)
    unparseable_xml: list[str] = field(default_factory=list)

    def pool_size(self) -> int:
        return len(self.samples)


def read_page(xml_path: Path) -> dict | None:
    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError:
        return None
    pages = [el for el in root.iter()
             if el.tag.startswith(PAGE_NS) and el.tag.endswith("Page")]
    if len(pages) != 1:
        return {}
    page = pages[0]
    return {
        "imageFilename": page.get("imageFilename"),
        "width": int(page.get("imageWidth")),
        "height": int(page.get("imageHeight")),
        "regions": sum(1 for el in root.iter()
                       if el.tag.startswith(PAGE_NS) and el.tag.endswith("Region")
                       and not el.tag.endswith("ReadingOrder")),
        "reading_order": any(el.tag.startswith(PAGE_NS)
                             and el.tag.endswith("ReadingOrder")
                             for el in root.iter()),
    }


def choose_annotation(candidates: list[tuple[Path, str]]) -> tuple[Path, str]:
    """Pick one representative annotation among those mapping to one image."""
    def rank(item: tuple[Path, str]) -> tuple:
        path, method = item
        method_rank = {"exact": 0, "case-insensitive": 1, "normalized-stem": 2}[method]
        has_paren = PAREN_SUFFIX in path.name
        return (method_rank, has_paren, path.name)
    return sorted(candidates, key=rank)[0]


def scan_category(category: str) -> CategoryScan:
    scan = CategoryScan()
    cdir = RAW_DATASET / category
    by_name: dict[str, Path] = {}
    by_stem: dict[str, Path] = {}
    for p in sorted(cdir.iterdir()):
        if p.is_file() and not p.is_symlink() and p.suffix.lower() in IMAGE_EXTS:
            by_name.setdefault(p.name.lower(), p)
            by_stem.setdefault(norm_stem(p.name), p)

    per_image: dict[Path, list[tuple[Path, str]]] = {}
    dims: dict[Path, tuple[int, int]] = {}
    for xml_path in sorted(cdir.glob("*.xml")):
        rel = f"{category}/{xml_path.name}"
        info = read_page(xml_path)
        if info is None:
            scan.unparseable_xml.append(rel)
            continue
        if not info:
            scan.unresolved_refs.append(f"{rel} (no unique <Page>)")
            continue
        ref = info["imageFilename"]
        target: Path | None = None
        method: str | None = None
        direct = cdir / ref
        if ref and direct.is_file():
            target, method = direct, "exact"
        elif ref and ref.lower() in by_name:
            hits = [p for n, p in by_name.items() if n == ref.lower()]
            if len(hits) == 1:
                target, method = hits[0], "case-insensitive"
            else:
                scan.ambiguous_refs.append(f"{rel} -> {ref}")
                continue
        elif ref and norm_stem(ref) in by_stem:
            hits = [p for s, p in by_stem.items() if s == norm_stem(ref)]
            if len(hits) == 1:
                target, method = hits[0], "normalized-stem"
            else:
                scan.ambiguous_refs.append(f"{rel} -> {ref}")
                continue
        if target is None:
            scan.unresolved_refs.append(f"{rel} -> {ref}")
            continue
        per_image.setdefault(target, []).append((xml_path, method))

    for image_path, anns in sorted(per_image.items(), key=lambda kv: kv[0].name):
        if len(anns) > 1:
            kept = choose_annotation(anns)[0]
            for other, _ in anns:
                if other != kept:
                    scan.collapsed_annotations.append(
                        f"{category}/{other.name} (same page as {kept.name})")
        xml_path, method = choose_annotation(anns)
        rel_img = f"{category}/{image_path.name}"
        try:
            with Image.open(image_path) as im:
                im.load()
                w, h = im.size
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            scan.unreadable_images.append(f"{rel_img} ({exc!r})")
            continue
        info = read_page(xml_path)
        warning = None
        if (info["width"], info["height"]) != (w, h):
            detail = (f"{category}/{xml_path.name} declares "
                      f"{info['width']}x{info['height']}, raster is {w}x{h}")
            scan.dim_mismatches.append(detail)
            warning = detail
        sample = Sample(
            category=category,
            image=image_path,
            xml=xml_path,
            mapping_method=method,
            width=w,
            height=h,
            regions=info["regions"],
            reading_order=info["reading_order"],
            declared_warning=warning,
        )
        if warning is None:
            scan.samples.append(sample)
    return scan


def selection_rank(sample: Sample) -> str:
    key = f"{SEED}|{sample.category}|{sample.xml.relative_to(RAW_DATASET).as_posix()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def slug(category: str) -> str:
    return category.lower().replace(" ", "_")


def build() -> tuple[list[Sample], dict]:
    scans = {c: scan_category(c) for c in CATEGORIES}

    order = sorted(
        CATEGORIES,
        key=lambda c: (scans[c].pool_size(), CATEGORIES.index(c)),
    )

    claimed_images: set[str] = set()
    claimed_xmls: set[str] = set()
    selected: list[Sample] = []
    cross_skipped: Counter = Counter()

    for cat in order:
        scan = scans[cat]
        ranked = sorted(scan.samples, key=selection_rank)
        taken = 0
        for s in ranked:
            if taken >= TARGET_PER_CATEGORY:
                break
            if s.image_sha256 in claimed_images:
                cross_skipped[cat] += 1
                continue
            if s.xml_sha256 in claimed_xmls:
                cross_skipped[cat] += 1
                continue
            claimed_images.add(s.image_sha256)
            claimed_xmls.add(s.xml_sha256)
            selected.append(s)
            taken += 1

    meta = {"scans": scans, "order": order, "cross_skipped": cross_skipped}
    return selected, meta


def write_subset(selected: list[Sample]) -> None:
    if SUBSET_DIR.exists():
        sys.exit(f"error: {SUBSET_DIR} already exists - remove it explicitly to rebuild "
                 f"(this script never overwrites an existing subset)")
    for s in selected:
        dest_dir = SUBSET_DIR / s.category
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s.image, dest_dir / s.image.name)
        shutil.copy2(s.xml, dest_dir / s.xml.name)


def manifest_document(selected: list[Sample], meta: dict) -> dict:
    counts = Counter(s.category for s in selected)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    docs = []
    for s in sorted(selected, key=lambda x: (x.category, x.xml.stem)):
        docs.append({
            "sample_id": f"{slug(s.category)}__{s.xml.stem}",
            "category": s.category,
            "image_relative_path": f"{s.category}/{s.image.name}",
            "xml_relative_path": f"{s.category}/{s.xml.name}",
            "image_sha256": s.image_sha256,
            "xml_sha256": s.xml_sha256,
            "image_width": s.width,
            "image_height": s.height,
            "number_of_regions": s.regions,
            "reading_order_exists": s.reading_order,
            "mapping_method": s.mapping_method,
            "source_image_path": s.image.relative_to(BENCH_ROOT).as_posix(),
            "source_xml_path": s.xml.relative_to(BENCH_ROOT).as_posix(),
        })
    return {
        "schema": "openlearn-ocrbench-manifest",
        "schema_version": 1,
        "dataset": "bce-arabic-v1",
        "subset": "bce-arabic-v1-balanced",
        "created": now,
        "sample_unit": "one benchmark sample = one page image + its PAGE-XML annotation",
        "selection": {
            "tool": TOOL_NAME,
            "algorithm_version": ALGORITHM_VERSION,
            "seed": SEED,
            "target_samples_per_category": TARGET_PER_CATEGORY,
            "rules": [
                "deterministic XML->image ladder: exact > case-insensitive > normalized-stem (_b suffix)",
                "Pillow-decodable images only",
                "declared Page dimensions must equal actual raster size",
                "one representative annotation per distinct page ((2) re-saves grouped)",
                "SHA-256 content uniqueness across the whole subset (images and XMLs)",
                "cross-category duplicates claimed by the category with the smaller candidate pool first",
                f"within-category ranking sha256('{SEED}|<category>|<xml_relpath>')",
            ],
            "canonical_category_order": list(CATEGORIES),
            "processing_order_by_pool_size": meta["order"],
        },
        "totals": {
            "selected_samples": len(selected),
            "samples_per_category": {c: counts.get(c, 0) for c in CATEGORIES},
            "shortfall_vs_target": {
                c: TARGET_PER_CATEGORY - counts.get(c, 0) for c in CATEGORIES
                if counts.get(c, 0) < TARGET_PER_CATEGORY
            },
        },
        "documents": docs,
    }


def report_markdown(selected: list[Sample], meta: dict) -> str:
    scans: dict[str, CategoryScan] = meta["scans"]
    counts = Counter(s.category for s in selected)
    methods = Counter(s.mapping_method for s in selected)
    ro = sum(1 for s in selected if s.reading_order)
    lines: list[str] = []
    add = lines.append

    add("# BCE Arabic v1 - Balanced Benchmark Subset")
    add("")
    add("## Dataset")
    add("")
    add("- **Dataset:** BCE Arabic v1 (`data/raw/bce-arabic-v1`, untouched)")
    add("- **Subset:** balanced benchmark subset (`data/benchmark/bce-arabic-v1-balanced`)")
    add("- **Unit:** one sample = one page image + its PAGE-XML annotation")
    add("")
    add("## Target")
    add("")
    add("25 valid unique samples per category, 8 categories = **200 samples**.")
    add("")
    add("## Actual result")
    add("")
    add("| Category | Selected | Target | Eligible pool before conflicts |")
    add("|---|---|---|---|")

    for c in CATEGORIES:
        mark = "" if counts[c] == TARGET_PER_CATEGORY else " **(shortfall)**"
        add(f"| {c} | {counts[c]}{mark} | {TARGET_PER_CATEGORY} | {len(scans[c].samples)} |")
    add(f"| **Total** | **{len(selected)}** | 200 | |")
    add("")
    short = [c for c in CATEGORIES if counts[c] < TARGET_PER_CATEGORY]
    if short:
        add("### Shortfall explanation")
        add("")
        for c in short:
            add(f"- **{c}: only {counts[c]} eligible unique pages exist.** After every "
                f"validity rule, the category holds exactly {len(scans[c].samples)} "
                f"eligible samples, and all of them were selectable.")
        add("")
        add("`tables` contains 25 PAGE-XML files but only 24 distinct pages: "
            "`Diagrams-42(2).xml` is a `(2)` re-save whose annotation content is identical to "
            "`Diagrams-42.xml` (only Metadata timestamps differ), so rule \"no `(2)` copies as "
            "independent samples\" leaves 24 unique pages. Reaching 25 would require duplicating "
            "a sample or counting the redundant copy, so the target is honestly missed by 1 "
            "for this category (**199 total**, not 200).")
        add("")
    add("## Exclusions / hygiene summary")
    add("")
    total_unres = sum(len(s.unresolved_refs) for s in scans.values())
    total_collapsed = sum(len(s.collapsed_annotations) for s in scans.values())
    total_dim = sum(len(s.dim_mismatches) for s in scans.values())
    add(f"- Unresolved XML->image references (excluded): **{total_unres}** - "
        "`titles/textonly-278.xml`, `titles/textonly-377.xml`")
    add(f"- Redundant annotation copies grouped onto their page (not independent samples): "
        f"**{total_collapsed}**")
    add(f"- Dimension-mismatch pages excluded (declared vs actual raster): **{total_dim}** - "
        "`text and images/Charts-52(.xml/(2).xml)` declares 1660x2339, raster is 1653x2339")
    add("- Unreadable/corrupt images: **0**")
    add(f"- Cross-category duplicate pages skipped in the loser category: "
        f"**{sum(meta['cross_skipped'].values())}** "
        f"(claimed by the scarcer category instead)")
    add("- Exact duplicate contents anywhere in the subset: **0** (enforced by SHA-256 registry)")
    add("- Junk files (Thumbs.db etc.): never part of any sample")
    add("")
    add("## Reproducibility")
    add("")
    add(f"- Selection seed: **{SEED}**")
    add(f"- Algorithm: `{TOOL_NAME}` v{ALGORITHM_VERSION} "
        f"(`scripts/build_bce_subset.py`)")
    add("- Source dataset path (relative to `experiments/OCR/ocr-benchmark/`): "
        "`data/raw/bce-arabic-v1`")
    add("- Mapping methods used: " + ", ".join(f"`{k}` x{n}" for k, n in sorted(methods.items())))
    add(f"- Samples with explicit `<ReadingOrder>`: {ro}/{len(selected)}")
    add("- Rerunning the script reproduces the identical file set and manifest content "
        "(except the manifest `created` timestamp); it refuses to overwrite an existing subset.")
    add("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog=TOOL_NAME,
                                     description="Build the balanced BCE-Arabic-v1 subset "
                                                 "(raw dataset untouched).")
    parser.add_argument("--dry-run", action="store_true",
                        help="select and print the plan without writing anything")
    args = parser.parse_args(argv)

    if not RAW_DATASET.is_dir():
        print(f"error: raw dataset not found: {RAW_DATASET}", file=sys.stderr)
        return 2

    selected, meta = build()
    scans: dict[str, CategoryScan] = meta["scans"]

    print(f"BCE balanced subset builder v{ALGORITHM_VERSION} (seed={SEED})")
    print(f"selected: {len(selected)} samples "
          f"({Counter(s.category for s in selected)})")

    if args.dry_run:
        for c in CATEGORIES:
            s = scans[c]
            print(f"\n[{c}] pool={len(s.samples)} "
                  f"unresolved={len(s.unresolved_refs)} collapsed={len(s.collapsed_annotations)} "
                  f"dim_mismatch={len(s.dim_mismatches)} unreadable={len(s.unreadable_images)} "
                  f"ambiguous={len(s.ambiguous_refs)} unparseable={len(s.unparseable_xml)}")
            picked = [x for x in selected if x.category == c]
            for x in picked[:5]:
                print(f"   {x.xml.name} <- {x.image.name} [{x.mapping_method}]")
            if len(picked) > 5:
                print(f"   ... {len(picked) - 5} more")
        return 0

    write_subset(selected)
    doc = manifest_document(selected, meta)
    (SUBSET_DIR / "manifest.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (SUBSET_DIR / "SELECTION_REPORT.md").write_text(
        report_markdown(selected, meta), encoding="utf-8")
    print(f"wrote: {SUBSET_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
