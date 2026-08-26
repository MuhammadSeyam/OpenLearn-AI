#!/usr/bin/env bash
# build_misraj_archive.sh — deterministic single-file dataset archive for external GPU runtimes.
#
# Output: dist/ocrbench-misraj-data-v1.tar.gz (+ .sha256 sidecar)
# Contents: ONLY the two canonical Misraj parquet shards, stored under their
#           repo-relative paths so the archive extracts directly into the
#           ocr-benchmark project root.
#
# Determinism: sorted names, fixed mtime, normalized ownership, gzip -n.
# The dataset itself is never modified.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

MANIFEST="data/processed/misraj/DATA_MANIFEST.sha256"
if [[ ! -f "$MANIFEST" ]]; then
    echo "ERROR: $MANIFEST missing — run scripts/build_data_manifest.sh first" >&2
    exit 1
fi

FILES=(
    "data/processed/misraj/data/train-00000-of-00002.parquet"
    "data/processed/misraj/data/train-00001-of-00002.parquet"
)
for rel in "${FILES[@]}"; do
    [[ -f "$rel" ]] || { echo "ERROR: missing $rel" >&2; exit 1; }
done

mkdir -p dist
ARCHIVE="dist/ocrbench-misraj-data-v1.tar.gz"

# --sort=name + fixed --mtime + owner/group normalization → byte-reproducible tar;
# gzip -n strips the gzip timestamp.
tar --sort=name --format=posix --mtime='UTC 2026-08-26' \
    --owner=0 --group=0 --numeric-owner \
    -cf - "${FILES[@]}" | gzip -n > "$ARCHIVE"

sha256sum "$ARCHIVE" | awk '{print $1}' > "$ARCHIVE.sha256"
echo "archive: $ARCHIVE ($(stat -c '%s' "$ARCHIVE") bytes)"
echo "sha256:  $(cat "$ARCHIVE.sha256")"
