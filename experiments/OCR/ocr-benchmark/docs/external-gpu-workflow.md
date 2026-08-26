# External GPU Workflow

**Status:** infrastructure runbook · **Scope:** execution environments only
**Principle:** *Colab is an execution environment, not a benchmark layer.*

There is ONE benchmark architecture and ONE Engine abstraction
(`ocrbench.engines.base.Engine` → `Prediction`). Where the GPU lives — local,
Colab, Kaggle, cloud — is infrastructure. No `RemoteEngine`/`LocalEngine`
split, no HTTP bridge, no execution backend exists or may be introduced.

---

## 1. Why external GPUs

The local development GPU is an RTX 3050 Laptop (4 GB). It runs Docling but
cannot fit every candidate engine (e.g., PaddleOCR-VL needs >4 GB at init).
External runtimes provide larger GPUs on demand without changing a single line
of benchmark code.

## 2. Why this does NOT change the architecture

The external runtime consumes the same repository, package, CLI, loaders,
engine adapters, and result format:

```
git clone (pinned commit)
  → uv Python 3.12 env from the repo's own pyproject/uv.lock
  → ad-hoc engine dependency install (project policy; engines stay out of pyproject)
  → canonical dataset archive + SHA-256 verification
  → .venv/bin/python -m ocrbench.run.run_text --limit N --engine docling   [EXISTING command]
  → results/formal/<dataset>/<engine>/<timestamp>/…                        [EXISTING structure]
  → archive artifact → download → local analysis
```

Only the machine changes.

## 3. Primary external runtime: Google Colab

Chosen for: free T4 16 GB, native Drive round-trip for artifacts and the
dataset archive, minimal setup, and headroom for engines that exceed 4 GB.

## 4. Fallback: Kaggle

Equally compatible via the same notebook logic (attach the dataset as a Kaggle
Dataset instead of Drive). Not implemented yet; revisit only if Colab quota
becomes a constraint.

## 5. Required GPU validation

The notebook asserts, in order:

1. `nvidia-smi` present;
2. `torch.cuda.is_available()` is True (system torch used only for this gate);
3. device name / total VRAM / CUDA build printed;
4. a real CUDA tensor matmul succeeds.

GPU-first policy: if any check fails, stop. Never fall back to CPU silently.
Inside the benchmark run itself, `run_text.py` re-verifies CUDA and aborts
otherwise (`_require_gpu`), and asserts the adapter's accelerator is `cuda`.

### 5.1 PaddleOCR-VL specifics (T4)

- Stack (pinned, ad-hoc in `.venv`): `paddlepaddle-gpu==3.2.2` (Baidu cu126
  index) + `paddleocr[doc-parser]>=3.7,<3.8`. Torch is installed first from
  the pytorch cu126 index so the whole stack shares the **cu12** wheel family.
- **NCCL collision caveat**: `nvidia-nccl-cu12` (paddle) and a cu13 torch would
  clobber each other's `nvidia/nccl/lib/libnccl.so.2` (last install wins). The
  notebook keeps everything on cu12 and includes an import guard that repairs
  torch's NCCL once if a collision is ever detected; both imports are then
  re-verified. Never mix cu12-paddle with a cu13-torch install order.
- **Precision on T4**: Turing has no native BF16, so paddlex selects fp32 for
  the 0.9 B VL weights (~3.6 GB) — fits comfortably in 15.6 GB. Expect slower
  decoding than bf16-on-Ampere; measure per-page wall time during the pilot
  before authorizing formal runs.
- **Persistent model cache (source-verified)**: paddlex reads
  `PADDLE_PDX_CACHE_HOME` (`paddlex/utils/cache.py:29`) and stores models under
  `<cache>/official_models` (`official_models.py:880`). The notebook sets it to
  `Drive/ocrbench/models/paddlex_cache`, so the ~1.8 GB PaddleOCR-VL-1.6
  weights download once and persist across sessions. Set the variable before
  the first paddle import.
- **One-image probe gate**: the notebook runs exactly one real Misraj page
  through the adapter before any pilot and dumps the payload structure — the
  extraction contract is anchored to observed reality, not assumptions.

## 6. Python / uv setup

Colab host images do not guarantee Python ≥ 3.12 (`requires-python` in
`pyproject.toml`). The notebook therefore bootstraps an isolated interpreter:

```
pip install uv
uv python install 3.12
uv venv --python 3.12 .venv      # inside experiments/OCR/ocr-benchmark/
uv sync --frozen                 # exact core deps from uv.lock; installs ocrbench editable
uv pip install "docling>=2.0"    # ad-hoc engine dep, same policy as local (.venv only)
```

`pyproject.toml` must never be relaxed to accommodate a host image.

## 7. Dataset archive strategy (upload ONCE)

- Build locally: `bash scripts/build_misraj_archive.sh`
  → `dist/ocrbench-misraj-data-v1.tar.gz` (+ `.sha256` sidecar).
- Contents: ONLY the two canonical Misraj parquet shards under their
  repo-relative paths. Excluded by construction: caches, results, .venv,
  model weights.
- Deterministic: sorted members, fixed mtime, `gzip -n` — rebuilding yields a
  byte-identical archive (verified twice locally).
- Upload the single file to Drive once (`MyDrive/ocrbench/`). Individual
  dataset files are never re-uploaded.

When another stage needs Custom/BCE externally, extend
`scripts/build_misraj_archive.sh` with those paths and bump the version suffix
(`-v2`) — new snapshot, new name, old archives stay valid.

## 8. SHA-256 verification (mandatory gate)

Before extraction the notebook compares the downloaded archive's SHA-256 to
the pinned constant. After extraction it verifies every line of the tracked
integrity record `configs/datasets/misraj_DATA_MANIFEST.sha256`
(`sha256 · byte size · path`; generated by `scripts/build_data_manifest.sh`,
which also mirrors it to `data/processed/misraj/DATA_MANIFEST.sha256` for
local workflows — `data/processed/**` itself is gitignored, so the configs
copy is what travels with a clone). Any mismatch aborts before a single
benchmark step runs.

Regenerate only when the dataset snapshot legitimately changes:
`bash scripts/build_data_manifest.sh` (updates both copies atomically).

## 9. The benchmark command (unchanged)

```
cd /content/OpenLearn-AI/experiments/OCR/ocr-benchmark
.venv/bin/python -m ocrbench.run.run_text --limit 20 --engine docling
```

Same loader, same deterministic selection (loader natural order), same retry
policy, same metrics, same output writer as the local known-good run
(`results/formal/misraj/docling/20260825-184822/`).

## 10. Result artifact handling

The notebook locates the newest timestamped run directory, validates it
(`raw_outputs/` count == limit, `metrics.json` fields, all four artifact
classes present, accelerator == cuda), then tars it to:

```
/content/drive/MyDrive/ocrbench/external_result_<timestamp>.tar.gz
```

and prints the exact path. Results are gitignored by policy — artifacts move
via Drive, never through git.

## 11. Downloading results back locally

```
# after downloading external_result_<timestamp>.tar.gz from Drive:
mkdir -p "experiments/OCR/ocr-benchmark/results/formal/misraj/docling/ext-<timestamp>"
tar -xzf external_result_<timestamp>.tar.gz \
    -C "experiments/OCR/ocr-benchmark/results/formal/misraj/docling/"
```

Local validation checklist (no evaluator changes needed):

1. Directory contains exactly `raw_outputs/`, `metrics.json`, `config.yaml`,
   `run_log.md`.
2. `raw_outputs/` has 20 verbatim JSON files.
3. `metrics.json`: `sample_count == 20`; `selected_sample_ids` identical to
   the local reference run's (same deterministic selection);
   `accelerator_device == "cuda"`; micro/macro blocks present.
4. Spot-check one raw output: parseable JSON, matches that sample's stored
   hypothesis lengths.
5. Record comparison notes beside the artifact; do not overwrite the local
   reference run.

## 12. Known limitation: ephemerality

Colab runtimes are ephemeral (session limits, disk wiped on disconnect).
Mitigations already in place: raw outputs are written incrementally during the
run (a disconnect loses at most one sample); the entire 20-page pilot takes
minutes, so a clean re-run is cheap. Resume functionality was deliberately
deferred until real experience shows it is needed. Long formal runs (400
pages) should copy partial artifacts to Drive periodically at the notebook
level.

---

## Step 0 prerequisite (one-time)

The pinned commit in the notebook must contain the committed benchmark
implementation. As of 2026-08-26 the implementation exists in the local
working tree but is **not yet committed/pushed**; committing requires explicit
authorization. When approved:

```
git add src tests scripts notebooks docs configs/datasets/misraj_DATA_MANIFEST.sha256 .gitignore
git commit -m "OCR benchmark: evaluation layer, Docling/Paddle adapters, external-GPU workflow"
git push origin main        # then update PINNED_COMMIT in notebooks/colab_gpu_smoke.ipynb
```

Dataset files are not part of this commit (gitignored; delivered via archive).
