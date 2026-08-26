#!/usr/bin/env bash
# build_data_manifest.sh — deterministic integrity record for the Misraj source data.
#
# Produces data/processed/misraj/DATA_MANIFEST.sha256 with one line per file:
#     <sha256>  <byte_size>  <repo-relative-path>
# (paths relative to the ocr-benchmark project root)
#
# Deterministic: sorted by path; no timestamps; read-only over the dataset.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MISRAJ_DIR="$PROJECT_ROOT/data/processed/misraj"
MANIFEST="$MISRAJ_DIR/DATA_MANIFEST.sha256"
# Tracked twin: data/processed/** is gitignored, but external-GPU consumers
# verify against the repository checkout, so the same bytes are published
# under configs/datasets/ in the same write (no drift possible).
TRACKED_COPY="$PROJECT_ROOT/configs/datasets/misraj_DATA_MANIFEST.sha256"

FILES=(
    "data/processed/misraj/data/train-00000-of-00002.parquet"
    "data/processed/misraj/data/train-00001-of-00002.parquet"
)

tmp="$(mktemp)"
for rel in "${FILES[@]}"; do
    f="$PROJECT_ROOT/$rel"
    if [[ ! -f "$f" ]]; then
        echo "ERROR: missing dataset file: $rel" >&2
        rm -f "$tmp"
        exit 1
    fi
    hash=$(sha256sum "$f" | awk '{print $1}')
    size=$(stat -c '%s' "$f")
    printf '%s  %s  %s\n' "$hash" "$size" "$rel" >> "$tmp"
done

sort -o "$tmp" "$tmp"
mv "$tmp" "$MANIFEST"
cp "$MANIFEST" "$TRACKED_COPY"
echo "manifest written: ${MANIFEST#$PROJECT_ROOT/} (+ tracked copy: ${TRACKED_COPY#$PROJECT_ROOT/})"
cat "$MANIFEST"
