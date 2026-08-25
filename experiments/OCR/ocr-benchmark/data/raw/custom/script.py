#!/usr/bin/env python3

"""
Split every PDF in a working copy of data/raw/custom/ into one-page PDFs.

IMPORTANT:
- This script is intended to run ONLY on a COPY of the dataset.
- It preserves the original directory structure.
- Each PDF page becomes a standalone PDF.
- Output filenames follow the benchmark sample_id convention:
    custom_<slugified-original-stem>_p001.pdf
    custom_<slugified-original-stem>_p002.pdf
    ...
- The original multi-page PDF is deleted ONLY after all page files
  have been successfully created and validated.
- Standalone images are untouched.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def slugify_filename(stem: str) -> str:
    """
    Convert a filename stem into the same style used by the benchmark IDs.

    Example:
        Custom_English_born_digital_001
        ->
        custom_english_born_digital_001
    """

    value = stem.strip().lower()

    # Replace non-alphanumeric runs with underscores.
    value = re.sub(r"[^a-z0-9]+", "_", value)

    # Collapse repeated underscores.
    value = re.sub(r"_+", "_", value)

    # Remove leading/trailing underscores.
    return value.strip("_")


def make_sample_id(pdf_path: Path, page_number: int) -> str:
    """
    Build the page-level sample ID.

    Example:
        custom_custom_english_born_digital_001_p001
    """

    stem_slug = slugify_filename(pdf_path.stem)

    return f"custom_{stem_slug}_p{page_number:03d}"


def split_pdf(pdf_path: Path, dry_run: bool = False) -> int:
    """
    Split one PDF into standalone one-page PDFs.

    Returns the number of generated pages.
    """

    print(f"\nPDF: {pdf_path}")

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        raise RuntimeError(
            f"Could not read PDF: {pdf_path}\n{exc}"
        ) from exc

    page_count = len(reader.pages)

    if page_count == 0:
        raise RuntimeError(f"PDF contains zero pages: {pdf_path}")

    print(f"Pages: {page_count}")

    output_paths: list[Path] = []

    for index, page in enumerate(reader.pages, start=1):
        sample_id = make_sample_id(pdf_path, index)

        output_path = pdf_path.with_name(
            f"{sample_id}.pdf"
        )

        output_paths.append(output_path)

        print(f"  -> {output_path.name}")

        if dry_run:
            continue

        # Never overwrite an existing file.
        if output_path.exists():
            raise RuntimeError(
                f"Refusing to overwrite existing file:\n"
                f"  {output_path}"
            )

        writer = PdfWriter()
        writer.add_page(page)

        with output_path.open("wb") as output_file:
            writer.write(output_file)

    if dry_run:
        return page_count

    # Validate that every expected output exists.
    missing = [
        path for path in output_paths
        if not path.is_file() or path.stat().st_size == 0
    ]

    if missing:
        raise RuntimeError(
            "Splitting failed. Missing/empty output files:\n"
            + "\n".join(str(path) for path in missing)
        )

    # Validate each generated PDF has exactly one page.
    for output_path in output_paths:
        try:
            generated_reader = PdfReader(str(output_path))

            if len(generated_reader.pages) != 1:
                raise RuntimeError(
                    f"Generated file does not contain exactly one page:\n"
                    f"  {output_path}"
                )

        except Exception as exc:
            raise RuntimeError(
                f"Generated PDF failed validation:\n"
                f"  {output_path}\n"
                f"{exc}"
            ) from exc

    # ONLY NOW delete the original.
    pdf_path.unlink()

    print(f"  Original deleted: {pdf_path.name}")

    return page_count


def find_pdfs(root: Path) -> list[Path]:
    """
    Find PDFs recursively.

    Sorted for deterministic processing.
    """

    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() == ".pdf"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Split all PDFs in a working copy of the custom OCR "
            "dataset into one-page PDFs."
        )
    )

    parser.add_argument(
        "root",
        type=Path,
        help="Path to the WORKING COPY of data/raw/custom/",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show what would happen without creating or deleting "
            "any files."
        ),
    )

    args = parser.parse_args()

    root = args.root.resolve()

    if not root.exists():
        print(f"ERROR: directory does not exist: {root}")
        return 1

    if not root.is_dir():
        print(f"ERROR: path is not a directory: {root}")
        return 1

    print("=" * 72)
    print("CUSTOM OCR PDF PAGE SPLITTER")
    print("=" * 72)
    print(f"Working directory: {root}")
    print(f"Dry run: {args.dry_run}")
    print()

    pdfs = find_pdfs(root)

    if not pdfs:
        print("No PDF files found.")
        return 0

    print(f"Found {len(pdfs)} PDF file(s).")

    # Safety confirmation unless dry-run.
    if not args.dry_run:
        print()
        print(
            "WARNING: This will DELETE the original PDFs "
            "inside this working copy AFTER successful splitting."
        )
        print("Your original dataset should NOT be this directory.")
        print()

        answer = input("Type SPLIT to continue: ")

        if answer != "SPLIT":
            print("Aborted.")
            return 1

    total_pages = 0

    try:
        for pdf_path in pdfs:
            total_pages += split_pdf(
                pdf_path,
                dry_run=args.dry_run,
            )

    except Exception as exc:
        print()
        print("=" * 72)
        print("ERROR")
        print("=" * 72)
        print(exc)
        print()
        print(
            "The script stopped immediately. "
            "Check the working copy before continuing."
        )
        return 1

    print()
    print("=" * 72)
    print("DONE")
    print("=" * 72)
    print(f"PDF files processed: {len(pdfs)}")
    print(f"Pages generated:     {total_pages}")

    if args.dry_run:
        print()
        print("DRY RUN: No files were modified.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
