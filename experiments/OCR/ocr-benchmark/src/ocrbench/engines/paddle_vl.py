"""PaddleOCR-VL adapter.

Wraps the official ``paddleocr.PaddleOCRVL`` pipeline (native backend).
Heavy imports happen only inside load()/run(); importing this module does
not require Paddle to be initialized.

Raw-output policy: every prediction object's structured ``json`` payload is
collected and serialized verbatim to one JSON array — parsing_res_list,
layout_det_res, model_settings, page dimensions: everything the engine
emitted, losslessly. Mechanical text extraction follows the OBSERVED T4
contract (PaddleOCRVLResult → .json → res → parsing_res_list →
block_content/block_bbox/block_label/block_order) with markdown/rec_texts
kept as higher-precedence legacy shapes, and raises loudly if none matches;
it never fabricates content.

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
        self.accelerator_device: str = "not-loaded"
        self.device: str = device
        self._pipeline: object | None = None

    def load(self) -> None:
        """Initialize the PaddleOCR-VL pipeline once per instance."""
        if self._pipeline is not None:
            return

        import paddle  # lazy heavy import

        from paddleocr import PaddleOCRVL  # lazy heavy import

        # GPU-first contract: the runner asserts accelerator_device == "cuda".
        # A CPU-only paddle build or absent device fails loudly here instead of
        # silently degrading benchmark execution.
        if not (paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0):
            raise RuntimeError(
                "paddle_vl: Paddle CUDA runtime unavailable — "
                f"compiled_with_cuda={paddle.device.is_compiled_with_cuda()}, "
                f"device_count={paddle.device.cuda.device_count()}"
            )
        self.accelerator_device = "cuda"

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
        """Mechanical plain-text extraction against the observed PaddleOCR-VL
        contract, in fixed precedence order:

        A. ``res.markdown.texts`` (str)            — if a future version emits it
        B. ``res.rec_texts`` (list)                — OCR-style results
        C. ``res.parsing_res_list`` (list)         — OBSERVED T4 payload:
              block_content joined in reading order; numeric ``block_order``
              first (ascending), then blocks with ``block_order=None`` (e.g.
              page numbers) deterministically by ``block_id``. Contents are
              preserved exactly as emitted — normalization is the metric layer's job.

        A recognized-but-empty structure yields "" (ok=True). A payload with
        none of these fields is an incompatible shape and fails loudly.
        """
        for payload in payloads:
            res = payload.get("res", payload)
            if not isinstance(res, dict):
                continue
            markdown = res.get("markdown")
            if isinstance(markdown, dict) and isinstance(markdown.get("texts"), str):
                return markdown["texts"]
            if isinstance(markdown, str):
                return markdown
            rec_texts = res.get("rec_texts")
            if isinstance(rec_texts, list):
                return "\n".join(str(t) for t in rec_texts)
            blocks = res.get("parsing_res_list")
            if isinstance(blocks, list):
                return "\n".join(PaddleVLEngine._ordered_block_texts(blocks))
        if payloads:
            raise RuntimeError(
                "paddle_vl: unrecognized result shape — no markdown.texts / "
                "rec_texts / parsing_res_list found; incompatible installed "
                "PaddleOCR version"
            )
        return ""

    @staticmethod
    def _ordered_block_texts(blocks: list) -> list[str]:
        """block_content values in deterministic reading order from parsing_res_list."""
        entries = []
        for index, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            content = block.get("block_content")
            if not isinstance(content, str) or not content:
                continue
            order = block.get("block_order")
            block_id = block.get("block_id")
            has_order = isinstance(order, (int, float)) and not isinstance(order, bool)
            id_key = block_id if isinstance(block_id, (int, float)) and not isinstance(block_id, bool) else 10**9
            # ordered blocks first by block_order, unordered after by block_id;
            # original index keeps the sort total and stable for degenerate ties
            key = (0 if has_order else 1,
                   order if has_order else 0,
                   id_key,
                   index)
            entries.append((key, content))
        entries.sort(key=lambda entry: entry[0])
        return [content for _, content in entries]

    @staticmethod
    def _extract_regions(payload: dict) -> list | None:
        """Regions only when the engine naturally emits them.

        Primary source is the observed ``parsing_res_list`` (block_bbox /
        block_label / block_content); the legacy rec_polys/rec_texts pair
        remains as a fallback for OCR-style results. Polygon points exist in
        the payload but the project Region schema has no polygon field, so
        they are intentionally not represented.
        """
        res = payload.get("res", payload)
        if not isinstance(res, dict):
            return None

        blocks = res.get("parsing_res_list")
        if isinstance(blocks, list):
            from ocrbench.types import Region

            regions = []
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                bbox = block.get("block_bbox")
                content = block.get("block_content")
                if not isinstance(bbox, list) or len(bbox) != 4:
                    continue
                if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in bbox):
                    continue
                if not isinstance(content, str) or not content:
                    continue
                regions.append(
                    Region(
                        box=(float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])),
                        type=str(block.get("block_label", "text")),
                        text=content,
                    )
                )
            # recognized layout output → return even when empty ([] ≠ N/A)
            return regions

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
