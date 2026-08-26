"""Focused contract tests for the PaddleOCR-VL adapter (no model loading)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ocrbench.engines.base import Engine
from ocrbench.engines.paddle_vl import PaddleVLEngine
from ocrbench.types import Prediction


def test_import_does_not_initialize_paddle():
    import sys

    from ocrbench.engines import paddle_vl  # noqa: F401

    assert not any(m.startswith("paddle") for m in sys.modules), "heavy module leaked at import"


def test_protocol_conformance_and_lazy_state():
    engine = PaddleVLEngine()
    assert isinstance(engine, Engine)
    assert engine.name == "paddle_vl"
    assert engine.model_version == "not-loaded"
    assert engine.accelerator_device == "not-loaded"
    assert engine.device == "gpu:0"
    assert engine._pipeline is None


def test_metadata_shape_and_accepted_inputs():
    engine = PaddleVLEngine()
    from ocrbench.engines.paddle_vl import SUPPORTED_SUFFIXES

    assert {".png", ".jpg", ".jpeg", ".pdf"} <= SUPPORTED_SUFFIXES
    # version string is only finalized after a successful load()
    assert engine.model_version == "not-loaded"


def test_accelerator_device_lifecycle_not_loaded_before_load():
    """The runner asserts accelerator_device == 'cuda' after load(); before
    load() it must be the explicit sentinel (no silent defaults)."""
    engine = PaddleVLEngine(device="gpu:0")
    assert engine.accelerator_device == "not-loaded"
    # load() itself needs the real paddle runtime + model weights and is
    # covered by the T4 integration path, not unit tests.


def test_run_before_load_fails_loudly(tmp_path):
    image = tmp_path / "page.png"
    image.write_bytes(b"\x89PNG fake")
    with pytest.raises(RuntimeError, match="before load"):
        PaddleVLEngine().run(image)


def test_invalid_inputs_propagate(tmp_path):
    engine = PaddleVLEngine()
    with pytest.raises(FileNotFoundError):
        engine.run(tmp_path / "missing.png")
    directory = tmp_path / "dir.png"
    directory.mkdir()
    with pytest.raises(ValueError, match="not a file"):
        engine.run(directory)
    doc = tmp_path / "notes.xyz"
    doc.write_text("x")
    with pytest.raises(ValueError, match="unsupported input type"):
        engine.run(doc)


class FakeResult:
    """Minimal stand-in for paddlex result objects (.json property)."""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class StubPipeline:
    """Bypasses load(); returns the canned prediction object."""

    def __init__(self, result):
        self._result = result

    def predict(self, path):
        return iter([self._result])


def test_raw_output_serialization_is_verbatim_structured(tmp_path):
    engine = PaddleVLEngine()
    payload = {"res": {"markdown": {"texts": "hello"}, "rec_texts": ["hello"]}}
    engine._pipeline = StubPipeline(FakeResult(payload))
    image = tmp_path / "page.png"
    image.write_bytes(b"\x89PNG fake")
    pred = engine.run(image)
    assert isinstance(pred, Prediction) and pred.ok
    assert pred.sample_id == "page"
    restored = json.loads(pred.raw_output)
    assert restored == [payload]  # complete structure preserved, nothing reduced
    assert pred.text == "hello"


def test_extraction_raises_on_unrecognized_shape(tmp_path):
    engine = PaddleVLEngine()
    engine._pipeline = StubPipeline(FakeResult({"unexpected": True}))
    image = tmp_path / "page.png"
    image.write_bytes(b"\x89PNG fake")
    pred = engine.run(image)
    assert not pred.ok
    assert "unrecognized result shape" in (pred.error or "")


def test_regions_only_when_naturally_available():
    assert PaddleVLEngine._extract_regions({"res": {}}) is None
    regions = PaddleVLEngine._extract_regions(
        {"res": {"rec_polys": [[[0, 0], [10, 0], [10, 5], [0, 5]]], "rec_texts": ["hi"]}}
    )
    assert regions is not None and len(regions) == 1
    assert regions[0].box == (0.0, 0.0, 10.0, 5.0)
    assert regions[0].text == "hi"


def test_regions_none_when_geometry_and_text_lengths_disagree():
    payload = {"res": {"rec_polys": [[[0, 0], [1, 0], [1, 1], [0, 1]]], "rec_texts": ["a", "b"]}}
    assert PaddleVLEngine._extract_regions(payload) is None


class TestTextExtractionPrecedence:
    """Extraction order is fixed and documented in the adapter docstring:
    markdown.texts → rec_texts → loud failure. Never invented fields."""

    def test_prefers_markdown_texts(self, tmp_path):
        engine = PaddleVLEngine()
        engine._pipeline = StubPipeline(
            FakeResult({"res": {"markdown": {"texts": "# Title\ntext"}, "rec_texts": ["ignored"]}})
        )
        image = tmp_path / "page.png"
        image.write_bytes(b"\x89PNG fake")
        pred = engine.run(image)
        assert pred.text == "# Title\ntext"

    def test_falls_back_to_rec_texts_in_native_order(self, tmp_path):
        engine = PaddleVLEngine()
        engine._pipeline = StubPipeline(
            FakeResult({"res": {"rec_texts": ["first", "second", "third"]}})
        )
        image = tmp_path / "page.png"
        image.write_bytes(b"\x89PNG fake")
        pred = engine.run(image)
        assert pred.ok
        assert pred.text == "first\nsecond\nthird"

    def test_recognized_but_blank_output_yields_empty_text(self, tmp_path):
        engine = PaddleVLEngine()
        engine._pipeline = StubPipeline(FakeResult({"res": {"markdown": {"texts": ""}}}))
        image = tmp_path / "page.png"
        image.write_bytes(b"\x89PNG fake")
        pred = engine.run(image)
        assert pred.ok and pred.text == ""

    def test_unrecognized_shape_fails_loudly_even_if_empty(self, tmp_path):
        # An empty/unrecognizable payload must NOT silently become CER=1.0 data;
        # it signals version drift and has to surface as an explicit failure.
        engine = PaddleVLEngine()
        engine._pipeline = StubPipeline(FakeResult({}))
        image = tmp_path / "page.png"
        image.write_bytes(b"\x89PNG fake")
        pred = engine.run(image)
        assert not pred.ok
        assert "unrecognized result shape" in (pred.error or "")

    def test_failure_prediction_for_input_level_engine_error(self, tmp_path):
        class BrokenPipeline:
            def predict(self, path):
                raise ValueError("boom")

        engine = PaddleVLEngine()
        engine._pipeline = BrokenPipeline()
        image = tmp_path / "page.png"
        image.write_bytes(b"\x89PNG fake")
        pred = engine.run(image)
        assert not pred.ok
        assert pred.raw_output == "" and pred.text is None
        assert "boom" in (pred.error or "")
