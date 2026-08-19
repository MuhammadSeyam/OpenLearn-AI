#!/usr/bin/env python3
"""Build the custom Phase-A benchmark dataset.

Single source of truth for sample selection. Reproduces:
  1. rendered/copied sample images under data/raw/custom/<category>/
  2. data/raw/custom/manifest.json
  3. text-layer ground truth (status: extracted_unverified) for born-digital
     PDF samples under data/ground_truth/custom/<sample_id>/

Selection evidence (language/text-layer checks via pdfinfo/pdftotext,
content verification via visual inspection on 2026-08-17) is recorded in
docs/provenance.md. Do NOT add samples without evidence.

Run from experiments/OCR/ocr-benchmark:  uv run python ../../ocr-benchmark/scripts/build_custom_dataset.py
(or: uv run python scripts/build_custom_dataset.py)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

BENCH = Path(__file__).resolve().parent.parent          # ocr-benchmark/
SRC = BENCH.parent / "Source"                            # experiments/OCR/Source
CUSTOM = BENCH / "data" / "raw" / "custom"
GT_ROOT = BENCH / "data" / "ground_truth" / "custom"
RENDER_DPI = 150

# canonical category key -> (existing directory name, difficulty default)
CATEGORIES = {
    "english_born_digital": ("1. English born-digital", "easy"),
    "arabic_born_digital": ("2. Arabic born-digital", "easy"),
    "english_scanned": ("3.English scanned", "hard"),
    "arabic_scanned": ("4. Arabic scanned", "hard"),
    "mixed_arabic_english": ("5. Arabic + English mixed", "hard"),
    "multi_column": ("6. Multi-column", "medium"),
    "tables": ("7. Tables", "medium"),
    "formulas": ("8. Formulas", "hard"),
    "figures_diagrams": ("9. Figures-diagrams", "medium"),
    "slides": ("10. Slides", "easy"),
    "dense_academic": ("11. Dense academic page", "medium"),
    "noisy_low_quality": ("12. Noisy-low-quality scan", "very_hard"),
}

# The selection table. Fields:
#   cat: category key
#   src: filename under Source/
#   page: 1-based PDF page (None for standalone images)
#   lang, features, difficulty override, evidence: short evidence string
#   gt: "text_layer" (born-digital PDF page -> extract) | "none" (pending manual)
SELECTION = [
    # 1. English born-digital (per-page text layer VERIFIED via pdftotext)
    dict(cat="english_born_digital", src="Object Oriented Programming in c++.pdf", page=20, lang=["en"], features=dict(),
         evidence="598 chars text layer on this page (verified)", gt="text_layer"),
    dict(cat="english_born_digital", src="AI_OS_Ch03.pdf", page=10, lang=["en"], features=dict(),
         evidence="307 chars text layer on this page (verified)", gt="text_layer"),
    dict(cat="english_born_digital", src="Transformers 1.pdf", page=3, lang=["en"], features=dict(),
         evidence="157 chars text layer — slide export, sparse text (verified)", gt="text_layer"),
    dict(cat="english_born_digital", src="NIPS-2012-imagenet-classification-with-deep-convolutional-neural-networks-Paper.pdf", page=6, lang=["en"],
         features=dict(multi_column=True, dense=True),
         evidence="3985 chars text layer (verified)", gt="text_layer"),
    dict(cat="english_born_digital", src="NIPS-2017-attention-is-all-you-need-Paper.pdf", page=8, lang=["en"],
         features=dict(multi_column=True, dense=True),
         evidence="3367 chars text layer (verified)", gt="text_layer"),

    # 2. Arabic born-digital — NO SOURCE MATERIAL EXISTS (gap, documented).
    #    Every Arabic file in Source/ is scanned/photographed (verified:
    #    الليالي البيضاء.pdf has no Arabic text layer on any tested page).

    # 3. English scanned (per-page text layer ~0 chars — VERIFIED scanned)
    dict(cat="english_scanned", src="CA lect1.pdf", page=3, lang=["en"], features=dict(),
         evidence="1 char text layer on this page — image-only scan (verified)", gt="none"),
    dict(cat="english_scanned", src="Data+Structre+lect1.pdf", page=5, lang=["en"], features=dict(),
         evidence="1 char text layer on this page — image-only scan (verified)", gt="none"),
    dict(cat="english_scanned", src="Vlec5.pdf", page=2, lang=["en"], features=dict(),
         evidence="no text layer on any tested page (scanned)", gt="none"),
    dict(cat="english_scanned", src="Vlec6.pdf", page=3, lang=["en"], features=dict(),
         evidence="no text layer on any tested page (scanned)", gt="none"),
    dict(cat="english_scanned", src="lec+9+CP.pdf", page=5, lang=["en"], features=dict(),
         evidence="no text layer on any tested page (scanned)", gt="none"),

    # 4. Arabic scanned
    dict(cat="arabic_scanned", src="ar.png", page=None, lang=["ar"],
         features=dict(), difficulty="very_hard",
         evidence="scanned Arabic textbook page, diacritics, RTL (visual inspection)", gt="none"),
    dict(cat="arabic_scanned", src="الليالي البيضاء.pdf", page=5, lang=["ar"], features=dict(),
         evidence="scanned Arabic novel; no text layer (verified p3-90)", gt="none"),
    dict(cat="arabic_scanned", src="الليالي البيضاء.pdf", page=15, lang=["ar"], features=dict(),
         evidence="scanned Arabic novel; no text layer", gt="none"),
    dict(cat="arabic_scanned", src="الليالي البيضاء.pdf", page=40, lang=["ar"], features=dict(dense=True),
         evidence="scanned Arabic novel; no text layer", gt="none"),
    dict(cat="arabic_scanned", src="الليالي البيضاء.pdf", page=80, lang=["ar"], features=dict(dense=True),
         evidence="scanned Arabic novel; no text layer", gt="none"),

    # 5. Mixed Arabic + English (gap: only one verified mixed source)
    dict(cat="mixed_arabic_english", src="Arabic English.jpg", page=None, lang=["ar", "en"],
         features=dict(mixed_language=True), difficulty="hard",
         evidence="handwritten mixed Arabic/English with formulas (visual inspection)", gt="none"),

    # 6. Multi-column (two-column academic pages, text layer present)
    dict(cat="multi_column", src="NIPS-2012-imagenet-classification-with-deep-convolutional-neural-networks-Paper.pdf", page=2, lang=["en"],
         features=dict(multi_column=True, dense=True),
         evidence="two-column academic paper (text layer verified)", gt="text_layer"),
    dict(cat="multi_column", src="NIPS-2017-attention-is-all-you-need-Paper.pdf", page=2, lang=["en"],
         features=dict(multi_column=True, dense=True),
         evidence="two-column academic paper (text layer verified)", gt="text_layer"),
    dict(cat="multi_column", src="Batch Normalization Accelerating Deep Network Training b.pdf", page=2, lang=["en"],
         features=dict(multi_column=True, dense=True),
         evidence="two-column academic paper (text layer verified)", gt="text_layer"),
    dict(cat="multi_column", src="Learning Long Term Dependencies with Gradient Descent is Difficult.pdf", page=4, lang=["en"],
         features=dict(multi_column=True, dense=True),
         evidence="two-column scanned paper page (no text layer)", gt="none"),

    # 7. Tables
    dict(cat="tables", src="lec1,2 statistics.pdf", page=5, lang=["en"],
         features=dict(table=True, formula=True), difficulty="hard",
         evidence="6x4 data table + statistics symbols (visual inspection); CamScanner scan, text layer is watermark only (verified)", gt="none"),
    dict(cat="tables", src="470180880_1078242510765782_4224372347391521822_n.jpg", page=None, lang=["ar"],
         features=dict(table=True), difficulty="hard",
         evidence="photographed Arabic schedule table, low contrast/skew (visual inspection)", gt="none"),
    dict(cat="tables", src="NIPS-2017-attention-is-all-you-need-Paper.pdf", page=3, lang=["en"],
         features=dict(table=True, formula=True, multi_column=True, dense=True), difficulty="hard",
         evidence="Table 1 + display equations + two-column (visual inspection); 1765 chars text layer", gt="text_layer"),

    # 8. Formulas
    dict(cat="formulas", src="Screenshot from 2026-08-17 14-40-44.png", page=None, lang=["en"],
         features=dict(formula=True), difficulty="hard",
         evidence="handwritten derivation with multiple expressions (visual inspection)", gt="none"),
    dict(cat="formulas", src="NIPS-2012-imagenet-classification-with-deep-convolutional-neural-networks-Paper.pdf", page=4, lang=["en"],
         features=dict(formula=True, multi_column=True, dense=True),
         evidence="16 math tokens in text layer (verified)", gt="text_layer"),
    dict(cat="formulas", src="Batch Normalization Accelerating Deep Network Training b.pdf", page=3, lang=["en"],
         features=dict(formula=True, multi_column=True, dense=True),
         evidence="BN paper equation page (equations 3-7 region)", gt="text_layer"),

    # 9. Figures / diagrams
    dict(cat="figures_diagrams", src="2.png", page=None, lang=["en"],
         features=dict(figure=True),
         evidence="labeled neuron diagram slide (visual inspection)", gt="none"),
    dict(cat="figures_diagrams", src="5690_create-star-schema-data-model-using-microsoft-toolset.028.png", page=None, lang=["en"],
         features=dict(figure=True),
         evidence="star-schema diagram (visual inspection)", gt="none"),
    dict(cat="figures_diagrams", src="NIPS-2017-attention-is-all-you-need-Paper.pdf", page=4, lang=["en"],
         features=dict(figure=True, multi_column=True),
         evidence="transformer architecture figure dominates page (visual inspection)", gt="text_layer"),

    # 10. Slides
    dict(cat="slides", src="1.png", page=None, lang=["en"], features=dict(),
         evidence="born-digital bullet slide (visual inspection)", gt="none"),
    dict(cat="slides", src="Screenshot from 2026-08-17 14-39-17.png", page=None, lang=["en"], features=dict(),
         evidence="handwritten-style slide (visual inspection)", gt="none"),
    dict(cat="slides", src="Screenshot from 2026-08-17 14-39-28.png", page=None, lang=["en"], features=dict(),
         evidence="handwritten-style slide (visual inspection)", gt="none"),
    dict(cat="slides", src="Screenshot from 2026-08-17 14-39-40.png", page=None, lang=["en"], features=dict(),
         evidence="handwritten-style slide (visual inspection)", gt="none"),
    dict(cat="slides", src="Transformers 1.pdf", page=3, lang=["en"], features=dict(),
         evidence="lecture slide export (text layer verified)", gt="text_layer"),

    # 11. Dense academic page
    dict(cat="dense_academic", src="NIPS-2012-imagenet-classification-with-deep-convolutional-neural-networks-Paper.pdf", page=5, lang=["en"],
         features=dict(dense=True, multi_column=True),
         evidence="dense two-column paper body (text layer verified)", gt="text_layer"),
    dict(cat="dense_academic", src="NIPS-2017-attention-is-all-you-need-Paper.pdf", page=6, lang=["en"],
         features=dict(dense=True, multi_column=True),
         evidence="dense two-column paper body (text layer verified)", gt="text_layer"),
    dict(cat="dense_academic", src="Batch Normalization Accelerating Deep Network Training b.pdf", page=4, lang=["en"],
         features=dict(dense=True, multi_column=True),
         evidence="dense two-column paper body (text layer verified)", gt="text_layer"),
    dict(cat="dense_academic", src="Object Oriented Programming in c++.pdf", page=30, lang=["en"],
         features=dict(dense=True),
         evidence="dense lecture text page (text layer verified)", gt="text_layer"),
    dict(cat="dense_academic", src="1-MA212-Intro+to+IR+&+Boolean+Retrieval.pdf", page=10, lang=["en"],
         features=dict(dense=True),
         evidence="dense lecture text page (text layer verified)", gt="text_layer"),

    # 12. Noisy / low quality (gap: only two verified poor-quality sources)
    dict(cat="noisy_low_quality", src="English only.jpg", page=None, lang=["en"],
         features=dict(formula=True), difficulty="very_hard",
         evidence="blurry photographed handwritten notes (visual inspection)", gt="none"),
    dict(cat="noisy_low_quality", src="photo_5_2024-03-18_13-39-46.jpg", page=None, lang=["en"],
         features=dict(formula=True), difficulty="very_hard",
         evidence="low-resolution photographed handwritten notes (visual inspection)", gt="none"),
]

FEATURE_KEYS = ("table", "formula", "figure", "multi_column", "mixed_language", "dense")


def render_page(pdf: Path, page: int, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(RENDER_DPI), "-f", str(page), "-l", str(page),
         str(pdf), str(out.with_suffix(""))],
        check=True, capture_output=True,
    )
    produced = list(out.parent.glob(out.with_suffix("").name + "*.png"))
    assert len(produced) == 1, f"expected 1 rendered page, got {produced}"
    produced[0].rename(out)


def extract_text_layer(pdf: Path, page: int) -> str:
    r = subprocess.run(
        ["pdftotext", "-f", str(page), "-l", str(page), "-q", str(pdf), "-"],
        check=True, capture_output=True, text=True,
    )
    return r.stdout.strip()


def main() -> int:
    if not SRC.is_dir():
        print(f"ERROR: source pool not found: {SRC}", file=sys.stderr)
        return 1

    manifest_docs = []
    counters: dict[str, int] = {}
    for item in SELECTION:
        cat = item["cat"]
        cat_dirname, default_difficulty = CATEGORIES[cat]
        counters[cat] = counters.get(cat, 0) + 1
        sample_id = f"custom_{cat}_{counters[cat]:03d}"
        cat_dir = CUSTOM / cat_dirname
        cat_dir.mkdir(parents=True, exist_ok=True)

        src_path = SRC / item["src"]
        if not src_path.is_file():
            print(f"ERROR: missing source {src_path}", file=sys.stderr)
            return 1

        ext = src_path.suffix.lower()
        sample_file = f"{sample_id}{ext if ext in ('.png', '.jpg', '.jpeg') else '.png'}"
        target = cat_dir / sample_file

        if item["page"] is None:
            shutil.copy2(src_path, target)
        else:
            render_page(src_path, item["page"], target)

        features = {k: bool(item.get("features", {}).get(k, False)) for k in FEATURE_KEYS}

        gt_status = "pending"
        if item["gt"] == "text_layer":
            gt_dir = GT_ROOT / sample_id
            gt_dir.mkdir(parents=True, exist_ok=True)
            text = extract_text_layer(src_path, item["page"])
            (gt_dir / "text.txt").write_text(text + "\n", encoding="utf-8")
            (gt_dir / "meta.json").write_text(json.dumps({
                "sample_id": sample_id,
                "status": "extracted_unverified",
                "source": "pdf_text_layer (pdftotext)",
                "note": "Extracted from the born-digital PDF text layer. NOT manually "
                        "verified ground truth; may differ from the rendered page "
                        "(ligatures, reading order, formulas). Verify before scoring.",
                "extracted_with": f"pdftotext -f {item['page']} -l {item['page']}",
                "created": "2026-08-17",
            }, indent=2) + "\n", encoding="utf-8")
            gt_status = "extracted_unverified"

        manifest_docs.append({
            "sample_id": sample_id,
            "dataset": "custom",
            "category": cat,
            "category_dir": cat_dirname,
            "language": item["lang"],
            "source_type": "scanned" if item["page"] is None or "no text layer" in item["evidence"] or item["cat"] in ("english_scanned", "arabic_scanned") else "born_digital",
            "file": str(target.relative_to(CUSTOM)),
            "page": item["page"],
            "original_source": item["src"],
            "difficulty": item.get("difficulty", default_difficulty),
            "features": features,
            "ground_truth_status": gt_status,
            "ground_truth_path": f"../../ground_truth/custom/{sample_id}" if gt_status != "pending" else None,
            "provenance_status": "UNKNOWN",
            "render": {"dpi": RENDER_DPI, "tool": "pdftoppm"} if item["page"] is not None else None,
            "evidence": item["evidence"],
        })

    manifest = {
        "schema": "openlearn-ocrbench-manifest",
        "schema_version": 2,
        "dataset": "custom_v2",
        "created": "2026-08-17",
        "sample_unit": "one benchmark sample = one document page or one standalone image",
        "categories": {k: v[0] for k, v in CATEGORIES.items()},
        "null_semantics": {
            "ground_truth_status=pending": "no ground truth exists yet; manual annotation required (annotation-guidelines.md)",
            "ground_truth_status=extracted_unverified": "text extracted from the PDF text layer as a starting point; NOT verified GT",
            "provenance_status=UNKNOWN": "rights unknown; internal research use only (docs/provenance.md)",
        },
        "known_gaps": {
            "arabic_born_digital": "no Arabic born-digital source material exists in Source/ (all Arabic files are scans/photos) — HUMAN ACTION REQUIRED",
            "mixed_arabic_english": "only 1 verified mixed source; roadmap marks mixed Ar/En as highest priority — more sources needed",
            "tables": "3 verified samples (target 5)",
            "noisy_low_quality": "2 verified samples (target 5)",
        },
        "documents": manifest_docs,
    }
    (CUSTOM / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(manifest_docs)} samples across {len(set(d['category'] for d in manifest_docs))} populated categories")
    for cat in CATEGORIES:
        n = counters.get(cat, 0)
        print(f"  {cat}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
