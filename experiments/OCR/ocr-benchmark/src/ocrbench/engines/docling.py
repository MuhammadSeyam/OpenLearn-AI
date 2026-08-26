"""Docling adapter.

Satisfies the Engine protocol via lazy imports: importing this module (and
even instantiating DoclingEngine) does NOT require or initialize Docling;
heavy imports happen inside load() / run().

Raw-output policy
-----------------
Prediction.raw_output carries the complete DoclingDocument serialized to JSON
(pydantic ``model_dump_json``). This retains the full structured engine result
(text cells, tables, layout provenance) verbatim, not just convenience text
exports. If serialization is impossible on the installed version, the adapter
raises loudly instead of fabricating a reduced "raw" output.

Failure policy
--------------
- Engine-invocation failures on a single input are benchmark data:
  ok=False + error, never raised, never retried.
- Everything outside the invocation path (missing/invalid input path,
  missing/incompatible Docling API surface) is an environment or programming
  error and propagates loudly.
"""

from __future__ import annotations

import json
from pathlib import Path

from ocrbench.types import Prediction

SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".pdf"}


class DoclingEngine:
    """Adapter wrapping Docling's DocumentConverter.

    PDFs are passed to Docling directly (native ingestion); the adapter never
    renders or rewrites them. The accelerator is configured explicitly
    (CUDA when available) and recorded on ``accelerator_device`` so callers
    can verify what was actually requested.
    """

    def __init__(self) -> None:
        self.name: str = "docling"
        self.model_version: str = "not-loaded"
        self.accelerator_device: str = "not-loaded"
        self._converter: object | None = None

    def load(self) -> None:
        """Initialize DocumentConverter once per instance."""
        if self._converter is not None:
            return

        import torch  # lazy heavy import (engine dependency, not core)

        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import (
            AcceleratorOptions,
            PdfPipelineOptions,
        )
        from docling.document_converter import (
            DocumentConverter,
            ImageFormatOption,
            PdfFormatOption,
        )

        self.accelerator_device = "cuda" if torch.cuda.is_available() else "cpu"
        accelerator = AcceleratorOptions(num_threads=4, device=self.accelerator_device)
        pdf_options = PdfPipelineOptions()
        pdf_options.accelerator_options = accelerator

        # Images share StandardPdfPipeline in this Docling version, so the same
        # pipeline options govern both input kinds.
        self._converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=pdf_options),
            }
        )

        import docling  # local: version probe only

        self.model_version = str(getattr(docling, "__version__", "unknown"))

    def run(self, image_path: Path) -> Prediction:
        if not isinstance(image_path, Path):
            raise TypeError(f"docling: expected Path, got {type(image_path)!r}")
        if not image_path.exists():
            raise FileNotFoundError(f"docling: input does not exist: {image_path}")
        if not image_path.is_file():
            raise ValueError(f"docling: input is not a file: {image_path}")
        if image_path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(
                f"docling: unsupported input type {image_path.suffix!r} "
                f"(supported: {sorted(SUPPORTED_SUFFIXES)})"
            )
        if self._converter is None:
            raise RuntimeError("docling: run() called before load()")

        sample_id = image_path.stem
        try:
            result = self._converter.convert(str(image_path))
            document = self._require(result, "document")
            status_name = getattr(getattr(result, "status", None), "name", "UNKNOWN")
            ok = status_name == "SUCCESS"

            raw_output = self._serialize(document)
            return Prediction(
                sample_id=sample_id,
                ok=ok,
                text=self._extract_text(document),
                raw_output=raw_output,
                error=None if ok else f"conversion status: {status_name}",
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
    def _require(obj: object, attr: str):
        value = getattr(obj, attr, None)
        if value is None:
            raise RuntimeError(
                f"docling: unexpected result shape — missing .{attr}; "
                f"incompatible installed Docling version"
            )
        return value

    @staticmethod
    def _serialize(document) -> str:
        """Complete structured result as stable JSON text."""
        dump_json = getattr(document, "model_dump_json", None)
        if callable(dump_json):
            return str(dump_json())
        export_dict = getattr(document, "export_to_dict", None)
        if callable(export_dict):
            return json.dumps(export_dict(), default=str)
        raise RuntimeError(
            "docling: cannot serialize document (no model_dump_json / "
            "export_to_dict); refusing to invent a reduced raw output"
        )

    @staticmethod
    def _extract_text(document) -> str | None:
        """Mechanical plain-text extraction only — no normalization."""
        for exporter in ("export_to_text", "export_to_markdown"):
            fn = getattr(document, exporter, None)
            if callable(fn):
                return str(fn())
        raise RuntimeError(
            "docling: no text exporter found on document; incompatible version"
        )
