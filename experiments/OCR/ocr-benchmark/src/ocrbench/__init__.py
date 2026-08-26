"""ocrbench — OpenLearn AI OCR benchmark package.

Foundation stage: filesystem paths (paths.py) and shared dataclasses
(types.py). Dataset loaders, the engine boundary, metrics, and runners are
added in later stages as separate vertical slices.

Standing rules:
- Engine-specific code stays in engine modules; shared evaluation logic
  never imports engine code.
- Prediction.raw_output preserves engine output verbatim; normalization
  happens only in the metric layer.
- Failures are benchmark data and must remain visible, not disappear.
"""
