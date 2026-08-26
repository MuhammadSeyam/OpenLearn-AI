"""Engine boundary — the benchmark's single intentional abstraction.

A structural protocol: any object with these attributes/methods is a valid
engine. No ABC, no base class, no lifecycle framework.

Contract semantics:
- load(): initialize heavy engine components once per instance; never runs
  benchmark samples.
- run(image_path): process exactly one input file and return one Prediction.
  The adapter preserves raw output verbatim and performs mechanical text
  extraction only — normalization and metrics belong to the metric layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from ocrbench.types import Prediction


@runtime_checkable
class Engine(Protocol):
    """Structural engine contract (isinstance checks methods/attrs only)."""

    name: str
    model_version: str

    def load(self) -> None:
        """Initialize the engine (models, pipelines). Idempotent per instance."""
        ...

    def run(self, image_path: Path) -> Prediction:
        """Process one input file into a Prediction."""
        ...
