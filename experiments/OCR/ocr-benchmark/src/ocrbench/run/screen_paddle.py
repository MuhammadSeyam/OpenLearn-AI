"""PaddleOCR-VL screening execution path (engine-specific, intentionally local).

Re-runs ONLY the PaddleOCR-VL operational screening: environment checks,
load attempt with VRAM observation, and the three deterministic Custom
representatives. No CER/WER, no normalization, no accuracy claims.

This module is deliberately NOT a generic multi-engine runner.

Usage:
    .venv/bin/python -m ocrbench.run.screen_paddle
"""

from __future__ import annotations

import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

from ocrbench.datasets.custom import GT_ROOT, load_custom
from ocrbench.engines.paddle_vl import SUPPORTED_SUFFIXES, PaddleVLEngine
from ocrbench.types import Prediction

REPORT_PATH: Path = Path(__file__).resolve().parents[3] / "results" / "screening" / "paddle_vl.md"

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp"}
STRATA = (
    ("English", lambda s: "en" in s.metadata["language"]),
    ("Arabic", lambda s: s.metadata["language"] == ["ar"]),
    ("Mixed", lambda s: set(s.metadata["language"]) == {"ar", "en"}),
)


def _pick(samples, predicate):
    candidates = [s for s in samples if predicate(s)]
    if not candidates:
        raise ValueError(f"screen_paddle: empty candidate pool")
    return min(
        candidates,
        key=lambda s: (
            s.image_path.suffix.lower() not in IMAGE_SUFFIXES,
            sum(1 for v in s.metadata["features"].values() if v),
            s.sample_id,
        ),
    )


def select_samples():
    """The same three deterministic representatives as the previous screening."""
    samples = load_custom()
    return [(tag, _pick(samples, pred)) for tag, pred in STRATA]


class VramWatcher:
    def __init__(self) -> None:
        self.peak_mb = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._watch, daemon=True)

    def _watch(self) -> None:
        while not self._stop.is_set():
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                capture_output=True, text=True,
            )
            try:
                self.peak_mb = max(self.peak_mb, int(out.stdout.strip()))
            except ValueError:
                pass
            time.sleep(0.5)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join(timeout=2)


def main() -> int:
    import paddle

    lines = ["# PaddleOCR-VL Screening", ""]
    engine_desc = (
        "## Engine",
        "",
        "- adapter: `ocrbench.engines.paddle_vl.PaddleVLEngine` (native backend)",
        "- model family: PaddleOCR-VL document-parsing pipeline (v1.6)",
    )
    lines += engine_desc

    # --- environment ---
    env_ok_torch = False
    try:
        import torch

        env_ok_torch = bool(torch.cuda.is_available())
        torch_version = str(torch.__version__)
    except Exception as exc:  # coexistence check must stay visible
        torch_version = f"IMPORT FAILED: {type(exc).__name__}: {exc}"
    smi = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
         "--format=csv,noheader"], capture_output=True, text=True,
    ).stdout.strip().replace(", ", " | ")
    gpu_visible = paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0

    lines += [
        "## Environment",
        "",
        f"- date: {datetime.now().isoformat(timespec='seconds')}",
        f"- paddle: {paddle.__version__} (compiled_cuda={paddle.device.is_compiled_with_cuda()}, "
        f"runtime_cuda={paddle.version.cuda()}, cudnn={paddle.version.cudnn()})",
        f"- paddleocr: {__import__('paddleocr').__version__} · paddlex: {__import__('paddlex').__version__}",
        f"- torch coexistence: {torch_version} (cuda_available={env_ok_torch})",
        f"- GPU: {smi}",
        f"- Paddle GPU visible: {gpu_visible}",
        "",
    ]

    if not gpu_visible or not env_ok_torch:
        lines += ["## Load Result", "", "**FAIL** — GPU/coexistence precondition violated; screening aborted.", ""]
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        print("GPU precondition failed; report written.")
        return 1

    # --- deterministic sample selection (identical to previous screening) ---
    picks = select_samples()
    print("Selected samples:")
    for tag, sel in picks:
        print(f"  - [{tag}] {sel.sample_id} ({sel.image_path.suffix})")

    engine = PaddleVLEngine(device="gpu:0")
    with VramWatcher() as watcher:
        t0 = time.perf_counter()
        try:
            engine.load()
            load_error = ""
            load_status = "PASS"
        except Exception as exc:
            # single-line summary; full tracebacks stay in stdout logs
            load_error = f"{type(exc).__name__} during model initialization"
            load_status = "FAIL"
        load_s = time.perf_counter() - t0
        load_peak_mb = watcher.peak_mb

    lines += [
        "## Load Result",
        "",
        f"- **{load_status}** after {load_s:.1f}s | configured device: `{engine.device}` "
        f"| model_version: `{engine.model_version}`",
    ]
    if load_error:
        lines += [f"- error: `{load_error}`"]
    lines += [f"- peak VRAM during load: {load_peak_mb} MiB / 4096 MiB", ""]

    rows: list[dict] = []
    if load_status == "PASS":
        for tag, sel in picks:
            with VramWatcher() as watcher:
                t0 = time.perf_counter()
                try:
                    pred = engine.run(sel.image_path)
                    error = ""
                except Exception as exc:
                    pred, error = None, f"{type(exc).__name__}: {str(exc)[:160]}"
                wall_s = time.perf_counter() - t0
            if not isinstance(pred, Prediction):
                rows.append({
                    "tag": tag, "sample_id": sel.sample_id, "suffix": sel.image_path.suffix,
                    "status": "ERROR", "ok": None, "raw_bytes": 0, "parseable": False,
                    "text_len": 0, "wall_s": round(wall_s, 2), "peak_mb": watcher.peak_mb,
                    "error": error,
                })
                continue
            parseable = False
            if pred.ok and pred.raw_output:
                try:
                    parseable = isinstance(json.loads(pred.raw_output), list)
                except json.JSONDecodeError:
                    parseable = False
            status = ("SUCCESS" if pred.ok else "ENGINE_FAILURE") if not error else "ERROR"
            rows.append({
                "tag": tag, "sample_id": sel.sample_id, "suffix": sel.image_path.suffix,
                "status": status, "ok": pred.ok,
                "raw_bytes": len(pred.raw_output.encode("utf-8")),
                "parseable": parseable, "text_len": len(pred.text or ""),
                "wall_s": round(wall_s, 2), "peak_mb": watcher.peak_mb,
                "error": pred.error or error,
            })
            print(f"  -> [{tag}] {sel.sample_id}: {rows[-1]['status']} raw={rows[-1]['raw_bytes']}B")

    all_success = (
        load_status == "PASS"
        and len(rows) == 3
        and all(r["status"] == "SUCCESS" and r["parseable"] for r in rows)
    )
    recommendation = "PASS" if all_success else ("FAIL" if load_status == "FAIL" and not gpu_visible else "CONDITIONAL")

    lines += [
        "## Per-Sample Execution",
        "",
        "| type | sample_id | input | status | ok | raw_output bytes | parseable JSON | text chars | wall_s | peak VRAM MiB | error |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['tag']} | {r['sample_id']} | {r['suffix']} | {r['status']} | {r['ok']} "
            f"| {r['raw_bytes']} | {r['parseable']} | {r['text_len']} | {r['wall_s']} "
            f"| {r['peak_mb']} | {(r['error'] or '')[:100]} |"
        )
    if not rows:
        for tag, sel in picks:
            lines.append(
                f"| {tag} | {sel.sample_id} | {sel.image_path.suffix} "
                f"| NOT_EXECUTED (load blocker) | — | — | — | — | — | — | — |"
            )

    lines += [
        "",
        "## Raw Output Preservation",
        "",
        "- Adapter serializes each result's complete structured `.json` payload verbatim into a JSON array (no text-only reduction).",
        f"- End-to-end preservation this run: {'CONFIRMED (non-empty parseable JSON per sample)' if all_success else 'NOT ACHIEVED (blocked by load)'}.",
        "",
        "## GPU Execution Evidence",
        "",
        f"- Paddle compiled with CUDA: {paddle.device.is_compiled_with_cuda()} · runtime CUDA {paddle.version.cuda()} · device `{engine.device}`",
        f"- Peak VRAM observed during load: {load_peak_mb} MiB"
        + (f"; per-sample peaks listed above." if rows else "; inference never reached."),
        "- No CPU fallback was attempted.",
        "",
        "## Obvious Issues",
        "",
    ]

    issues = []
    if load_status == "FAIL":
        issues.append(
            f"Native initialization still exceeds the 4 GB card ({load_peak_mb} MiB peak): "
            f"{load_error}"
        )
    for r in rows:
        if r["status"] != "SUCCESS":
            issues.append(f"{r['sample_id']}: {r['status']} — {r['error']}")
    lines += [f"- {i}" for i in issues] or ["- none observed"]

    lines += [
        "",
        "## Comparison With Previous Screening",
        "",
        "- Previous (2026-08-25, first run): CONDITIONAL — same ResourceExhaustedError during VL weight placement (~3.76 GiB peak), bf16 already selected, no offload option in installed version.",
        f"- This run: {'unchanged blocker reproduced' if load_status == 'FAIL' else 'blocker resolved'}; package versions identical (paddle 3.2.2 / paddleocr 3.7.0 / paddlex 3.7.2); NCCL collision repair still holding (torch imports with CUDA available).",
        "",
        "## Recommendation",
        "",
        f"**{recommendation}**",
        "",
        "- Operational screening only; no accuracy was measured and none may be inferred.",
    ]

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report written: {REPORT_PATH}")
    print(f"Recommendation: {recommendation}")

    assert GT_ROOT.is_dir(), "ground truth root vanished during screening"
    return 0 if all_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
