"""Text-accuracy runner: Docling × Misraj pilot (GPU-first, sequential).

Implements the benchmark execution policy for one vertical slice:

load dataset → load engine (timed) → warm-up → select samples
→ sequential inference → immediate raw-output persistence
→ per-sample raw+normalized CER/WER → micro/macro aggregation
→ timestamped result directory (never overwritten).

Policies honored:
- GPU guard: refuses to run without CUDA (no silent CPU fallback).
- Retry: at most one second attempt on a failed prediction (architecture §24).
- Failures score CER=WER=1.0 naturally via an empty hypothesis and are
  reported separately; they are never silently dropped.
- Empty references are excluded from scoring and explicitly counted.
- Raw engine output is saved verbatim during execution, before any metric.

Usage:
    .venv/bin/python -m ocrbench.run.run_text --limit 20
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path

import yaml

from ocrbench.datasets.misraj import load_misraj
from ocrbench.engines.docling import SUPPORTED_SUFFIXES, DoclingEngine
from ocrbench.metrics.normalize import NORMALIZATION_NOTES, NORMALIZATION_VERSION, normalize_text
from ocrbench.metrics.text import cer, macro_cer, macro_wer, micro_cer, micro_wer, wer
from ocrbench.types import Prediction


def _scores(reference: str, hypothesis: str) -> dict:
    """Raw + normalized lengths and CER/WER for one sample."""
    reference_norm = normalize_text(reference)
    hypothesis_norm = normalize_text(hypothesis)

    def lens(ref: str, hyp: str) -> dict:
        return {
            "reference_length": len(ref),
            "hypothesis_length": len(hyp),
            "cer": cer(ref, hyp),
            "wer": wer(ref, hyp),
        }

    return {
        "raw": lens(reference, hypothesis),
        "normalized": lens(reference_norm, hypothesis_norm),
        "text": {
            "reference_raw": reference,
            "hypothesis_raw": hypothesis,
            "reference_normalized": reference_norm,
            "hypothesis_normalized": hypothesis_norm,
        },
    }


def _gpu_info() -> dict:
    import torch

    info: dict = {
        "torch": str(torch.__version__),
        "cuda_build": str(torch.version.cuda),
        "cuda_available": torch.cuda.is_available(),
        "device": None,
        "driver": None,
    }
    if info["cuda_available"]:
        props = torch.cuda.get_device_properties(0)
        info["device"] = props.name
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=15,
        )
        if out.returncode == 0:
            info["driver"] = out.stdout.strip().splitlines()[0]
    except Exception:
        pass
    return info


def _require_gpu(gpu: dict) -> None:
    if not gpu["cuda_available"]:
        raise SystemExit(
            "run_text: torch.cuda.is_available() is False — GPU-first policy "
            "forbids a silent CPU fallback. Fix the CUDA environment."
        )


def _run_with_retry(engine: DoclingEngine, image_path: Path) -> tuple[Prediction, float, int]:
    """Attempt 1 → optional single retry → final result. Returns (pred, s, retries)."""
    start = time.perf_counter()
    pred = engine.run(image_path)
    retries = 0
    if not pred.ok:
        retries = 1
        pred = engine.run(image_path)
    return pred, time.perf_counter() - start, retries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Misraj × engine text pilot")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--engine", default="docling", choices=["docling"])
    args = parser.parse_args(argv)

    gpu = _gpu_info()
    _require_gpu(gpu)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path(__file__).resolve().parents[3] / "results" / "formal" / "misraj" / args.engine / timestamp
    raw_dir = run_dir / "raw_outputs"
    raw_dir.mkdir(parents=True, exist_ok=False)

    print(f"[run] loading misraj...")
    samples = load_misraj()
    selected = samples[: args.limit]  # loader natural stable order (sorted by id)

    print(f"[run] loading {args.engine} (GPU)...")
    t0 = time.perf_counter()
    engine = DoclingEngine()
    engine.load()
    load_time_s = time.perf_counter() - t0
    assert engine.accelerator_device == "cuda", "GPU-first policy violated"

    warmup_id = selected[0].sample_id
    w0 = time.perf_counter()
    engine.run(selected[0].image_path)
    warmup_s = time.perf_counter() - w0
    print(f"[run] warm-up done ({warmup_s:.1f}s)")

    per_sample: list[dict] = []
    retry_events: list[str] = []
    total_inference_s = 0.0

    for index, sample in enumerate(selected):
        pred, elapsed_s, retries = _run_with_retry(engine, sample.image_path)
        total_inference_s += elapsed_s
        if retries:
            retry_events.append(sample.sample_id)

        # immediate verbatim persistence, before any metric touches anything
        (raw_dir / f"{sample.sample_id}.json").write_text(pred.raw_output, encoding="utf-8")

        reference_raw = sample.reference_text or ""
        hypothesis_raw = pred.text if pred.ok else ""
        entry: dict = {
            "sample_id": sample.sample_id,
            "ok": pred.ok,
            "elapsed_s": round(elapsed_s, 3),
            "retries": retries,
        }
        if not pred.ok:
            entry["error"] = pred.error

        if reference_raw.strip():
            entry.update(_scores(reference_raw, hypothesis_raw))
        else:
            entry["empty_reference"] = True

        per_sample.append(entry)
        print(
            f"[run {index + 1}/{len(selected)}] {sample.sample_id}: "
            f"ok={pred.ok} cer_norm={entry.get('normalized', {}).get('cer', 'n/a')}"
        )

    scorable = [e for e in per_sample if e.get("ok") and not e.get("empty_reference")]
    empty_reference_count = sum(1 for e in per_sample if e.get("empty_reference"))
    failed = [e for e in per_sample if not e["ok"]]

    def pairs(key: str) -> list[tuple[str, str]]:
        return [(e["text"][f"reference_{key}"], e["text"][f"hypothesis_{key}"]) for e in scorable]

    raw_pairs, norm_pairs = pairs("raw"), pairs("normalized")
    metrics = {
        "run_timestamp": timestamp,
        "dataset": "misraj",
        "engine": args.engine,
        "model_version": engine.model_version,
        "accelerator_device": engine.accelerator_device,
        "sample_count": len(selected),
        "selected_sample_ids": [s.sample_id for s in selected],
        "successful_samples": sum(1 for e in per_sample if e["ok"]),
        "failed_samples": len(failed),
        "failure_rate": len(failed) / len(per_sample),
        "empty_reference_count": empty_reference_count,
        "load_time_s": round(load_time_s, 2),
        "warmup": {"sample_id": warmup_id, "elapsed_s": round(warmup_s, 2)},
        "timing_summary": {
            "total_inference_s": round(total_inference_s, 2),
            "mean_per_sample_s": round(total_inference_s / len(selected), 3),
            "max_per_sample_s": round(max(e["elapsed_s"] for e in per_sample), 3),
        },
        "retry_events": retry_events,
        "normalization_version": NORMALIZATION_VERSION,
        "normalization_notes": NORMALIZATION_NOTES,
        "per_sample": per_sample,
        "micro": {
            "cer_raw": micro_cer(raw_pairs),
            "wer_raw": micro_wer(raw_pairs),
            "cer_normalized": micro_cer(norm_pairs),
            "wer_normalized": micro_wer(norm_pairs),
        },
        "macro": {
            "cer_raw": macro_cer(raw_pairs),
            "wer_raw": macro_wer(raw_pairs),
            "cer_normalized": macro_cer(norm_pairs),
            "wer_normalized": macro_wer(norm_pairs),
        },
    }
    (run_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    config = {
        "run_timestamp": timestamp,
        "dataset": {"name": "misraj", "sample_count_total": len(samples)},
        "selection": f"loader natural order (sorted by sample_id), first {args.limit}",
        "selected_sample_ids": [s.sample_id for s in selected],
        "engine": {
            "name": args.engine,
            "model_version": engine.model_version,
            "accelerator_device": engine.accelerator_device,
            "input_formats_accepted": sorted(SUPPORTED_SUFFIXES),
        },
        "gpu": gpu,
        "runner": {
            "sequential": True,
            "warmup": True,
            "retry_policy": "attempt 1 -> single retry on failure -> final",
            "max_retries": 1,
        },
        "input_transformation": "none — native PNG page cache materialized by the loader",
        "normalization": {
            "version": NORMALIZATION_VERSION,
            "notes": NORMALIZATION_NOTES,
        },
    }
    (run_dir / "config.yaml").write_text(
        yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    status = (
        "PASS"
        if len(per_sample) == len(selected)
        and metrics["successful_samples"] + len(failed) == len(selected)
        else "PARTIAL"
    )
    run_log = "\n".join([
        "# Misraj × Docling Pilot Run Log",
        "",
        f"- run: {args.engine}/misraj/{timestamp}",
        f"- timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"- environment: Python {platform.python_version()}, {platform.system()} "
        f"{platform.release()}",
        f"- GPU: {gpu['device']} | driver {gpu['driver']} | torch {gpu['torch']} "
        f"(cuda {gpu['cuda_build']})",
        f"- engine/model: docling {engine.model_version} | accelerator: "
        f"{engine.accelerator_device}",
        f"- load time: {load_time_s:.1f}s | warm-up: {warmup_s:.1f}s ({warmup_id}, "
        "excluded from timing)",
        f"- samples: {len(selected)} attempted | successes {metrics['successful_samples']}"
        f" | failures {len(failed)} | retries {len(retry_events)}"
        + (f" ({', '.join(retry_events)})" if retry_events else ""),
        f"- timing: total {total_inference_s:.1f}s, mean "
        f"{total_inference_s / len(selected):.2f}s/sample",
        f"- normalization: {NORMALIZATION_VERSION}",
        f"- empty references excluded: {empty_reference_count}",
        "",
        "## Notes",
        "",
        "- Pilot validates the pipeline only; NOT a scientific estimate of the "
        "400-page result.",
        "- Raw Docling JSON persisted verbatim per sample before scoring.",
        "",
        f"## Final pilot status: **{status}**",
        "",
    ])
    (run_dir / "run_log.md").write_text(run_log, encoding="utf-8")

    micro = metrics["micro"]
    macro = metrics["macro"]
    print(
        f"\n[run] micro CER raw={micro['cer_raw']:.4f} norm={micro['cer_normalized']:.4f} | "
        f"WER raw={micro['wer_raw']:.4f} norm={micro['wer_normalized']:.4f}"
    )
    print(
        f"[run] macro CER raw={macro['cer_raw']:.4f} norm={macro['cer_normalized']:.4f} | "
        f"WER raw={macro['wer_raw']:.4f} norm={macro['wer_normalized']:.4f}"
    )
    print(f"[run] results: {run_dir}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
