"""_bench_paths.py — canonical path resolution for ocr-benchmark scripts.

Single strategy for every script in this directory:

- The benchmark project root is derived from THIS file's location
  (`<root>/scripts/_bench_paths.py`), never from Path.cwd(). Scripts behave
  identically whether invoked from `ocr-benchmark/`, `ocr-benchmark/scripts/`,
  or any other working directory.

- CLI-supplied relative paths are interpreted as PROJECT-ROOT-relative
  (matching the conventions used inside manifests, configs, and docs).
  Absolute paths are honored as-is.
"""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the ocr-benchmark/ root directory (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent


def resolve_path(path: str | Path) -> Path:
    """Resolve a user-supplied path.

    Absolute paths pass through unchanged (after ~ expansion); relative
    paths are resolved against the benchmark project root.
    """
    p = Path(path).expanduser()
    return p if p.is_absolute() else project_root() / p
