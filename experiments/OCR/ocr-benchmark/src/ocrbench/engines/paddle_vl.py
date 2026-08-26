"""PaddleOCR-VL adapter.

Wraps the official ``paddleocr.PaddleOCRVL`` pipeline (native backend).
Heavy imports happen only inside load()/run(); importing this module does
not require Paddle to be initialized.

Raw-output policy: every prediction object's structured ``json`` payload is
collected and serialized verbatim to one JSON array — recognized text,
layout blocks, confidences, everything the engine emitted. Mechanical text
extraction probes the documented paddlex result shapes and raises loudly if
none matches; it never fabricates content.

Known constraint (screening 2026-08-25): native in-process loading of the
0.9B VL weights requires more VRAM than a 4 GB card provides
(ResourceExhaustedError at ~3.8 GB peak); see results/screening/paddle_vl.md.
"""

from __future__ import annotations

import json
from pathlib import Path

from ocrbench.types import Prediction

SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".pdf"}
DEFAULT_PIPELINE_VERSION = "v1.6"


class PaddleVLEngine:
    """Adapter wrapping the PaddleOCR-VL document-parsing pipeline."""

    def __init__(self, device: str = "gpu:0") -> None:
        self.name: str = "paddle_vl"
        self.model_version: str = "not-loaded"
        self.device: str = device
        self._pipeline: object | None = None

    def load(self) -> None:
        """Initialize the PaddleOCR-VL pipeline once per instance."""
        if self._pipeline is not None:
            return

        from paddleocr import PaddleOCRVL  # lazy heavy import

        self._pipeline = PaddleOCRVL(device=self.device)
        version = DEFAULT_PIPELINE_VERSION
        try:
            version = self._pipeline.config.pipeline_version  # type: ignore[attr-defined]
        except AttributeError:
            pass
        self.model_version = f"PaddleOCR-VL-{version}"

    def run(self, image_path: Path) -> Prediction:
        if not isinstance(image_path, Path):
            raise TypeError(f"paddle_vl: expected Path, got {type(image_path)!r}")
        if not image_path.exists():
            raise FileNotFoundError(f"paddle_vl: input does not exist: {image_path}")
        if not image_path.is_file():
            raise ValueError(f"paddle_vl: input is not a file: {image_path}")
        if image_path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(
                f"paddle_vl: unsupported input type {image_path.suffix!r} "
                f"(supported: {sorted(SUPPORTED_SUFFIXES)})"
            )
        if self._pipeline is None:
            raise RuntimeError("paddle_vl: run() called before load()")

        sample_id = image_path.stem
        try:
            results = list(self._pipeline.predict(str(image_path)))
            payloads = [self._result_json(r) for r in results]
            raw_output = json.dumps(payloads, ensure_ascii=False, default=str)

            first = payloads[0] if payloads else {}
            return Prediction(
                sample_id=sample_id,
                ok=True,
                text=self._extract_text(payloads),
                raw_output=raw_output,
                regions=self._extract_regions(first),
            )
        except Exception as exc:  # per-input engine failure → recorded, not raised
            return Prediction(
                sample_id=sample_id,
                ok=False,
                text=None,
                raw_output="",
                error=f"{type(exc).__name__}: {exc}",
            )

    @staticmethod
    def _result_json(result) -> dict:
        """Complete structured payload of one prediction result."""
        payload = getattr(result, "json", None)
        if callable(payload):
            payload = payload()
        if isinstance(payload, dict):
            return payload
        raise RuntimeError(
            "paddle_vl: result has no serializable .json payload; "
            "refusing to invent a reduced raw output"
        )

    @staticmethod
    def _extract_text(payloads: list[dict]) -> str | None:
        """Mechanical plain-text extraction; probes documented result shapes."""
        for payload in payloads:
            res = payload.get("res", payload)
            markdown = res.get("markdown")
            if isinstance(markdown, dict) and isinstance(markdown.get("texts"), str):
                return markdown["texts"]
            if isinstance(markdown, str):
                return markdown
            rec_texts = res.get("rec_texts")
            if isinstance(rec_texts, list):
                return "\n".join(str(t) for t in rec_texts)
        if payloads:
            raise RuntimeError(
                "paddle_vl: unrecognized result shape — no markdown/rec_texts "
                "field found; incompatible installed PaddleOCR version"
            )
        return ""

    @staticmethod
    def _extract_regions(payload: dict) -> list | None:
        """Region boxes only when the engine naturally emits them."""
        res = payload.get("res", payload)
        polys = res.get("rec_polys")
        texts = res.get("rec_texts")
        if not polys or texts is None or len(polys) != len(texts):
            return None
        from ocrbench.types import Region

        regions = []
        for poly, text in zip(polys, texts):
            xs = [float(p[0]) for p in poly]
            ys = [float(p[1]) for p in poly]
            regions.append(
                Region(box=(min(xs), min(ys), max(xs), max(ys)), type="text", text=str(text))
            )
        return regions
