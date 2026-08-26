"""Misraj-DocOCR loader.

Reads the two parquet shards under data/processed/misraj/data and materializes
the embedded PNG page images into a regenerable cache under CACHE_ROOT. The
dataset itself is never written to.
"""

from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from ocrbench import paths
from ocrbench.types import Sample

MISRAJ_ROOT: Path = paths.PROCESSED_ROOT / "misraj"
DATA_DIR: Path = MISRAJ_ROOT / "data"
PAGE_CACHE_DIR: Path = paths.CACHE_ROOT / "misraj_pages"

EXPECTED_SHARDS = 2
EXPECTED_SAMPLES = 400
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _materialize_page(sample_id: str, blob: bytes) -> Path:
    """Write the embedded PNG into the cache (reusing a valid entry)."""
    if not blob:
        raise ValueError(f"misraj {sample_id}: empty image bytes in parquet")
    if not blob.startswith(PNG_MAGIC):
        raise ValueError(f"misraj {sample_id}: image bytes are not PNG")

    dest = PAGE_CACHE_DIR / f"{sample_id}.png"
    if dest.exists() and dest.stat().st_size == len(blob):
        return dest

    PAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob)
    if dest.stat().st_size != len(blob):
        raise ValueError(f"misraj {sample_id}: cache write incomplete ({dest})")
    return dest


def load_misraj() -> list[Sample]:
    """Return the 400 Misraj pages as Samples with materialized page images."""
    shards = sorted(DATA_DIR.glob("*.parquet"))
    if len(shards) != EXPECTED_SHARDS:
        raise ValueError(
            f"misraj: expected {EXPECTED_SHARDS} parquet shards in {DATA_DIR}, "
            f"found {len(shards)}"
        )

    samples: list[Sample] = []
    seen: set[str] = set()

    for shard in shards:
        reader = pq.ParquetFile(shard)
        # The image lives in an `image` struct<bytes, path> at the Arrow level
        # (raw Parquet metadata shows the same leaves flattened).
        missing = [
            c for c in ("uuid", "markdown", "image")
            if c not in reader.schema_arrow.names
        ]
        if missing:
            raise ValueError(f"misraj {shard.name}: missing columns {missing}")

        for batch in reader.iter_batches(
            batch_size=25, columns=["uuid", "markdown", "image"]
        ):
            for row in batch.to_pylist():
                sample_id = row["uuid"]
                markdown = row["markdown"]
                if not isinstance(sample_id, str) or not sample_id:
                    raise ValueError(f"misraj {shard.name}: invalid uuid {sample_id!r}")
                if sample_id in seen:
                    raise ValueError(f"misraj: duplicate sample id {sample_id!r}")
                if not isinstance(markdown, str) or not markdown.strip():
                    raise ValueError(f"misraj {sample_id}: empty reference markdown")
                seen.add(sample_id)

                image_struct = row["image"] or {}
                blob = image_struct.get("bytes")
                image_name = image_struct.get("path")
                image_path = _materialize_page(sample_id, blob)
                samples.append(
                    Sample(
                        sample_id=sample_id,
                        image_path=image_path,
                        reference_text=markdown,
                        metadata={"image_name": image_name},
                    )
                )

    if len(samples) != EXPECTED_SAMPLES:
        raise ValueError(
            f"misraj: expected {EXPECTED_SAMPLES} samples, loaded {len(samples)}"
        )
    if len(seen) != EXPECTED_SAMPLES:
        raise ValueError(f"misraj: expected {EXPECTED_SAMPLES} unique ids, got {len(seen)}")

    unresolved = [s.sample_id for s in samples if not s.image_path.is_file()]
    if unresolved:
        raise ValueError(f"misraj: missing cached images for {unresolved[:5]}...")

    samples.sort(key=lambda s: s.sample_id)
    return samples
