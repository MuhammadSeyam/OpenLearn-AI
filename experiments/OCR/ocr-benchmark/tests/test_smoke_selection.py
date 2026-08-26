"""Smoke-test selection + adapter-contract tests (no engine execution here)."""

from __future__ import annotations

import json

import pytest

from ocrbench.datasets.custom import CUSTOM_ROOT, load_custom
from ocrbench.engines.docling import SUPPORTED_SUFFIXES, DoclingEngine
from ocrbench.run.smoke import require_cuda, select_smoke_samples


def _manifest_ids() -> set[str]:
    manifest = json.loads((CUSTOM_ROOT / "manifest.json").read_text(encoding="utf-8"))
    return {d["sample_id"] for d in manifest["documents"]}


def test_exactly_three_unique_manifest_backed_samples():
    picks = select_smoke_samples()
    assert len(picks) == 3
    ids = [p.sample_id for p in picks]
    assert len(set(ids)) == 3
    assert set(ids) <= _manifest_ids()


def test_selection_is_deterministic():
    a = [p.sample_id for p in select_smoke_samples()]
    b = [p.sample_id for p in select_smoke_samples()]
    assert a == b


def test_strata_coverage():
    by_id = {s.sample_id: s for s in load_custom()}
    en_bd, ar, mixed = select_smoke_samples()

    assert "english_born_digital" in by_id[en_bd.sample_id].categories
    assert by_id[ar.sample_id].metadata["language"] == ["ar"]
    assert set(by_id[mixed.sample_id].metadata["language"]) == {"ar", "en"}
    assert all("deterministic pick" in p.rationale for p in select_smoke_samples())


def test_pdf_inputs_are_accepted_by_the_adapter_contract():
    """PDFs must reach Docling directly; the adapter may not reject them."""
    assert ".pdf" in SUPPORTED_SUFFIXES


def test_adapter_rejects_genuinely_unknown_types_only():
    """Non-PDF/image inputs are still rejected loudly; PDFs pass the gate."""
    from pathlib import Path

    engine = DoclingEngine()
    assert engine.model_version == "not-loaded"
    assert ".pdf" in SUPPORTED_SUFFIXES
    with pytest.raises(ValueError, match="unsupported input type"):
        engine.run(Path("pyproject.toml"))


def test_gpu_guard_blocks_silent_cpu_fallback():
    with pytest.raises(SystemExit, match="GPU-first"):
        require_cuda(False)
    require_cuda(True)  # no-op when CUDA present
