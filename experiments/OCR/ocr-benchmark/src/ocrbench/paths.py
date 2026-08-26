"""Filesystem locations for the OCR benchmark.

Single source of truth for project-relative paths. All constants resolve
relative to the repository root derived from this file's location, so the
package behaves identically from any working directory.

Assumes the package is used from a repository checkout / editable install;
the datasets, results, and cache trees live inside the repository itself.
Importing this module has no filesystem side effects (nothing is created).
"""

from __future__ import annotations

from pathlib import Path

# src/ocrbench/paths.py -> ocr-benchmark/
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent

DATA_ROOT: Path = PROJECT_ROOT / "data"
PROCESSED_ROOT: Path = DATA_ROOT / "processed"
GROUND_TRUTH_ROOT: Path = DATA_ROOT / "ground_truth"

CUSTOM_GROUND_TRUTH_ROOT: Path = GROUND_TRUTH_ROOT / "custom"

CACHE_ROOT: Path = DATA_ROOT / "cache"

RESULTS_ROOT: Path = PROJECT_ROOT / "results"

__all__ = [
    "PROJECT_ROOT",
    "DATA_ROOT",
    "PROCESSED_ROOT",
    "GROUND_TRUTH_ROOT",
    "CUSTOM_GROUND_TRUTH_ROOT",
    "CACHE_ROOT",
    "RESULTS_ROOT",
]
