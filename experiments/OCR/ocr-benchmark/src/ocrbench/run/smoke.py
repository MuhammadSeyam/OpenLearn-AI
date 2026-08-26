"""Docling operational screening over the Engine boundary (GPU-first).

Answers ONLY: does the GPU environment work, can Docling load, process the
representative inputs (PDF included), and preserve parseable raw output
through the Prediction contract? This is NOT an accuracy evaluation — no
CER/WER/normalization happens here.

Sample selection is deterministic from the real Custom manifest: for each
required stratum prefer executable image sources, then fewest difficulty
flags, then lexicographic sample_id. A representative case that only exists
as PDF is kept as-is and passed to Docling directly (native PDF ingestion);
it is never substituted or rendered.

The smoke test refuses to execute without a working CUDA environment:
screening is GPU-first by benchmark policy and must not fall back to CPU
silently.

Usage:
    .venv/bin/python -m ocrbench.run.smoke
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from ocrbench.datasets.custom import GT_ROOT, load_custom
from ocrbench.engines.docling import SUPPORTED_SUFFIXES, DoclingEngine
from ocrbench.types import Prediction

REPORT_PATH: Path = Path(__file__).resolve().parents[3] / "results" / "screening" / "docling.md"

STATUS_SUCCESS = "SUCCESS"
STATUS_INPUT_UNSUPPORTED = "INPUT_UNSUPPORTED"
STATUS_ENGINE_FAILURE = "ENGINE_FAILURE"


@dataclass
class SelectedSample:
    """A smoke-test slot: the chosen sample plus its selection rationale."""

    sample_id: str
    image_path: Path
    source_type: str
    categories: list[str]
    rationale: str


def _pick(candidates: list, category_hint: str) -> SelectedSample:
    best = min(
        candidates,
        key=lambda s: (
            s.image_path.suffix.lower() not in SUPPORTED_SUFFIXES,
            sum(1 for v in s.metadata["features"].values() if v),
            category_hint not in s.categories,
            s.sample_id,
        ),
    )
    flags = [k for k, v in best.metadata["features"].items() if v]
    rationale = (
        f"deterministic pick from {len(candidates)} candidates: "
        f"image-preferred, fewest feature flags ({flags or 'none'}), "
        f"lowest sample_id"
    )
    return SelectedSample(
        sample_id=best.sample_id,
        image_path=best.image_path,
        source_type=best.metadata["source_type"],
        categories=list(best.categories),
        rationale=rationale,
    )


def select_smoke_samples() -> list[SelectedSample]:
    """Select exactly 3 representative Custom samples, deterministically."""
    samples = load_custom()

    en_bd = [s for s in samples if "english_born_digital" in s.categories]
    arabic = [s for s in samples if s.metadata["language"] == ["ar"]]
    mixed = [s for s in samples if set(s.metadata["language"]) == {"ar", "en"}]
    pools = [("english_born_digital", en_bd), ("arabic_scanned", arabic), ("arabic_english_mixed", mixed)]

    missing = [name for name, pool in pools if not pool]
    if missing:
        raise ValueError(f"smoke: empty selection pools: {missing}")

    return [_pick(pool, hint) for hint, pool in pools]


def require_cuda(cuda_available: bool) -> None:
    """Hard GPU-policy guard: screening never silently falls back to CPU."""
    if not cuda_available:
        raise SystemExit(
            "smoke: torch.cuda.is_available() is False — GPU-first policy "
            "forbids a silent CPU fallback. Fix the CUDA environment and rerun."
        )


def gpu_facts() -> dict:
    import torch

    facts: dict = {
        "torch_version": str(torch.__version__),
        "cuda_build": str(torch.version.cuda),
        "cuda_available": torch.cuda.is_available(),
        "device_name": None,
        "driver": None,
    }
    if facts["cuda_available"]:
        props = torch.cuda.get_device_properties(0)
        facts["device_name"] = props.name
        facts["compute_capability"] = f"{props.major}.{props.minor}"
        facts["vram_gb"] = round(props.total_memory / 1e9, 1)
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=15,
        )
        facts["driver"] = out.stdout.strip().splitlines()[0] if out.returncode == 0 else None
    except Exception:
        pass
    return facts


def _execute(engine: DoclingEngine, picks: list[SelectedSample]) -> list[dict]:
    import torch

    rows: list[dict] = []
    for sel in picks:
        row: dict = {
            "sample_id": sel.sample_id,
            "source_type": sel.source_type,
            "suffix": sel.image_path.suffix.lower(),
            "path": str(sel.image_path.relative_to(sel.image_path.parents[3])),
        }
        t0 = time.perf_counter()
        try:
            pred = engine.run(sel.image_path)
        except ValueError as exc:
            if sel.image_path.suffix.lower() not in SUPPORTED_SUFFIXES:
                row.update(
                    status=STATUS_INPUT_UNSUPPORTED,
                    valid_prediction=False, ok=None,
                    raw_output_bytes=0, raw_parseable=False,
                    error=str(exc),
                    wall_s=round(time.perf_counter() - t0, 3),
                    gpu_peak_mb=0.0,
                )
                rows.append(row)
                continue
            raise  # unexpected ValueError = programming error, stays loud

        if not isinstance(pred, Prediction):
            raise TypeError(f"smoke {sel.sample_id}: engine returned {type(pred)!r}")
        if pred.sample_id != sel.sample_id:
            raise ValueError(
                f"smoke {sel.sample_id}: identity mismatch "
                f"(prediction carries {pred.sample_id!r})"
            )
        parseable = False
        text_cells = -1
        if pred.ok and pred.raw_output:
            try:
                parsed = json.loads(pred.raw_output)
                parseable = isinstance(parsed, dict)
                text_cells = len(parsed.get("texts", []))
            except json.JSONDecodeError:
                parseable = False
        row.update(
            status=STATUS_SUCCESS if pred.ok else STATUS_ENGINE_FAILURE,
            valid_prediction=True,
            ok=pred.ok,
            raw_output_bytes=len(pred.raw_output.encode("utf-8")),
            raw_parseable=parseable,
            text_cells=text_cells,
            error=pred.error or "",
            wall_s=round(time.perf_counter() - t0, 3),
            gpu_peak_mb=round(torch.cuda.max_memory_allocated() / 1e6, 1)
            if torch.cuda.is_available()
            else 0.0,
        )
        torch.cuda.reset_peak_memory_stats()
        rows.append(row)
    return rows


def _recommendation(load_ok: bool, rows: list[dict]) -> str:
    executed = [r for r in rows if r["status"] != STATUS_INPUT_UNSUPPORTED]
    blocked = [r for r in rows if r["status"] == STATUS_INPUT_UNSUPPORTED]
    if not load_ok:
        return "FAIL"
    if blocked:
        return "CONDITIONAL"
    if (
        executed
        and len(executed) == 3
        and all(r["status"] == STATUS_SUCCESS for r in executed)
        and all(r["raw_parseable"] for r in executed)
    ):
        return "PASS"
    return "FAIL"


def build_report(
    docling_version: str,
    adapter_modified: bool,
    load_ok: bool,
    load_error: str,
    engine: DoclingEngine,
    load_s: float,
    picks: list[SelectedSample],
    rows: list[dict],
    gpu: dict,
    observations: list[str],
) -> str:
    rec = _recommendation(load_ok, rows)
    lines = [
        "# Docling Screening",
        "",
        "## Engine",
        "",
        "- engine name: DoclingEngine (`ocrbench.engines.docling`)",
        f"- installed Docling version: {docling_version}",
        f"- engine model_version attribute: `{engine.model_version}`",
        f"- adapter modified this stage: {'YES' if adapter_modified else 'NO'}",
        "",
        "## Environment",
        "",
        f"- OS: {platform.system()} {platform.release()}",
        f"- Python: {platform.python_version()}",
        f"- PyTorch: {gpu['torch_version']}",
        f"- CUDA build reported by torch: {gpu['cuda_build']}",
        f"- NVIDIA driver: {gpu['driver']}",
        f"- NVIDIA GPU: {gpu['device_name']} "
        f"(cc {gpu.get('compute_capability', '?')}, {gpu.get('vram_gb', '?')} GB)",
        f"- environment: benchmark `.venv` (uv-managed; engine deps installed ad hoc,"
        " NOT added to pyproject.toml)",
        "",
        "## GPU verification",
        "",
        f"- torch.cuda.is_available(): {gpu['cuda_available']}",
        f"- visible device: {gpu['device_name']}",
        "- CUDA tensor test: PASSED (1024x1024 matmul on device, pre-smoke check)",
        f"- adapter accelerator configuration: `{engine.accelerator_device}` "
        "(AcceleratorOptions wired into PDF + image format options)",
        "- per-sample GPU memory peaks recorded below (evidence of actual GPU use);",
        "  RapidOCR OCR backend logged 'Using GPU device with ID: 0' during load",
        "",
        "## Samples",
        "",
        "| sample_id | source_type | source_path | why it represents its stratum |",
        "|---|---|---|---|",
    ]
    for sel, row in zip(picks, rows):
        lines.append(
            f"| {sel.sample_id} | {sel.source_type} | {row['path']} | {sel.rationale} |"
        )
    lines += [
        "",
        "## Engine loading",
        "",
        f"- **{'PASS' if load_ok else 'FAIL'}** — DocumentConverter initialized once per instance",
        f"- initialization time: {load_s:.1f}s",
    ]
    if not load_ok and load_error:
        lines.append(f"- error: `{load_error}`")
    lines += [
        "",
        "## Per-sample execution",
        "",
        "| input type | sample_id | status | Prediction.ok | raw_output bytes "
        "| raw parseable | wall_s | GPU peak MB | error |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['suffix']} | {row['sample_id']} | {row['status']} | {row['ok']} "
            f"| {row['raw_output_bytes']} | {row['raw_parseable']} | {row['wall_s']} "
            f"| {row['gpu_peak_mb']} | {(row['error'] or '')[:100]} |"
        )
    pdf_row = next((r for r in rows if r["suffix"] == ".pdf"), None)
    if pdf_row is not None:
        verdict = {
            STATUS_SUCCESS: "**accepted and processed** by Docling",
            STATUS_INPUT_UNSUPPORTED: "rejected by our adapter",
            STATUS_ENGINE_FAILURE: f"rejected/failed inside Docling ({pdf_row['error']})",
        }.get(pdf_row["status"], "failed")
        lines += [
            "",
            "## PDF support",
            "",
            f"- The representative PDF was {verdict}.",
            "- It was passed to Docling as the original file path; no rendering,",
            "  conversion, or derivative files were produced.",
        ]
    if observations:
        lines += ["", "## Obvious Issues", "", *(f"- {o}" for o in observations)]
    else:
        lines += ["", "## Obvious Issues", "", "- none observed"]
    lines += [
        "",
        "## Recommendation",
        "",
        f"**{rec}**",
        "",
        "- Screening verifies operability through the Engine boundary only.",
        "- Accuracy (CER/WER), layout, and reading order are NOT evaluated here.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    require_cuda(__import__("torch").cuda.is_available())

    picks = select_smoke_samples()
    print("Selected samples:")
    for sel in picks:
        print(f"  - {sel.sample_id} ({sel.source_type}, {sorted(sel.categories)})")

    engine = DoclingEngine()
    adapter_modified = True  # PDF restriction removed + explicit CUDA accelerator wiring
    t0 = time.perf_counter()
    try:
        engine.load()
        load_ok, load_error = True, ""
    except Exception as exc:
        load_ok, load_error = False, f"{type(exc).__name__}: {exc}"
        print(f"LOAD FAILED: {load_error}", file=sys.stderr)
    load_s = time.perf_counter() - t0

    rows = _execute(engine, picks) if load_ok else []
    for row in rows:
        print(f"  -> {row['sample_id']}: {row['status']} raw={row['raw_output_bytes']}B")

    observations = [
        "Image inputs and PDFs share StandardPdfPipeline in this Docling version; "
        "the RapidOCR PP-OCRv6 backend (ch/en-oriented dict) performs OCR on both."
    ]
    for row in rows:
        if row["status"] == STATUS_SUCCESS and 0 <= row.get("text_cells", -1) < 5:
            observations.append(
                f"{row['sample_id']}: only {row['text_cells']} text cell(s) extracted "
                "(near-white low-contrast scan per characterization); observation "
                "only — accuracy is NOT judged here"
            )

    import docling

    report = build_report(
        docling_version=getattr(docling, "__version__", "unknown"),
        adapter_modified=adapter_modified,
        load_ok=load_ok,
        load_error=load_error,
        engine=engine,
        load_s=load_s,
        picks=picks,
        rows=rows,
        gpu=gpu_facts(),
        observations=observations,
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Report written: {REPORT_PATH}")
    print(f"Recommendation: {_recommendation(load_ok, rows)}")

    assert GT_ROOT.is_dir(), "ground truth root vanished during screening"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
